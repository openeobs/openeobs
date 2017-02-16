# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`gcs.py` defines the Glasgow Coma Scale observation class and its
standard behaviour and policy triggers based on this worldwide standard.
"""
import bisect
import logging

from openerp import models, fields, osv, SUPERUSER_ID
from openerp.addons.nh_observations import fields as obs_fields

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_gcs(models.Model):
    """
    Represents an Glasgow Coma Scale
    :class:`observation<observations.nh_clinical_patient_observation>`
    which stores three parameters that are used as a way to communicate
    about the level of consciousness of
    :class:`patients<base.nh_clinical_patient>` with acute brain injury.

    The basis of the scale system are the following parameters:
    Eye response: spontaneous, to sound, to pressure, none.
    Verbal response: orientated, confused, words, sounds, none.
    Motor response: obey commands, localising, normal flexion, abnormal
    flexion, extension, none.
    """
    _name = 'nh.clinical.patient.observation.gcs'
    _inherit = ['nh.clinical.patient.observation_scored']

    # Also decides the order fields are displayed in the mobile view.
    _required = ['eyes', 'verbal', 'motor']
    _scored = ['eyes', 'verbal', 'motor']
    _description = "GCS Observation"
    _eyes_selection = [
        ('SP', 'Spontaneous'),
        ('TS', 'To Sound'),
        ('TP', 'To Pressure'),
        ('NN', 'None'),
        ('NT', 'Not Testable')
    ]
    _verbal_selection = [
        ('OR', 'Orientated'),
        ('CO', 'Confused'),
        ('WO', 'Words'),
        ('SO', 'Sounds'),
        ('NN', 'None'),
        ('NT', 'Not Testable')
    ]
    _motor_selection = [
        ('OC', 'Obey Commands'),
        ('LO', 'Localising'),
        ('NF', 'Normal Flexion'),
        ('AF', 'Abnormal Flexion'),
        ('EX', 'Extension'),
        ('NN', 'None'),
        ('NT', 'Not Testable')
    ]

    """
    Default GCS policy has 5 different scenarios:
        case 0: 30 min frequency
        case 1: 1 hour frequency
        case 2: 2 hour frequency
        case 3: 4 hour frequency
        case 4: 12 hour frequency (no clinical risk)
    """
    _POLICY = {'ranges': [5, 9, 13, 14],
               'case': '01234',
               'frequencies': [30, 60, 120, 240, 720],
               'notifications': [[], [], [], [], []]}

    eyes = obs_fields.Selection(_eyes_selection, 'Eyes Open', required=True)
    verbal = obs_fields.Selection(_verbal_selection, 'Best Verbal Response',
                                  required=True)
    motor = obs_fields.Selection(_motor_selection, 'Best Motor Response',
                                 required=True)

    # TODO For some reason if you do not re-declare these as Odoo's field type,
    # type() will return nh_observation's Selection field type instead...
    # This strange behaviour breaks nh_clinical_form_description.to_dict()
    frequency = fields.Selection(default=60)
    partial_reason = fields.Selection()

    def calculate_score(self, record, return_dictionary=True):
        is_dict = type(record) is dict
        obs_data_dict = {
            'eyes': record['eyes'] if is_dict else record.eyes,
            'verbal': record['verbal'] if is_dict else record.verbal,
            'motor': record['motor'] if is_dict else record.motor
        }
        return super(nh_clinical_patient_observation_gcs, self)\
            .calculate_score(obs_data_dict,
                             return_dictionary=return_dictionary)

    def complete(self, cr, uid, activity_id, context=None):
        """
        It determines which acuity case the current observation is in
        with the stored data and responds to the different policy
        triggers accordingly defined on the ``_POLICY`` dictionary.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(
            self._POLICY['ranges'], activity.data_ref.score)])
        hcagroup_ids = groups_pool.search(
            cr, uid, [('users', 'in', [uid]),
                      ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(
            cr, uid, [('users', 'in', [uid]),
                      ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False

        # TRIGGER NOTIFICATIONS
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._POLICY['notifications'][case],
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)

        return super(nh_clinical_patient_observation_gcs, self).complete(
            cr, uid, activity_id, context)

    def create_activity(self, cr, uid, vals_activity=None, vals_data=None,
                        context=None):
        """
        When creating a new activity of this type, an exception will be
        raised if the :class:`spell<base.nh_clinical_spell>` already has
        an open GCS.

        :returns: :class:`activity<activity.nh_activity>` id.
        :rtype: int
        """
        if not vals_activity:
            vals_activity = {}
        if not vals_data:
            vals_data = {}
        assert vals_data.get('patient_id'), "patient_id is a required field!"
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id', '=', vals_data['patient_id']],
                  ['data_model', '=', self._name],
                  ['state', 'in', ['new', 'started', 'scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain)
        if len(ids):
            raise osv.except_osv("GCS Create Error!",
                                 "Having more than one activity of type '%s' "
                                 "is restricted. Terminate activities with "
                                 "ids=%s first" % (self._name, str(ids)))
        return super(
            nh_clinical_patient_observation_gcs, self).create_activity(
            cr, uid, vals_activity, vals_data, context)
