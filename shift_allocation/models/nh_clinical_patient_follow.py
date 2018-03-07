# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp import SUPERUSER_ID


class NhClinicalPatientFollow(orm.Model):
    """
    Represents the action to invite another user to follow a group
    of :mod:`patients<base.nh_clinical_patient>` adding visibility
    for those patients even when the invited user does not have a
    responsibility towards them.
    """
    _name = 'nh.clinical.patient.follow'
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_ids': fields.many2many(
            'nh.clinical.patient', 'follow_patient_rel', 'follow_id',
            'patient_id', 'Patients to Follow', required=True)
    }

    def complete(self, cr, uid, activity_id, context=None):
        """
        Calls :meth:`complete<activity.nh_activity.complete>` and then
        updates the ``following_ids`` list for the assigned
        :mod:`user<base.res_users>`.

        It will also call
        :meth:`update activity<activity.nh_activity.update_activity>`
        for all not ``completed`` or ``cancelled`` activities related to
        the list of patients.

        :returns: ``True``
        :rtype: bool
        """
        super(NhClinicalPatientFollow, self).complete(
            cr, uid, activity_id, context)
        activity_pool = self.pool['nh.activity']
        user_pool = self.pool['res.users']
        follow_activity = activity_pool.browse(cr, uid, activity_id,
                                               context=context)

        following_ids = []
        for patient in follow_activity.data_ref.patient_ids:
            following_ids.append([4, patient.id])

        if not follow_activity.user_id:
            raise osv.except_osv(
                'Error!',
                'Cannot complete follow activity without an assigned user to '
                'follow the patients')

        res = user_pool.write(
            cr, SUPERUSER_ID, follow_activity.user_id.id,
            {'following_ids': following_ids}, context=context)

        patient_ids = [
            patient.id for patient in follow_activity.data_ref.patient_ids
        ]
        update_activity_ids = activity_pool.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)
        for activity_id in update_activity_ids:
            activity_pool.update_activity(cr, SUPERUSER_ID, activity_id,
                                          context=context)
        return res
