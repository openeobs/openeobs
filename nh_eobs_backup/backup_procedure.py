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
    _name = 'nh.clinical.patient.observation'
    _inherit = 'nh.clinical.patient.observation'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(NHClinicalObservationCompleteOverride, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, context=context)
        spell_pool.write(cr, uid, spell_id, {'report_printed': False})
        return res