from openerp.exceptions import AccessError
from openerp.exceptions import except_orm
from openerp.osv import orm
from openerp.osv import fields
from openerp.osv import osv
from openerp import api
import logging
import base64
import os
import errno

_logger = logging.getLogger(__name__)


class NHClinicalObservationReportPrinting(orm.Model):
    """
    Add functionality for printing report and saving it to database and/or
    file system
    """
    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def add_report_to_database(
            self, cr, uid, report_name,
            report_datas, report_filename, report_model, report_id,
            context=None
    ):
        """
        Add the report to the database as an ir.attachment. The report PDF
        will be transformed into base64 before saving it.

        :param cr: Odoo cursor
        :param uid: User ID
        :param report_name: Name for the attachment
        :param report_datas: Base64 version of the Report
        :param report_filename: Filename for the report
        :param report_model: Odoo model the report is for
        :param report_id: ID of the report
        :return: ID from saving to database
        """
        attachment_id = None
        attachment = {
            'name': report_name,
            'datas': base64.encodestring(report_datas),
            'datas_fname': report_filename,
            'res_model': report_model,
            'res_id': report_id,
        }
        try:
            attachment_id = self.pool['ir.attachment'].create(
                cr, uid, attachment, context=context)
            _logger.info(
                'The PDF document %s is now saved in the database',
                attachment['name']
            )
        except AccessError:
            _logger.warning(
                'Cannot save PDF report %r as attachment',
                attachment['name']
            )

        return attachment_id

    def add_report_to_backup_location(
            self, backup_location_path, report_data, report_filename):
        """
        Save the report to the file system.

        :param backup_location_path: Location to save the report in the
            file system
        :param report_data: PDF data to save to file
        :param report_filename: Name of the file to save
        :return: True
        """
        if not os.path.exists(backup_location_path):
            try:
                os.makedirs(backup_location_path)
                _logger.info(
                    'Generating backup directory - {0}'.format(
                        backup_location_path
                    )
                )
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(
                        backup_location_path):
                    pass
                else:
                    return False
        path = '{backup_location_path}/{report_filename}.pdf'.format(
            backup_location_path=backup_location_path,
            report_filename=report_filename
        )
        with open(path, 'wb') as file:
            file.write(report_data)
            _logger.info('Report file written to {0}'.format(path))
        return True

    @api.model
    def print_report(self, spell_id=None):
        """
        'Print' the report by getting the PDF data for the rendered Report
        HTML. This is then saved to the database and the filesystem

        This method is called via a ir.cron entry which prints the reports that
        need printing every 10 minutes.

        :param spell_id: ID of the spell to print. If no spell ID is passed
            a list of spells that need printing will be collected and each one
            printed
        :return: True
        """
        # Get spell ids for reports to be printed
        spell_pool = self.pool['nh.clinical.spell']
        loc_pool = self.pool['nh.clinical.location']
        spell_ids = []

        if spell_id:
            spell_ids.append(spell_id)
        else:
            loc_ids = loc_pool.search(
                self._cr, self._uid,
                [
                    ['usage', '=', 'ward'],
                    ['backup_observations', '=', True]
                ]
            )
            spell_ids = spell_pool.search(
                self._cr, self._uid,
                [
                    ['report_printed', '=', False],
                    ['state', 'not in', ['completed', 'cancelled']],
                    ['location_id', 'child_of', loc_ids]
                ]
            )

        # For each report; print it, save it to DB, save it to FS,
        # set flag to True
        report_pool = self.pool['report']
        obs_report_pool = self.pool['report.nh.clinical.observation_report']
        for spell in spell_ids:
            obs_report_wizard_pool = \
                self.pool['nh.clinical.observation_report_wizard']
            obs_report_wizard_id = obs_report_wizard_pool.create(
                self._cr, self._uid, {
                    'start_time': None,
                    'end_time': None
                }
            )
            data = obs_report_wizard_pool.read(
                self._cr, self._uid, obs_report_wizard_id)
            data['spell_id'] = spell
            data['ews_only'] = True

            # Render the HTML for the report
            report_html = obs_report_pool.render_html(self._cr, self._uid,
                                                      obs_report_wizard_id,
                                                      data=data,
                                                      context=self._context)

            # Create PDF from HTML
            try:
                report_pdf = report_pool.get_pdf(
                    self._cr, self._uid, [obs_report_wizard_id],
                    'nh.clinical.observation_report',
                    html=report_html,
                    data=data, context=self._context
                )

                # file name in ward_surname_nhsnumber format
                spell_obj = spell_pool.read(self._cr, self._uid, spell)
                patient_id = spell_obj['patient_id'][0]
                patient = self.pool['nh.clinical.patient'].read(
                    self._cr, self._uid,
                    patient_id,
                    [
                        'patient_identifier',
                        'current_location_id',
                        'family_name'
                    ]
                )
                nhs_number = None
                if 'patient_identifier' in patient \
                        and patient['patient_identifier']:
                    nhs_number = patient['patient_identifier']
                ward = None
                ward_id = None
                if 'current_location_id' in patient \
                        and patient['current_location_id']:
                    ward_id = patient['current_location_id'][0]
                if ward_id:
                    loc_pool = self.pool['nh.clinical.location']
                    ward_usage = loc_pool.read(
                        self._cr, self._uid,
                        ward_id,
                        ['usage', 'display_name']
                    )
                    if ward_usage['usage'] != 'ward':
                        ward_ward = loc_pool.get_closest_parent_id(
                            self._cr, self._uid, ward_id, 'ward')
                        if ward_ward:
                            ward = loc_pool.read(
                                self._cr, self._uid, ward_ward,
                                ['display_name']
                            )['display_name'].replace(' ', '')
                    else:
                        ward = ward_usage['display_name'].replace(' ', '')
                surname = None
                if 'family_name' in patient and patient['family_name']:
                    surname = patient['family_name']
                file_name = '{w}_{s}_{n}'.format(
                    w=ward,
                    s=surname,
                    n=nhs_number
                )
                # Save to database
                db = self.add_report_to_database(
                    'nh.clinical.observation_report',
                    report_pdf,
                    file_name,
                    'nh.clinical.observation_report_wizard',
                    obs_report_wizard_id)

                # Save to file system
                fs = self.add_report_to_backup_location('/bcp/out', report_pdf,
                                                        file_name)
                if db and fs:
                    self.pool['nh.clinical.spell'].write(
                        self._cr, self._uid, spell, {'report_printed': True})
            except except_orm:
                pass
        return True
