# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.exceptions import AccessError
from openerp.exceptions import except_orm
from openerp.osv import orm
from openerp.osv import fields
from openerp.osv import osv
import logging
import base64
import os
import errno

_logger = logging.getLogger(__name__)


class NHClinicalBackupSpellFlag(orm.Model):
    _name = 'nh.clinical.spell'
    _inherit = 'nh.clinical.spell'

    _columns = {
        'report_printed': fields.boolean('Has the report been printed?')
    }

    _defaults = {
        'report_printed': False
    }


class NHClinicalObservationCompleteOverride(orm.AbstractModel):
    _inherit = 'nh.clinical.patient.observation.ews'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(NHClinicalObservationCompleteOverride, self)\
            .complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, patient_id, context=context)
        spell_pool.write(cr, uid, spell_id, {'report_printed': False})
        return res


class NHClinicalObservationBackupSettings(osv.TransientModel):
    _inherit = 'base.config.settings'
    _name = 'base.config.settings'
    _columns = {
        'locations_to_print': fields.many2many(
            'nh.clinical.location',
            domain=[['usage', '=', 'ward']],
            string='Locations to print backup observation reports for'
        )
    }

    def set_locations(self, cr, uid, ids, context=None):
        loc_pool = self.pool.get('nh.clinical.location')
        record = self.browse(cr, uid, ids[0], context=context)
        loc_ids = [l.id for l in record.locations_to_print]
        locs = loc_pool.search(
            cr,
            uid,
            [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True],
                ['id', 'not in', loc_ids]
            ]
        )
        loc_pool.write(cr, uid, locs, {'backup_observations': False})
        return loc_pool.write(cr, uid, loc_ids, {'backup_observations': True})

    def get_default_all(self, cr, uid, ids, context=None):
        loc_pool = self.pool.get('nh.clinical.location')
        locs = loc_pool.search(
            cr, uid,
            [
                ['usage', '=', 'ward'],
                ['backup_observations', '=', True]
            ]
        )
        return dict(locations_to_print=locs)


class NHClinicalObservationBackupLocation(orm.Model):
    _inherit = 'nh.clinical.location'
    _name = 'nh.clinical.location'
    _columns = {
        'backup_observations': fields.boolean(
            'Backup observations for this location'
        )
    }

    _defaults = {
        'backup_observations': False
    }


class NHClinicalObservationReportPrinting(orm.Model):
    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def add_report_to_database(
            self, cr, uid, report_name,
            report_datas, report_filename, report_model, report_id
    ):
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
                cr, uid, attachment)
        except AccessError:
            _logger.warning(
                'Cannot save PDF report %r as attachment',
                attachment['name']
            )
        else:
            _logger.info(
                'The PDF document %s is now saved in the database',
                attachment['name']
            )
        return attachment_id

    def add_report_to_backup_location(
            self, backup_location_path, report_data, report_filename):
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

    def print_report(self, cr, uid, spell_id=None, context=None):
        # Get spell ids for reports to be printed
        spell_pool = self.pool['nh.clinical.spell']
        loc_pool = self.pool['nh.clinical.location']
        spell_ids = []

        if spell_id:
            spell_ids.append(spell_id)
        else:
            loc_ids = loc_pool.search(
                cr, uid,
                [
                    ['usage', '=', 'ward'],
                    ['backup_observations', '=', True]
                ]
            )
            spell_ids = spell_pool.search(
                cr, uid,
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
                cr, uid, {
                    'start_time': None,
                    'end_time': None
                }
            )
            data = obs_report_wizard_pool.read(cr, uid, obs_report_wizard_id)
            data['spell_id'] = spell
            data['ews_only'] = True

            # Render the HTML for the report
            report_html = obs_report_pool.render_html(cr, uid,
                                                      obs_report_wizard_id,
                                                      data=data,
                                                      context=context)

            # Create PDF from HTML
            try:
                report_pdf = report_pool.get_pdf(
                    cr, uid, [obs_report_wizard_id],
                    'nh.clinical.observation_report',
                    html=report_html,
                    data=data, context=context
                )

                # file name in ward_surname_nhsnumber format
                spell_obj = spell_pool.read(cr, uid, spell)
                patient_id = spell_obj['patient_id'][0]
                patient = self.pool['nh.clinical.patient'].read(
                    cr, uid,
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
                        cr, uid,
                        ward_id,
                        ['usage', 'display_name']
                    )
                    if ward_usage['usage'] != 'ward':
                        ward_ward = loc_pool.get_closest_parent_id(
                            cr, uid, ward_id, 'ward')
                        if ward_ward:
                            ward = loc_pool.read(
                                cr, uid, ward_ward,
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
                    cr, uid,
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
                        cr, uid, spell, {'report_printed': True})
            except except_orm:
                pass
        return True
