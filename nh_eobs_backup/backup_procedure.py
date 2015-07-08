__author__ = 'colinwren'
from openerp.osv import orm, fields

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
        res = super(NHClinicalObservationCompleteOverride, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, context=context)
        spell_pool.write(cr, uid, spell_id, {'report_printed': False})
        return res

class NHClinicalObservationReportPrinting(orm.Model):
    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def print_report(self, cr, uid, spell_id=None, context=None):
        # Get spell ids for reports to be printed
        spell_ids = []
        if spell_id:
            spell_ids.append(spell_id)
        else:
            spell_ids = self.pool['nh.clinical.spell'].search(cr, uid, [['report_printed', '=', False]])

        # For each report; print it, save it to DB, save it to FS, set flag to True
        report_pool = self.pool['report']
        obs_report_pool = self.pool['report.nh.clinical.observation_report']
        for spell in spell_ids:
            obs_report_wizard_pool = self.pool['nh.clinical.observation_report_wizard']
            obs_report_wizard_id = obs_report_wizard_pool.create(cr, uid, {'start_time': None, 'end_time': None})
            data = obs_report_wizard_pool.read(cr, uid, obs_report_wizard_id)
            data['spell_id'] = spell

            # Render the HTML for the report
            report_html = obs_report_pool.render_html(cr, uid,
                                                      obs_report_wizard_id,
                                                      data=data,
                                                      context=context)

            # Create PDF from HTML
            report_pdf = report_pool.get_pdf(cr, uid, [obs_report_wizard_id],
                                             'nh.clinical.observation_report',
                                             html=report_html,
                                             data=data, context=context)
        return True

