# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.nh_observations.parameters import frequencies
import logging
import copy
_logger = logging.getLogger(__name__)


class nh_clinical_notification(orm.AbstractModel):
    _name = 'nh.clinical.notification'
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
    }
    _form_description = []

    def get_form_description(self, cr, uid, patient_id, context=None):
        return self._form_description

    def is_cancellable(self, cr, uid, context=None):
        return False
    
    
class nh_clinical_notification_hca(orm.Model):
    _name = 'nh.clinical.notification.hca'
    _inherit = ['nh.clinical.notification']

class nh_clinical_notification_nurse(orm.Model):
    _name = 'nh.clinical.notification.nurse'
    _inherit = ['nh.clinical.notification']


class nh_clinical_notification_frequency(orm.Model):
    _name = 'nh.clinical.notification.frequency'
    _inherit = ['nh.clinical.notification']
    _description = 'Review Frequency'
    _columns = {
        'observation': fields.text('Observation Model', required=True),
        'frequency': fields.selection(frequencies, 'Frequency')
    }
    _notifications = [{'model': 'medical_team', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        review_frequency = activity_pool.browse(cr, uid, activity_id, context=context)
        domain = [
            ('patient_id', '=', review_frequency.data_ref.patient_id.id),
            ('data_model', '=', review_frequency.data_ref.observation),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_ids = activity_pool.search(cr, uid, domain, order='create_date desc, id desc', context=context)
        obs = activity_pool.browse(cr, uid, obs_ids[0], context=context)
        obs_pool = self.pool[review_frequency.data_ref.observation]
        obs_pool.write(cr, uid, obs.data_ref.id, {'frequency': review_frequency.data_ref.frequency}, context=context)
        trigger_notification = review_frequency.creator_id.data_ref._name == 'nh.clinical.notification.assessment' and \
                               review_frequency.creator_id.creator_id.data_ref._name == 'nh.clinical.patient.observation.ews' \
                               and review_frequency.creator_id.creator_id.data_ref.clinical_risk == 'Low'
        if trigger_notification:
            api_pool = self.pool['nh.clinical.api']
            api_pool.trigger_notifications(cr, uid, {
                'notifications': self._notifications,
                'parent_id': review_frequency.parent_id.id,
                'creator_id': activity_id,
                'patient_id': review_frequency.data_ref.patient_id.id,
                'model': review_frequency.data_ref.observation,
                'group': 'nurse'
            }, context=context)
        return super(nh_clinical_notification_frequency, self).complete(cr, uid, activity_id, context=context)

    _form_description = [
        {
            'name': 'frequency',
            'type': 'selection',
            'selection': frequencies,
            'label': 'Observation frequency',
            'initially_hidden': False,
            'on_change': [
                {
                    'fields': ['submitButton'],
                    'condition': [['frequency', '==', '']],
                    'action': 'disable'
                },
                {
                    'fields': ['submitButton'],
                    'condition': [['frequency', '!=', '']],
                    'action': 'enable'
                }
            ],
        }
    ]


class nh_clinical_notification_doctor_assessment(orm.Model):
    _name = 'nh.clinical.notification.doctor_assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assessment Required'