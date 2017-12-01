from openerp.exceptions import AccessError
from openerp.exceptions import except_orm
from openerp.osv import orm
from openerp import api
import logging
import base64
import os
import re

_logger = logging.getLogger(__name__)


class NHClinicalObservationReportPrinting(orm.Model):
    """
    Add functionality for printing report and saving it to database and/or
    file system
    """
    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    @api.model
    def add_report_to_database(
            self, report_name, report_datas, report_filename, report_model,
            report_id):
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
            attachment_id = self.env['ir.attachment'].create(attachment)
            _logger.info(
                'The PDF document %s is now saved in the database',
                report_name
            )
        except AccessError:
            _logger.warning(
                'Cannot save PDF report %r as attachment',
                report_name
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
        :return: True if successful, False if error due to issues creating
            backup directory
        :rtype: bool
        """
        if not os.path.exists(backup_location_path):
            try:
                os.makedirs(backup_location_path)
                _logger.info(
                    'Generating backup directory - {0}'.format(
                        backup_location_path
                    )
                )
            except OSError:
                return False
        path = '{backup_location_path}/{report_filename}.pdf'.format(
            backup_location_path=backup_location_path,
            report_filename=report_filename
        )
        with open(path, 'wb') as file:
            file.write(report_data)
            _logger.info('Report file written to {0}'.format(path))
        return True

    def get_spells(self, spell_id=None):
        """
        Get the spells that need printing

        :param spell_id: A spell ID or none
        :return: list of spell_ids to print
        """
        if spell_id:
            if isinstance(spell_id, list):
                return spell_id
            return [spell_id]
        else:
            spell_model = self.env['nh.clinical.spell']
            loc_model = self.env['nh.clinical.location']
            loc_ids = loc_model.search(
                [
                    ['usage', '=', 'ward'],
                    ['backup_observations', '=', True]
                ]
            )
            return spell_model.search(
                [
                    ['report_printed', '=', False],
                    ['state', 'not in', ['completed', 'cancelled']],
                    ['location_id', 'child_of', loc_ids.id]
                ]
            ).ids

    def get_report(self, spell_id=None):
        """
        Get the PDF data of the report for the supplied spell_id

        :param spell_id: ID of the spell to print
        :return: tuple of wizard ID and string representation of PDF file
        """
        if not spell_id:
            return False
        report_model = self.env['report']
        obs_report_model = self.env['report.nh.clinical.observation_report']
        obs_report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']
        obs_report_wizard_id = obs_report_wizard_model.create(
            {
                'start_time': None,
                'end_time': None
            }
        )
        data = obs_report_wizard_model.browse(
            obs_report_wizard_id.id
        )
        data.spell_id = spell_id
        data.ews_only = True
        report_html = obs_report_model.render_html(data)
        try:
            return (
                obs_report_wizard_id,
                report_model.get_pdf(
                    obs_report_wizard_id,
                    'nh.clinical.observation_report',
                    html=report_html,
                    data=data
                )
            )
        except except_orm:
            return False

    def get_filename(self, spell_id=None):
        """
        Get the filename to save the report under this follows the

        ward_patientSurname_hospitalNumber_spellId format

        :param spell_id: ID of the spell to get filename for
        :return: filename or False
        """
        if not spell_id:
            return False
        spell_model = self.env['nh.clinical.spell']
        spell_obj = spell_model.browse(spell_id)
        patient = spell_obj.patient_id
        nhs_number = None
        if patient.patient_identifier:
            nhs_number = patient.patient_identifier
        ward = None
        ward_id = None
        if patient.current_location_id:
            ward_id = patient.current_location_id
        if ward_id:
            if ward_id.usage != 'ward':
                location_model = self.env['nh.clinical.location']
                ward_ward = location_model.browse(
                    location_model.get_closest_parent_id(ward_id.id, 'ward')
                )
                ward = ward_ward.display_name.replace(' ', '')
            else:
                ward = ward_id.display_name.replace(' ', '')
        surname = re.sub(r'\W', '', patient['family_name'])
        return '{ward}_{surname}_{identifier}_{spell}'.format(
            ward=ward,
            surname=surname,
            identifier=nhs_number,
            spell=spell_id
        )

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
        spell_ids = self.get_spells(spell_id)
        for spell_id in spell_ids:
            report_pdf = self.get_report(spell_id)
            if not report_pdf:
                return False
            file_name = self.get_filename(spell_id)
            if not file_name:
                return False
            saved_to_db = self.add_report_to_database(
                'nh.clinical.observation_report',
                report_pdf,
                file_name,
                'nh.clinical.observation_report_wizard',
                report_pdf[0]
            )
            if not saved_to_db:
                return False
            saved_to_fs = self.add_report_to_backup_location(
                '/bcp/out',
                report_pdf[1],
                file_name
            )
            if not saved_to_fs:
                return False
            spell = self.env['nh.clinical.spell'].browse(spell_id)
            spell.write({'report_printed': True})
        return True
