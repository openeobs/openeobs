# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`pbp.py` defines the postural blood pressure observation class and its
standard behaviour and policy triggers.
"""
from openerp.osv import orm, fields
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_pbp(orm.Model):
    """
    Represents a Postural Blood Pressure
    :class:`observation<observations.nh_clinical_patient_observation>`
    for postural hypotension detection, storing the systolic and
    dyastolic blood pressure for both standing and sitting postures.
    """
    _name = 'nh.clinical.patient.observation.pbp'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['systolic_sitting', 'diastolic_sitting',
                 'systolic_standing', 'diastolic_standing']
    _description = "Postural Blood Pressure Observation"

    _POLICY = {'schedule': [[6, 0], [18, 0]], 'notifications': [
        [],
        [{'model': 'nurse', 'summary': 'Inform FY2',
          'groups': ['nurse', 'hca']},
         {'model': 'hca', 'summary': 'Inform registered nurse',
          'groups': ['hca']},
         {'model': 'nurse',
          'summary': 'Informed about patient status (Postural Blood Pressure)',
          'groups': ['hca']}]
    ]}

    def _get_pbp_result(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pbp in self.browse(cr, uid, ids, context=context):
            if int(pbp.systolic_sitting - pbp.systolic_standing) > 20:
                res[pbp.id] = 'yes'
            else:
                res[pbp.id] = 'no'
        return res

    _columns = {
        'systolic_sitting': fields.integer('Sitting Blood Pressure Systolic'),
        'systolic_standing': fields.integer(
            'Standing Blood Pressure Systolic'),
        'diastolic_sitting': fields.integer(
            'Sitting Blood Pressure Diastolic'),
        'diastolic_standing': fields.integer(
            'Standing Blood Pressure Diastolic'),
        'result': fields.function(_get_pbp_result, type='char',
                                  string='>20 mm/Hg', size=5, store=False)
    }

    _form_description = [
        {
            'name': 'systolic_sitting',
            'type': 'integer',
            'label': 'Sitting Blood Pressure Systolic',
            'min': 1,
            'max': 300,
            'on_change': [
                {
                    'fields': ['systolic_standing', 'diastolic_standing'],
                    'condition': [['systolic_sitting', '!=', ''],
                                  ['diastolic_sitting', '!=', '']],
                    'action': 'show'
                },
                {
                    'fields': ['systolic_standing', 'diastolic_standing'],
                    'condition': ['||', ['systolic_sitting', '==', ''],
                                  ['diastolic_sitting', '==', '']],
                    'action': 'hide'
                }
            ],
            'validation': [
                {
                    'condition': {
                        'target': 'systolic_sitting',
                        'operator': '>',
                        'value': 'diastolic_sitting'
                    },
                    'message': {
                        'target': 'Sitting Systolic BP must be more than '
                                  'Sitting Diastolic BP',
                        'value': 'Sitting Diastolic BP must be less than '
                                 'Sitting Systolic BP'
                    }
                }
            ],
            'initially_hidden': False
        },
        {
            'name': 'diastolic_sitting',
            'type': 'integer',
            'label': 'Sitting Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'on_change': [
                {
                    'fields': ['systolic_standing', 'diastolic_standing'],
                    'condition': [['systolic_sitting', '!=', ''],
                                  ['diastolic_sitting', '!=', '']],
                    'action': 'show'
                },
                {
                    'fields': ['systolic_standing', 'diastolic_standing'],
                    'condition': ['||', ['systolic_sitting', '==', ''],
                                  ['diastolic_sitting', '==', '']],
                    'action': 'hide'
                }
            ],
            'validation': [
                {
                    'condition': {
                        'target': 'diastolic_sitting',
                        'operator': '<',
                        'value': 'systolic_sitting'
                    },
                    'message': {
                        'target': 'Sitting Diastolic BP must be less than '
                                  'Sitting Systolic BP',
                        'value': 'Sitting Systolic BP must be more than '
                                 'Sitting Diastolic BP'
                    }
                }
            ],
            'initially_hidden': False
        },
        {
            'name': 'systolic_standing',
            'type': 'integer',
            'label': 'Standing Blood Pressure Systolic',
            'min': 1,
            'max': 300,
            'validation': [
                {
                    'condition': {
                        'target': 'systolic_standing',
                        'operator': '>',
                        'value': 'diastolic_standing'
                    },
                    'message': {
                        'target': 'Standing Systolic BP must be more than '
                                  'Standing Diastolic BP',
                        'value': 'Standing Diastolic BP must be less than '
                                 'Standing Systolic BP'
                    }
                }
            ],
            'initially_hidden': True
        },
        {
            'name': 'diastolic_standing',
            'type': 'integer',
            'label': 'Standing Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'validation': [
                {
                    'condition': {
                        'target': 'diastolic_standing',
                        'operator': '<',
                        'value': 'systolic_standing'
                    },
                    'message': {
                        'target': 'Standing Diastolic BP must be less than '
                                  'Standing Systolic BP',
                        'value': 'Standing Systolic BP must be more than '
                                 'Standing Diastolic BP'
                    }
                }
            ],
            'initially_hidden': True
        }
    ]

    def schedule(self, cr, uid, activity_id, date_scheduled=None,
                 context=None):
        """
        If a specific ``date_scheduled`` parameter is not specified.
        The `_POLICY['schedule']` dictionary value will be used to find
        the closest time to the current time from the ones specified
        (0 to 23 hours)

        Then it will call :meth:`schedule<activity.nh_activity.schedule>`

        :returns: ``True``
        :rtype: bool
        """
        hour = td(hours=1)
        schedule_times = []
        for s in self._POLICY['schedule']:
            schedule_times.append(
                dt.now().replace(
                    hour=s[0], minute=s[1], second=0, microsecond=0))
        date_schedule = date_scheduled if date_scheduled else dt.now().replace(
            minute=0, second=0, microsecond=0)
        utctimes = [fields.datetime.utc_timestamp(
            cr, uid, t, context=context) for t in schedule_times]
        while all([date_schedule.hour != date_schedule.strptime(
                ut, DTF).hour for ut in utctimes]):
            date_schedule += hour
        return super(nh_clinical_patient_observation_pbp, self).schedule(
            cr, uid, activity_id, date_schedule.strftime(DTF), context=context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        It determines which acuity case the current observation is in
        with the stored data and responds to the different policy
        triggers accordingly defined on the ``_POLICY`` dictionary.

        Calls :meth:`complete<activity.nh_activity.complete>` and then
        creates and schedules a new postural blood pressure observation
        if the current
        :mod:`pbp monitoring<parameters.nh_clinical_patient_pbp_monitoring>`
        parameter is ``True``.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(activity.data_ref.result == 'yes')
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

        res = super(nh_clinical_patient_observation_pbp, self).complete(
            cr, uid, activity_id, context)

        activity_pool.cancel_open_activities(
            cr, uid, activity.parent_id.id, self._name, context=context)

        # create next PBP (schedule)
        domain = [
            ['data_model', '=', 'nh.clinical.patient.pbp_monitoring'],
            ['state', '=', 'completed'],
            ['patient_id', '=', activity.data_ref.patient_id.id]
        ]
        pbp_monitoring_ids = activity_pool.search(
            cr, uid, domain, order="date_terminated desc, sequence desc",
            context=context)
        monitoring_active = pbp_monitoring_ids and activity_pool.browse(
            cr, uid, pbp_monitoring_ids[0], context=context).data_ref.status
        if monitoring_active:
            next_activity_id = self.create_activity(
                cr, SUPERUSER_ID,
                {'creator_id': activity_id,
                 'parent_id': activity.parent_id.id},
                {'patient_id': activity.data_ref.patient_id.id})

            date_schedule = dt.now().replace(
                minute=0, second=0, microsecond=0) + td(hours=2)
            activity_pool.schedule(
                cr, uid, next_activity_id, date_schedule, context=context)
        return res
