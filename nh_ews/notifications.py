# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`notifications.py` define notification types necessary for the Early
Warning Score policy triggers.
"""
from openerp.osv import orm
from openerp.addons.nh_observations import frequencies
import logging
import copy
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
        :class:`frequency<notifications.nh_clinical_notification_frequency>`
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
        return super(nh_clinical_notification_assessment, self).complete(
            cr, uid, activity_id, context=context)


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
        :class:`assessment<notifications.nh_clinical_notification_doctor_
        assessment>` by default.

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
        return super(nh_clinical_notification_medical_team, self).complete(
            cr, uid, activity_id, context=context)

    def is_cancellable(self, cr, uid, context=None):
        """
        This notification is cancellable by default.

        :returns: ``True``
        :rtype: bool
        """
        return True


class NHClinicalNotificationFrequency(orm.Model):
    """
    This notification addresses the specific need of an observation
    frequency that needs to be reviewed by the medical staff.
    """
    _name = 'nh.clinical.notification.frequency'
    _inherit = 'nh.clinical.notification.frequency'
    _description = 'Review Frequency'
    _notifications = [{'model': 'medical_team', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        res = super(NHClinicalNotificationFrequency, self).complete(
            cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        review_frequency = activity_pool.browse(
            cr, uid, activity_id, context=context)

        if hasattr(review_frequency, 'creator_id') and \
                review_frequency.creator_id:
            creator = review_frequency.creator_id

            if hasattr(creator, 'creator_id') and creator.creator_id:
                parent = creator.creator_id

                if hasattr(parent.data_ref, 'clinical_risk'):
                    clinical_risk = parent.data_ref.clinical_risk
                    creator_type = creator.data_ref._name
                    parent_type = parent.data_ref._name

                    # TODO Does this condition need to be here? Can we create notifications for all models?
                    if creator_type == 'nh.clinical.notification.assessment' \
                        and parent_type == 'nh.clinical.patient.observation' \
                            '.ews' and clinical_risk == 'Low':
                        api_pool = self.pool['nh.clinical.api']
                        api_pool.trigger_notifications(cr, uid, {
                            'notifications': self._notifications,
                            'parent_id': review_frequency.parent_id.id,
                            'creator_id': activity_id,
                            'patient_id':
                                review_frequency.data_ref.patient_id.id,
                            'model': review_frequency.data_ref.observation,
                            'group': 'nurse'
                        }, context=context)
        return res

    def get_form_description(self, cr, uid, patient_id, context=None):
        freq_list = copy.deepcopy(frequencies.as_list())
        form_desc = copy.deepcopy(self._form_description)
        activity_pool = self.pool['nh.activity']
        ews_ids = activity_pool.search(
            cr, uid,
            [
                ['patient_id', '=', patient_id],
                ['parent_id.state', '=', 'started'],
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['state', '=', 'scheduled']
            ], order='sequence desc', context=context)
        if ews_ids:
            get_current_freq = activity_pool.browse(cr, uid, ews_ids[0],
                                                    context=context)
            if get_current_freq and get_current_freq.data_ref:
                current_freq = get_current_freq.data_ref.frequency
                for freq_tuple in frequencies.as_list():
                    if freq_tuple[0] > current_freq:
                        freq_list.remove(freq_tuple)
        for field in form_desc:
            if field['name'] == 'frequency':
                field['selection'] = freq_list
        return form_desc
