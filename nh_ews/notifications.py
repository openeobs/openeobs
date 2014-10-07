# -*- coding: utf-8 -*-

from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)


class nh_clinical_notification_assessment(orm.Model):
    _name = 'nh.clinical.notification.assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assess Patient'
    _notifications = [{'model': 'frequency', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
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
    _name = 'nh.clinical.notification.medical_team'
    _inherit = ['nh.clinical.notification']
    _description = 'Inform Medical Team?'
    _notifications = [{'model': 'doctor_assessment', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
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
        return True