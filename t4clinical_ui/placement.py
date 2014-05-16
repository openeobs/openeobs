from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)

from openerp import tools


class t4_clinical_placement(orm.Model):
    _name = "t4.clinical.placement"
    _inherits = {'t4.activity': 'activity_id'}
    _description = "Placement View"
    _auto = False
    _table = "t4_clinical_placement"
    _columns = {
        'activity_id': fields.many2one('t4.activity', 'Activity'),
        'location_id': fields.many2one('t4.clinical.location', 'Ward'),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number')
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        activity.id as id,
                        activity.id as activity_id,
                        activity.location_id as location_id,
                        activity.patient_id as patient_id,
                        activity.pos_id as pos_id,
                        patient.other_identifier as hospital_number
                    from t4_activity activity
                    inner join t4_clinical_patient patient on activity.patient_id = patient.id
                    where activity.data_model = 't4.clinical.patient.placement' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def complete(self, cr, uid, ids, context=None):
        placement = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_patient_placement_complete')], context=context)
        if not model_data_ids:
            pass # view doesnt exist
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']

        return {
            'name': 'Complete Placement',
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.patient.placement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': placement.activity_id.data_ref.id,
            'target': 'new',
            'view_id': int(view_id),
            'context': context
        }