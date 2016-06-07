"""
`nh_clinical_extension.py` extends several NH Clinical classes to add
relevant observations related functionality.
"""
from openerp.osv import orm


class nh_clinical_patient(orm.Model):
    """
    Extends :class:`patient<base.nh_clinical_patient>`
    """
    _name = 'nh.clinical.patient'
    _inherit = 'nh.clinical.patient'

    def write(self, cr, uid, ids, vals, context=None):
        """
        Calls :meth:`write<openerp.models.Model.write>` and
        automatically updates the :class:`location<base.nh_clinical_location>`
        of every
        :mod:`observation<observations.nh_clinical_patient_observation>`
        and :mod:`notification<notifications.nh_clinical_notification>`
        related.

        :returns: ``True``
        :rtype: bool
        """
        res = super(nh_clinical_patient, self).write(cr, uid, ids, vals,
                                                     context=context)
        if 'current_location_id' in vals:
            activity_pool = self.pool['nh.activity']
            patient_ids = [ids] if not isinstance(ids, list) else ids
            obs_and_not_ids = activity_pool.search(
                cr, uid, [['patient_id', 'in', patient_ids],
                          ['state', 'not in', ['completed', 'cancelled']],
                          '|', ['data_model', 'ilike', '%observation%'],
                          ['data_model', 'ilike', '%notification%']])
            activity_pool.write(cr, uid, obs_and_not_ids,
                                {'location_id': vals['current_location_id']},
                                context=context)
        return res
