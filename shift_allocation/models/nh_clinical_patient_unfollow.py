# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp import SUPERUSER_ID


class NhClinicalPatientUnfollow(orm.Model):
    """
    Represents the action to remove followers from a group of
    :mod:`patients<base.nh_clinical_patient>` removing visibility
    for those patients unless the user has a responsibility towards
    them.
    """
    _name = 'nh.clinical.patient.unfollow'
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_ids': fields.many2many(
            'nh.clinical.patient', 'unfollow_patient_rel', 'follow_id',
            'patient_id', 'Patients to stop Following', required=True)
    }

    def complete(self, cr, uid, activity_id, context=None):
        """
        Calls :meth:`complete<activity.nh_activity.complete>` and then
        removes the ``follower_ids`` list for the selected patients.

        It will also :meth:`cancel<activity.nh_activity.cancel>`
        any number of open (not ``completed`` or ``cancelled``)
        :mod:`follow invitations<operations.nh_clinical_patient_follow>`
        that contain the selected patients.

        :returns: ``True``
        :rtype: bool
        """
        super(NhClinicalPatientUnfollow, self).complete(
            cr, uid, activity_id, context)
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        follow_pool = self.pool['nh.clinical.patient.follow']
        unfollow_activity = activity_pool.browse(cr, uid, activity_id,
                                                 context=context)
        patient_ids = [p.id for p in unfollow_activity.data_ref.patient_ids]
        res = patient_pool.write(cr, uid, patient_ids,
                                 {'follower_ids': [[5]]}, context=context)
        update_activity_ids = activity_pool.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)

        for activity_id in update_activity_ids:
            activity_pool.update_activity(cr, SUPERUSER_ID, activity_id,
                                          context=context)
        # CANCEL PATIENT FOLLOW ACTIVITIES THAT CONTAIN ANY OF THE
        # UNFOLLOWED PATIENTS
        follow_ids = []
        for patient_id in patient_ids:
            follow_ids += follow_pool.search(cr, uid, [
                ['activity_id.create_uid', '=', uid],
                ['patient_ids', 'in', [patient_id]],
                ['activity_id.state', 'not in', ['completed', 'cancelled']]
            ])
        follow_ids = list(set(follow_ids))
        follow_activity_ids = [
            f.activity_id.id for f in follow_pool.browse(
                cr, uid, follow_ids, context=context)
        ]
        for activity_id in follow_activity_ids:
            activity_pool.cancel(cr, uid, activity_id, context=context)
        return res
