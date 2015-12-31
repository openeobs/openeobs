# -*- coding: utf-8 -*-
"""
`notifications.py` define notification types necessary for the Early
Warning Score policy triggers.
"""
from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class nh_clinical_notification_assessment(orm.Model):
    """
    This notification addresses the specific need of the
    :class:`patient<base.nh_clinical_patient>` needing medical
    assessment.
    """
    _name = 'nh.clinical.notification.assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assess Patient'
    _notifications = [{'model': 'frequency', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        """
        :meth:`completes<activity.nh_activity.complete>` the activity
        and triggers a
        :class:`review frequency<notifications.nh_clinical_notification_frequency>`
        by default.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }, context=context)
        return super(nh_clinical_notification_assessment, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_notification_medical_team(orm.Model):
    """
    This notification addresses the specific need of the responsible
    medical team having to be informed about the current
    :class:`patient<base.nh_clinical_patient>` condition.
    """
    _name = 'nh.clinical.notification.medical_team'
    _inherit = ['nh.clinical.notification']
    _description = 'Inform Medical Team?'
    _notifications = [{'model': 'doctor_assessment', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        """
        :meth:`completes<activity.nh_activity.complete>` the activity
        and triggers a
        :class:`doctor assessment<notifications.nh_clinical_notification_doctor_assessment>`
        by default.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id._name,
            'group': 'nurse'
        }, context=context)
        return super(nh_clinical_notification_medical_team, self).complete(cr, uid, activity_id, context=context)

    def is_cancellable(self, cr, uid, context=None):
        """
        This notification is cancellable by default.

        :returns: ``True``
        :rtype: bool
        """
        return True
