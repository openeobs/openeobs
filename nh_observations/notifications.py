# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`notifications.py` defines a set of activity types to serve as
informative reminders for the users that some action needs to take
place. They usually don't represent an action themselves.
A complete notification means the notification was read and the action
it refers to was done.
The abstract definition of a notification from which all other
notifications inherit is also included here.
"""
import logging

from openerp import api, exceptions
from openerp.addons.nh_observations import frequencies
from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)


class nh_clinical_notification(orm.AbstractModel):
    """
    Abstract representation of what a clinical notification is. Contains
    common information that all notifications will have but does not
    represent any entity itself, so it basically acts as a template
    for every other notification.
    """
    _name = 'nh.clinical.notification'
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
    }
    _form_description = []

    def get_form_description(self, cr, uid, patient_id, context=None):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui when the notification is
        shown.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        return self._form_description

    def is_cancellable(self, cr, uid, context=None):
        """
        Notifications cannot be cancelled by the user by default.
        :returns: ``False``
        :rtype: bool
        """
        return False

    @api.multi
    def is_valid(self):
        """
        Check the validity of the notification (each subclass to supply rules)

        :return: Boolean representing if notification instance is valid
        :rtype: bool
        """
        return True


class nh_clinical_notification_hca(orm.Model):
    """
    Represents a generic notification meant to be addressed only for
    the `HCA` user group.
    """
    _name = 'nh.clinical.notification.hca'
    _inherit = ['nh.clinical.notification']


class nh_clinical_notification_nurse(orm.Model):
    """
    Represents a generic notification meant to be addressed only for
    the `Nurse` user group.
    """
    _name = 'nh.clinical.notification.nurse'
    _inherit = ['nh.clinical.notification']


class nh_clinical_notification_frequency(orm.Model):
    """
    This notification addresses the specific need of an observation
    frequency that needs to be reviewed by the medical staff.
    """
    _name = 'nh.clinical.notification.frequency'
    _inherit = ['nh.clinical.notification']
    _description = 'Review Frequency'
    _columns = {
        'observation': fields.text('Observation Model', required=True),
        'frequency': fields.selection(frequencies.as_list(), 'Frequency')
    }
    _notifications = []

    @api.constrains('observation')
    def _check_valid_observation_model_name(self):
        if 'nh.clinical.patient.observation' not in self.observation:
            raise exceptions.ValidationError(
                "Observation field assigned an invalid observation model name."
            )

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity_review_frequency = activity_pool.browse(
            cr, uid, activity_id, context=context
        )
        spell_activity_id = activity_review_frequency.spell_activity_id.id
        observation_model_name = activity_review_frequency.data_ref.observation
        domain = [
            ('spell_activity_id', '=', spell_activity_id),
            ('data_model', '=', observation_model_name),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_ids = activity_pool.search(
            cr, uid, domain, order='create_date desc, id desc',
            context=context
        )
        if not obs_ids:
            message = "Review frequency task tried to adjust the frequency " \
                      "of the currently open obs but no open obs were found."
            raise ValueError(message)
        obs = activity_pool.browse(cr, uid, obs_ids[0], context=context)
        obs_pool = self.pool[activity_review_frequency.data_ref.observation]
        obs_pool.write(
            cr, uid, obs.data_ref.id,
            {'frequency': activity_review_frequency.data_ref.frequency},
            context=context)
        return super(nh_clinical_notification_frequency, self).complete(
            cr, uid, activity_id, context=context)

    _form_description = [
        {
            'name': 'frequency',
            'type': 'selection',
            'selection': frequencies.as_list(),
            'label': 'Observation frequency',
            'initially_hidden': False,
            'on_change': [
                {
                    'fields': ['submitButton'],
                    'condition': [['frequency', '==', '']],
                    'action': 'disable',
                    'type': 'value'
                },
                {
                    'fields': ['submitButton'],
                    'condition': [['frequency', '!=', '']],
                    'action': 'enable',
                    'type': 'value'
                }
            ],
        }
    ]

    def set_form_description_frequencies(self, available_frequencies):
        """
        Sets frequencies that appear in the tasks dropdown in the GUI.

        :param available_frequencies: a list of integers
        :type available_frequencies: list
        :return:
        """
        frequency = [field for field in self._form_description if
                     field['name'] == 'frequency'][0]
        frequency['selection'] = available_frequencies


class nh_clinical_notification_doctor_assessment(orm.Model):
    """
    This notification addresses the specific need of a doctor
    assessment needs to take place.
    """
    _name = 'nh.clinical.notification.doctor_assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assessment Required'
