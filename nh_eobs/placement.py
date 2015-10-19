"""
Shows all :class:`patients<base.nh_clinical_patient>` pending
:class:`placement<operations.nh_clinical_patient_placement>` in a
:class:`bed location<base.nh_clinical_location>`.
"""
from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_placement(orm.Model):
    """
    Extends :class:`activity<activity.nh_activity>` to create
    placement activities, showing all
    :class:`placements<operations.nh_clinical_patient_placement>`
    activities still pending. i.e. not `completed` or `cancelled`. These
    will be :class:`patients<base.nh_clinical_patient>` waiting to be
    'placed' in a :class:`bed location<base.nh_clinical_location>`.
    """

    _name = "nh.clinical.placement"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Placement View"
    _auto = False
    _table = "nh_clinical_placement"
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'location_id': fields.many2one('nh.clinical.location', 'Ward'),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number')
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s cascade;
                create or replace view %s as (
                    select
                        activity.id as id,
                        activity.id as activity_id,
                        activity.location_id as location_id,
                        activity.patient_id as patient_id,
                        activity.pos_id as pos_id,
                        patient.other_identifier as hospital_number,
                        patient.patient_identifier as nhs_number
                    from nh_activity activity
                    inner join nh_clinical_patient patient on activity.patient_id = patient.id
                    where activity.data_model = 'nh.clinical.patient.placement' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def complete(self, cr, uid, ids, context=None):
        """
        Extends :meth:`complete()<activity.nh_activity.complete>` to
        place a :class:`patient<base.nh_clinical_patient>` in a bed
        :class:`location<base.nh_clinical_location>`.

        :param ids: ids of placement
        :type ids: list
        :returns: an action to present a form view of
            :class:`placement<operations.nh_clinical_patient>`
        :rtype: dict
        """

        placement = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_patient_placement_complete')], context=context)
        if not model_data_ids:
            pass # view doesnt exist
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']

        return {
            'name': 'Patient Placement',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.placement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': placement.activity_id.data_ref.id,
            'target': 'new',
            'view_id': int(view_id),
            'context': context
        }
