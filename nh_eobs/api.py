# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Defines the core methods for `Open eObs` in the taking of
:class:`patient<base.nh_clinical_patient>` observations.
"""
import logging
from datetime import datetime as dt, timedelta as td

from openerp import SUPERUSER_ID
from openerp.osv import orm, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class nh_eobs_api(orm.AbstractModel):
    """
    Defines attributes and methods used by `Open eObs` in the making of
    patient observations.

    ``_active_observations`` are the observation types supported by
    eObs.
    """

    # TODO How come this doesn't inherit nh.clinical.api?
    _name = 'nh.eobs.api'

    # 'type' is the suffix of an observation model name.
    # e.g. 'nh.clinical.patient.observation.ews'
    #
    # 'name' is the label that will appear in the UI when selecting the type of
    # observation to perform.
    _active_observations = [
        {
            'type': 'ews',
            'name': 'NEWS'
        },
        {
            'type': 'height',
            'name': 'Height'
        },
        {
            'type': 'weight',
            'name': 'Weight'
        },
        {
            'type': 'blood_product',
            'name': 'Blood Product'
        },
        {
            'type': 'blood_sugar',
            'name': 'Blood Sugar'
        },
        {
            'type': 'stools',
            'name': 'Bristol Stool Scale'
        },
        {
            'type': 'gcs',
            'name': 'Glasgow Coma Scale (GCS)'
        },
        {
            'type': 'pbp',
            'name': 'Postural Blood Pressure'
        }
    ]

    def _get_activity_type(self, cr, uid, activity_type, observation=False,
                           context=None):
        model_pool = self.pool['ir.model']
        domain = [['model', 'ilike', '%'+activity_type+'%']] \
            if not observation \
            else [['model', 'ilike', '%observation.'+activity_type+'%']]
        m_ids = model_pool.search(cr, uid, domain, context=context)
        if not m_ids:
            raise osv.except_osv('Error!', 'Activity type not found!')
        if len(m_ids) > 1:
            _logger.warn(
                'More than one activity type found with the specified '
                'string: %s' % activity_type)
        return model_pool.read(cr, uid, m_ids[0], ['model'])['model']

    def _check_activity_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(
                _('Error!'), 'Activity ID not found: %s' % activity_id)
        return True

    def check_activity_access(self, cr, uid, activity_id, context=None):
        """
        Verifies if an :class:`activity<activity.nh_activity>` is
        assigned to a :class:`user<base.res_users>`.

        :param uid: id of user to verify
        :type uid: int
        :param activity_id: id of activity to verify
        :type activity_id: int
        :returns: ``True`` if user is assigned. Otherwise ``False``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        domain = [('id', '=', activity_id), '|', ('user_ids', 'in', [uid]),
                  ('user_id', '=', uid)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            return False
        user_id = activity_pool.read(
            cr, uid, activity_id, ['user_id'], context=context)['user_id']
        if user_id and user_id[0] != uid:
            return False
        return True

    def _create_activity(self, cr, uid, data_model, vals_activity=None,
                         vals_data=None, context=None):
        model_pool = self.pool[data_model]
        activity_id = model_pool.create_activity(
            cr, uid, vals_activity, vals_data, context=context)
        _logger.debug("Activity created id=%s, data_model=%s\n vals_activity: "
                      "%s\n vals_data: %s" % (activity_id, data_model,
                                              vals_activity, vals_data))
        return activity_id

    def get_activities_for_spell(self, cr, uid, spell_id, activity_type,
                                 start_date=None, end_date=None, context=None):
        """
        Gets all :class:`activities<activity.nh_activity>` for a patient
        :class:`spell<spell.nh_clinical_spell>`.

        :param spell_id: id for the patient spell
        :type spell_id: int
        :param activity_type: type of activity [optional]
        :type activity_type: str
        :param start_date: retrieve activities only on or after this
            date. Must be provided if ``activity_type`` has also been
            given
        :type start_date: str
        :param end_date: retrieve activities only on or before this
            date. Must be provided if ``activity_type`` has also been
            given
        :type end_date: str
        :returns: list of dictionaries of activities, including all
            fields and values
        :rtype: list
        """

        spell_pool = self.pool['nh.clinical.spell']
        if not spell_pool.search(
                cr, uid, [['id', '=', spell_id]], context=context):
            raise osv.except_osv('Error!', 'Spell ID provided does not exist')
        spell = spell_pool.browse(cr, uid, spell_id, context=None)
        model_pool = self.pool[self._get_activity_type(
            cr, uid, activity_type, observation=True, context=context)] \
            if activity_type else self.pool['nh.activity']
        domain = [('activity_id.parent_id', '=', spell.activity_id.id),
                  ('patient_id', '=', spell.patient_id.id),
                  ('activity_id.state', '=', 'completed')] \
            if activity_type \
            else [('parent_id', '=', spell.activity_id.id),
                  ('patient_id', '=', spell.patient_id.id),
                  ('state', 'not in', ['completed', 'cancelled'])]
        if activity_type:
            if start_date:
                if not isinstance(start_date, dt):
                    raise osv.except_osv(
                        "Value Error!",
                        "Datetime object expected, %s received."
                        % type(start_date))
                domain.append(
                    ('date_terminated', '>=', start_date.strftime(DTF)))
            if end_date:
                if not isinstance(end_date, dt):
                    raise osv.except_osv(
                        "Value Error!", "Datetime object expected, %s "
                                        "received." % type(end_date))
                domain.append(
                    ('date_terminated', '<=', end_date.strftime(DTF)))
        ids = model_pool.search(cr, uid, domain, context=context)
        return model_pool.read(cr, uid, ids, [], context=context)

    def get_share_users(self, cr, uid, context=None):
        """
        Gets :class:`user<base.res_users>` information `name`, `id`
        and `number of patients responsible for`) of each user who
        is responsible for any location located in any of the wards
        the user calling the method is responsible for.

        :param uid: id of user calling method
        :type uid: int
        :returns: list of dictionaries containing values ``name``,
            ``id`` and ``patients`` for each user
        :rtype: list
        """

        result = []
        user_pool = self.pool['res.users']
        activity_pool = self.pool['nh.activity']
        location_pool = self.pool['nh.clinical.location']
        user = user_pool.browse(cr, SUPERUSER_ID, uid, context=context)
        groups = [g.name for g in user.groups_id]
        wards = list(set([location_pool.get_closest_parent_id(
            cr, uid, loc.id, 'ward', context=context
        ) if loc.usage != 'ward' else loc.id for loc in user.location_ids]))
        location_ids = []
        for ward_id in wards:
            location_ids += location_pool.search(
                cr, uid, [['id', 'child_of', ward_id]])
        share_groups = ['NH Clinical Shift Coordinator Group',
                        'NH Clinical Nurse Group', 'NH Clinical HCA Group']
        domain = [['id', '!=', uid],
                  ['groups_id.name', 'in',
                   list(set(groups).intersection(share_groups))],
                  ['location_ids', 'in', location_ids]]
        user_ids = user_pool.search(cr, uid, domain, context=context)
        for user_id in user_ids:
            user_data = user_pool.read(cr, SUPERUSER_ID, user_id, ['name'])
            patients_number = len(activity_pool.search(
                cr, uid, [
                    ['user_ids', 'in', user_id],
                    ['data_model', '=', 'nh.clinical.spell'],
                    ['state', 'not in', ['cancelled', 'completed']]],
                context=context))
            result.append({
                'name': user_data['name'],
                'id': user_id,
                'patients': patients_number
            })
        return result

    # # # # # # # #
    #  ACTIVITIES #
    # # # # # # # #

    def get_activities(self, cr, uid, ids, context=None):
        """
        Gets a list of :class:`activities<activity.nh_activity>`.

        :param ids: ids of the activities. An empty list returns all
            activities
        :type ids: list
        :returns: list of dictionaries containing activities. See source
            for specific attributes returned for each activity
        :rtype: list
        """
        settings_pool = self.pool['nh.clinical.settings']
        activity_period = settings_pool.get_setting(cr, uid, 'activity_period')
        activity_time = dt.now()+td(minutes=activity_period)

        domain = [('id', 'in', ids)] if ids else [
            ('state', 'not in', ['completed', 'cancelled']), '|',
            ('date_scheduled', '<=', activity_time.strftime(DTF)),
            ('date_deadline', '<=', activity_time.strftime(DTF)),
            ('user_ids', 'in', [uid]),
            '|', ('user_id', '=', False), ('user_id', '=', uid)
        ]
        return self.collect_activities(cr, uid, domain, context=context)

    def collect_activities(self, cr, uid, domain, context=None):
        """
        Get activities from the database for a given domain
        :param cr: odoo cursor
        :param uid: user to perform search as
        :param domain: domain to look for
        :param context: odoo context
        :returns: list of dictionaries containing activities. See source
            for specific attributes returned for each activity
        :rtype: list
        """
        activity_pool = self.pool['nh.activity']
        sql_pool = self.pool['nh.clinical.sql']
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activity_ids_sql = ','.join(map(str, activity_ids))
        sql = sql_pool.get_collect_activities_sql(activity_ids_sql)
        activity_values = []
        if activity_ids:
            cr.execute(sql)
            activity_values = cr.dictfetchall()
        return activity_values

    def get_assigned_activities(self, cr, uid, activity_type=None,
                                context=None):
        """
        Gets :class:`users<base.res_users>` open assigned
        :class:`activities<activity.nh_activity>` of the specified type
        (any by default).

        :param activity_type: type of activity [optional]
        :type activity_type: str [default is ``None``]
        :returns: list of dictionaries containing activities
        :rtype: list
        """

        activity_pool = self.pool['nh.activity']
        domain = [['state', 'not in', ['cancelled', 'completed']],
                  ['user_id', '=', uid]]
        if activity_type:
            domain.append(['data_model', '=', activity_type])
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activities = activity_pool.browse(
            cr, uid, activity_ids, context=context)

        res = []
        for activity in activities:
            if activity.data_model == 'nh.clinical.patient.follow':
                patient_ids = [
                    patient.id for patient in activity.data_ref.patient_ids]
                data = {
                    'id': activity.id,
                    'user': activity.create_uid.name,
                    'count': len(patient_ids),
                    'patient_ids': patient_ids
                }
                data['message'] = 'You have been invited to follow ' +\
                                  str(data['count']) + ' patients from ' +\
                                  data['user']
            else:
                data = {
                    'id': activity.id,
                    'message': 'You have a notification'
                }
            res.append(data)
        return res

    def cancel(self, cr, uid, activity_id, data, context=None):
        """
        Cancel an :class:`activity<activity.nh_activity>`, updating it
        with submitted ``data``.

        :param activity_id: id of activity to cancel
        :type activity_id: int
        :param data: data to update the activity
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        if not data:
            data = {}
        activity_pool = self.pool['nh.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        activity_pool.submit(cr, uid, activity_id, data, context=context)
        return activity_pool.cancel(cr, uid, activity_id, context=context)

    def submit(self, cr, uid, activity_id, data, context=None):
        """
        Updates submitted :class:`activity<activity.nh_activity>` data.

        :param activity_id: id of activity to update
        :type activity_id: int
        :param data: data to update activity
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        activity_pool = self.pool['nh.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        if not self.check_activity_access(
                cr, uid, activity_id, context=context):
            raise osv.except_osv(
                _('Error!'),
                'User ID %s not allowed to update this activity: %s'
                % (uid, activity_id))
        return activity_pool.submit(
            cr, uid, activity_id, data, context=context)

    def unassign(self, cr, uid, activity_id, context=None):
        """
        Unassign the :class:`activity<activity.nh_activity>` from the
        :class:`user<base.res_users>`.

        :param uid: id of the user
        :type uid: int
        :param activity_id: id of activity
        :type activity_id: int
        :returns: ``True``
        :rtype: bool
        """

        activity_pool = self.pool['nh.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        if not self.check_activity_access(
                cr, uid, activity_id, context=context):
            raise osv.except_osv(
                _('Error!'),
                'User ID %s not allowed to unassign this activity: %s'
                % (uid, activity_id))
        return activity_pool.unassign(cr, uid, activity_id, context=context)

    def unassign_my_activities(self, cr, uid, context=None):
        """
        Unassigns every :class:`activity<activity.nh_activity>` the
        :class:`user<base.res_users>` is assigned to.

        Not included are activities that are always belong to a specific
        user.

        :param uid: id user of user
        :type uid: int
        :returns: ``True``
        :rtype: bool
        """

        activity_pool = self.pool['nh.activity']
        domain = [['user_id', '=', uid],
                  ['data_model', 'not in',
                   ['nh.clinical.notification.hca',
                    'nh.clinical.patient.follow']],
                  ['state', 'not in', ['completed', 'cancelled']]]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        [self.unassign(cr, uid, aid, context=context) for aid in activity_ids]
        return True

    def assign(self, cr, uid, activity_id, data, context=None):
        """
        Assigns an :class:`activity<activity.nh_activity>` to a
        :class:`user<base.res_users>`. Raises an exception if the user
        is not permitted to assign the activity or if the user being
        assigned cannot be located.

        :param activity_id: id of activity
        :type activity_id: int
        :param data: may contain ``user_id``. The activity will be
            assigned to this user
        :type data: dict
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: ``True``
        :rtype: bool
        """

        if not data:
            data = {}
        activity_pool = self.pool['nh.activity']
        user_pool = self.pool['res.users']
        user_id = uid
        if not self.check_activity_access(
                cr, user_id, activity_id, context=context):
            raise osv.except_osv(
                _('Error!'),
                'User ID %s not allowed to assign this activity: %s'
                % (user_id, activity_id))
        self._check_activity_id(cr, uid, activity_id, context=context)
        if data.get('user_id'):
            user_id = data['user_id']
            domain = [('id', '=', user_id)]
            user_ids = user_pool.search(cr, uid, domain, context=context)
            if not user_ids:
                raise osv.except_osv(
                    _('Error!'), 'User ID not found: %s' % user_id)
        return activity_pool.assign(
            cr, uid, activity_id, user_id, context=context)

    def complete(self, cr, uid, activity_id, data, context=None):
        """
        Completes an :class:`activity<activity.nh_activity>`. Raises an
        exception if the :class:`user<base.res_users>` is not permitted
        to complete the activity.

        :param activity_id: id of activity
        :type activity_id: int
        :param data: data to submit
        :type data: dict
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: ``True``
        :rtype: bool
        """

        activity_pool = self.pool['nh.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        if not self.check_activity_access(
                cr, uid, activity_id, context=context):
            raise osv.except_osv(
                _('Error!'),
                'User ID %s not allowed to complete this activity: %s'
                % (uid, activity_id))
        activity_pool.submit(cr, uid, activity_id, data, context=context)
        return activity_pool.complete(cr, uid, activity_id, context=context)

    def get_cancel_reasons(self, cr, uid, context=None):
        """
        Gets the :class:`reason<activity_extension.nh_clinical_reason>`
        for each cancelled :class:`activity<activity.nh_activity>`.

        :returns: list of dictionaries of reasons
        :rtype: list
        """

        cancel_pool = self.pool['nh.cancel.reason']
        reason_ids = cancel_pool.search(cr, uid, [], context=context)
        reasons = []
        for reason in cancel_pool.browse(cr, uid, reason_ids, context=context):
            if not reason.system:
                reasons.append({'id': reason.id, 'name': reason.name})
        return reasons

    def get_form_description(self, cr, uid, patient_id, data_model,
                             context=None):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui to submit the
        observation.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        model_pool = self.pool[data_model]
        return model_pool.get_form_description(
            cr, uid, patient_id, context=context)

    def is_cancellable(self, cr, uid, data_model, context=None):
        """
        Checks if instances belonging to data model can be cancelled.
        Only data models which are `notifications` (i.e. either is or
        have inherited from
        :class:`notification<notification.nh_clinical_notification>`.

        :param data_model: data model
        :type data_model: str
        :returns: ``True`` or ``False``
        :rtype: bool
        """

        model_pool = self.pool[data_model]
        return model_pool.is_cancellable(
            cr, uid, context=context) if 'notification' in data_model \
            else False

    def get_activity_score(self, cr, uid, data_model, data, context=None):
        """
        Gets the activity score for a
        :class:`observation<observations.nh_clinical_patient_observation>`.

        :param data_model: name of the data model
        :type data_model: str
        :param data: observation data
        :type data: dict
        :returns: observation score. Otherwise ``False``
        :rtype: dict
        """
        model_pool = self.pool[data_model]
        return model_pool.calculate_score(
            data) if 'observation' in data_model else False

    def get_active_observations(self, cr, uid, patient_id, context=None):
        """
        Returns all active observation types supported by eObs, if the
        :class:`patient<base.nh_clinical_patient>` has an active
        :class:`spell<spell.nh_clinical_spell>`.

        :param patient_id: id of patient
        :type patient_id: int
        :returns: list of all observation types
        :rtype: list
        """

        activity_pool = self.pool['nh.activity']
        spell_id = activity_pool.search(
            cr, uid, [['location_id.user_ids', 'in', [uid]],
                      ['patient_id', '=', patient_id],
                      ['state', '=', 'started'],
                      ['data_model', '=', 'nh.clinical.spell']],
            context=context)
        if spell_id:
            return self._active_observations
        return []

    # # # # # # #
    #  PATIENTS #
    # # # # # # #

    def get_patient_info(self, cr, uid, hospital_number, context=None):
        """
        Gets :class:`patient<base.nh_clinical_patient>` information for
        a patient, including :class:`activities<activity.nh_activity>`.

        :param hospital_number: `hospital number` of patient
        :type hospital_number: str
        :returns: dictionary containing the patient fields.
        :rtype: dict
        """

        patient_pool = self.pool['nh.clinical.patient']
        activity_pool = self.pool['nh.activity']
        patient_pool.check_hospital_number(
            cr, uid, hospital_number, exception='False', context=context)
        patient_ids = patient_pool.search(
            cr, uid, [['other_identifier', '=', hospital_number]],
            context=context)
        domain = [
            ('patient_id', '=', patient_ids[0]),
            ('state', 'not in', ['cancelled', 'completed']),
            ('data_model', 'not in', ['nh.clinical.spell'])
        ]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activities = activity_pool.read(
            cr, uid, activity_ids, [], context=context)
        for a in activities:
            if a.get('date_scheduled'):
                scheduled = dt.strptime(a['date_scheduled'], DTF)
                time = scheduled - dt.now() if dt.now() <= scheduled \
                    else dt.now() - scheduled
                hours = time.seconds/3600
                minutes = time.seconds/60 - time.seconds/3600*60
                time_string = '{overdue}{days}{hours}:{minutes}'.format(
                    overdue='overdue: ' if dt.now() > scheduled else '',
                    days=str(time.days) + 'Days ' if time.days else '',
                    hours=hours if hours > 9 else '0' + str(hours),
                    minutes=str(
                        minutes if minutes > 9 else '0' + str(minutes)
                    ) + ' hours')
                a['time'] = time_string
            else:
                a['time'] = ''
        patient = self.get_patients(cr, uid, patient_ids, context=context)
        patient[0]['activities'] = activities
        return patient

    def get_patients(self, cr, uid, ids, context=None):
        """
        Return containing every field from
        :class:`patient<base.nh_clinical_patient>` for each patients.

        :param ids: ids of the patients. If empty, then all patients are
            returned
        :type ids: list
        :returns: list of patient dictionaries
        :rtype: list
        """
        if ids:
            domain = [
                ('patient_id', 'in', ids),
                ('state', '=', 'started'),
                ('data_model', '=', 'nh.clinical.spell'),
                '|',
                ('user_ids', 'in', [uid]),  # filter user responsibility
                ('patient_id.follower_ids', 'in', [uid])
            ]
        else:
            domain = [
                ('state', '=', 'started'),
                ('data_model', '=', 'nh.clinical.spell'),
                ('user_ids', 'in', [uid]),  # filter user responsibility
            ]
        return self.collect_patients(cr, uid, domain, context=context)

    def collect_patients(self, cr, uid, domain, context=None):
        """
        Collect patients for a given domain and return SQL output.

        :param cr: Odoo cursor
        :param uid: user ID for user doing operation
        :param domain: search domain to use
        :param context: Odoo context
        :return: list of dicts
        """
        activity_pool = self.pool['nh.activity']
        sql_model = self.pool['nh.clinical.sql']
        spell_ids = activity_pool.search(cr, uid, domain, context=context)
        spell_ids_sql = ','.join(map(str, spell_ids))
        sql = sql_model.get_collect_patients_sql(spell_ids_sql)
        patient_values = []
        if spell_ids:
            cr.execute(sql)
            patient_values = cr.dictfetchall()
        return patient_values

    def get_followed_patients(self, cr, uid, context=None):
        """
        Returns a list of :class:`patients<base.nh_clinical_patient>`
        followed by :class:`user<base.res_users>` in a dictionary
        (containing every field from the table).

        :param uid: id of the user
        :type uid: int
        :returns: list of patient dictionaries
        :rtype: list
        """

        patient_pool = self.pool['nh.clinical.patient']
        patient_ids = patient_pool.search(
            cr, uid, [['follower_ids', 'in', [uid]]], context=context)
        patient_ids_sql = ','.join(map(str, patient_ids))
        sql = """
        select distinct activity.id,
            patient.id,
            patient.dob,
            patient.gender,
            patient.sex,
            patient.other_identifier,
            case char_length(patient.patient_identifier) = 10
                when true then substring(patient.patient_identifier
                  from 1 for 3) || ' ' || substring(patient.patient_identifier
                  from 4 for 3) || ' ' || substring(patient.patient_identifier
                  from 7 for 4)
                else patient.patient_identifier
            end as patient_identifier,
            coalesce(patient.family_name, '') || ', ' ||
              coalesce(patient.given_name, '') || ' ' ||
              coalesce(patient.middle_names,'') as full_name,
            case
                when ews0.date_scheduled is not null then
                  case when greatest(now() at time zone 'UTC',
                    ews0.date_scheduled) != ews0.date_scheduled
                    then 'overdue: '
                  else '' end ||
                  case when extract(days from (greatest(now() at time zone
                    'UTC', ews0.date_scheduled) - least(now() at time zone
                    'UTC', ews0.date_scheduled))) > 0
                    then extract(days from (greatest(now() at time zone 'UTC',
                      ews0.date_scheduled) - least(now() at time zone 'UTC',
                      ews0.date_scheduled))) || ' day(s) '
                    else '' end ||
                  to_char(justify_hours(greatest(now() at time zone 'UTC',
                    ews0.date_scheduled) - least(now() at time zone 'UTC',
                    ews0.date_scheduled)), 'HH24:MI') || ' hours'
                else to_char((interval '0s'), 'HH24:MI') || ' hours'
            end as next_ews_time,
            location.name as location,
            location_parent.name as parent_location,
            case
                when ews1.score is not null then ews1.score::text
                else ''
            end as ews_score,
            ews1.clinical_risk,
            case
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) = 0 then 'same'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) > 0 then 'up'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) < 0 then 'down'
                when ews1.id is null and ews2.id is null then 'none'
                when ews1.id is not null and ews2.id is null then 'first'
                when ews1.id is null and ews2.id is not null then 'no latest'
            end as ews_trend,
            case
                when ews0.frequency is not null then ews0.frequency
                else 0
            end as frequency
        from nh_activity activity
        inner join nh_clinical_patient patient
          on patient.id = activity.patient_id
        inner join nh_clinical_location location
          on location.id = activity.location_id
        inner join nh_clinical_location location_parent
          on location_parent.id = location.parent_id
        left join ews1 on ews1.spell_activity_id = activity.id
        left join ews2 on ews2.spell_activity_id = activity.id
        left join ews0 on ews0.spell_activity_id = activity.id
        where activity.state = 'started' and activity.data_model =
          'nh.clinical.spell' and patient.id in (%s)
        order by location
        """ % patient_ids_sql
        patient_values = []
        if patient_ids:
            cr.execute(sql)
            patient_values = cr.dictfetchall()
        return patient_values

    def get_invited_users(self, cr, uid, patients, context=None):
        """
        Expects the return value from get_patients or
        get_followed_patients and adds the users that have an open
        follow invitation for each patient.
        """

        follow_pool = self.pool['nh.clinical.patient.follow']
        for p in patients:
            follow_ids = follow_pool.search(cr, uid, [
                ['activity_id.state', 'not in', ['completed', 'cancelled']],
                ['patient_ids', 'in', [p['id']]]], context=context)
            p['invited_users'] = [
                {'id': f.activity_id.user_id.id,
                 'name': f.activity_id.user_id.name}
                for f in follow_pool.browse(
                    cr, uid, follow_ids, context=context)]
        return True

    def get_patient_followers(self, cr, uid, patients, context=None):
        """
        Expects the return value from get_patients or
        get_followed_patients and adds the followers for each patient.
        """
        patient_pool = self.pool['nh.clinical.patient']
        for p in patients:
            patient = patient_pool.browse(cr, uid, p['id'], context=context)
            p['followers'] = [
                {'id': f.id, 'name': f.name} for f in patient.follower_ids]
        return True

    def update(self, cr, uid, patient_id, data, context=None):
        """
        Wraps :meth:`update()<api.nh_clinical_api.update>`, updating a
        :class:`patient<base.nh_clinical_patient>` record.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].update(
            cr, uid, patient_id, data, context=context)

    def register(self, cr, uid, hospital_number, data, context=None):
        """
        Wraps :meth:`register()<api.nh_clinical_api.register>`,
        register a :class:`patient<base.nh_clinical_patient>` in the
        system.

        :param hospital_number: `hospital number` of the patient
        :type hospital_number: str
        :param data: dictionary parameter that may contain the following
            about the patient: ``patient_identifier``, ``family_name``,
            ``given_name``, ``middle_names``, ``dob``, ``gender``,
            ``sex``.
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].register(
            cr, uid, hospital_number, data, context=context)

    def admit(self, cr, uid, hospital_number, data, context=None):
        """
        Extends :meth:`admit()<api.nh_clinical_api.admit>`,
        admitting a patient into a specified
        :class:`location<base.nh_clinical_location>`.

        :param hospital_number: `hospital number` of the patient
        :type hospital_number: str
        :param data: dictionary parameter that must contain a
            ``location`` key
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        res = self.pool['nh.clinical.api'].admit(
            cr, uid, hospital_number, data, context=context)
        return res

    def admit_update(self, cr, uid, patient_id, data, context=None):
        """
        Wraps :meth:`admit_update()<api.nh_clinical_api.admit_update>`,
        updating the :class:`spell<spell.nh_clinical_spell>`
        information of a :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :param data: dictionary parameter that must contain a
            ``location`` key
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].admit_update(
            cr, uid, patient_id, data, context=context)

    def cancel_admit(self, cr, uid, patient_id, context=None):
        """
        Extends
        :meth:`cancel_admit()<api.nh_clinical_api.cancel_admit>`,
        cancelling the open :class:`spell<spell.nh_clinical_spell>` of a
        :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].cancel_admit(
            cr, uid, patient_id, context=context)

    def discharge(self, cr, uid, patient_id, data, context=None):
        """
        Extends
        :meth:`discharge()<api.nh_clinical_api.discharge>`,
        closing the :class:`spell<spell.nh_clinical_spell>` of a
        :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :param data: may contain the key ``discharge_date``
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].discharge(
            cr, uid, patient_id, data, context=context)

    def cancel_discharge(self, cr, uid, patient_id, context=None):
        """
        Extends
        :meth:`cancel_discharge()<api.nh_clinical_api.cancel_discharge>`
        of a :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :returns: ``True``
        :rtype: bool
        """

        res = self.pool['nh.clinical.api'].cancel_discharge(
            cr, uid, patient_id, context=context)
        return res

    def merge(self, cr, uid, patient_id, data, context=None):
        """
        Wraps
        :meth:`merge()<api.nh_clinical_patient.merge>`
        of a :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient to merge
            INTO
        :type patient_id: str
        :param data: dictionary parameter that may contain the following
            keys ``from_identifier``, the `hospital number` of the
            patient merged FROM
        :type data: dict
        :type patient_id: str
        :returns: ``True``
        :rtype: bool
        """

        return self.pool['nh.clinical.api'].merge(
            cr, uid, patient_id, data, context=context)

    def transfer(self, cr, uid, hospital_number, data, context=None):
        """
        Extends
        :meth:`transfer()<api.nh_clinical_api.transfer>`, transferring
        a :class:`patient<base.nh_clinical_patient>` to a
        :class:`location<base.nh_clinical_location>`.

        :param hospital_number: `hospital number` of the patient
        :type hospital_number: str
        :param data: dictionary parameter that may contain the key
            ``location``
        :returns: ``True``
        :rtype: bool
        """

        res = self.pool['nh.clinical.api'].transfer(
            cr, uid, hospital_number, data, context=context)
        return res

    def cancel_transfer(self, cr, uid, patient_id, context=None):
        """
        Extends
        :meth:`cancel_transfer()<api.nh_clinical_api.cancel_transfer>`,
        cancelling the transfer of a
        :class:`patient<base.nh_clinical_patient>`.

        :param patient_id: `hospital number` of the patient
        :type patient_id: str
            ``location``
        :returns: ``True``
        :rtype: bool
        """

        res = self.pool['nh.clinical.api'].cancel_transfer(
            cr, uid, patient_id, context=context)
        return res

    def check_patient_responsibility(self, cr, uid, patient_id, context=None):
        """
        Verifies that a :class:`user<base.res_users>` is responsible for
        a :class:`patient<base.nh_clinical_patient>`.

        :param uid: id of the user
        :type uid: int
        :param patient_id: `hospital number` of the patient
        :type patient_id: str
        :returns: ``True`` if user is responsible. Otherwise ``False``
        :rtype: bool
        """

        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, patient_id, context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        return self.check_activity_access(
            cr, uid, spell.activity_id.id, context=context)

    def follow_invite(self, cr, uid, patient_ids, to_user_id, context=None):
        """
        Creates a
        :class:`follow activity<operations.nh_clinical_patient_follow>`
        for the :class:`user<base.res_users>` to follow the
        :class:`patients<base.nh_clinical_patients>`. Raises an
        exception if the user is not responsible for a patient.

        :param patient_ids: ids of the patients to follow
        :type patient_ids: list
        :param to_user_id: id of the user to invite
        :type to_user_id: int
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: id of the follow activity
        :rtype: int
        """

        if not all([self.check_patient_responsibility(
                cr, uid, patient_id, context=context
        ) for patient_id in patient_ids]):
            raise osv.except_osv(
                'Error!', 'You are not responsible for this patient.')
        follow_pool = self.pool['nh.clinical.patient.follow']
        follow_activity_id = follow_pool.create_activity(
            cr, uid, {'user_id': to_user_id}, {
                'patient_ids': [[6, 0, patient_ids]]}, context=context)
        return follow_activity_id

    def remove_followers(self, cr, uid, patient_ids, context=None):
        """
        Removes followers (:class:`users<base.res_users>`) from
        :class:`patients<base.nh_clinical_patients>`. Raises an
        exception if the user is not responsible for a patient.

        :param patient_ids: ids of the patients to unfollow
        :type patient_ids: list
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: ``True``
        :rtype: bool
        """

        if not all([self.check_patient_responsibility(
                cr, uid, patient_id, context=context
        ) for patient_id in patient_ids]):
            raise osv.except_osv(
                'Error!', 'You are not responsible for this patient.')
        activity_pool = self.pool['nh.activity']
        unfollow_pool = self.pool['nh.clinical.patient.unfollow']
        unfollow_activity_id = unfollow_pool.create_activity(cr, uid, {}, {
            'patient_ids': [[6, 0, patient_ids]]}, context=context)
        activity_pool.complete(cr, uid, unfollow_activity_id, context=context)
        return True

    def get_activities_for_patient(self, cr, uid, patient_id, activity_type,
                                   start_date=None, end_date=None,
                                   context=None):
        """
        Returns a list of
        :class:`activities<activity.nh_activity>` for a
        :class:`patient<base.nh_clinical_patient>` in a dictionary
        (containing every field from the table).

        :param patient_id: id of the patient
        :type patient_id: int
        :param activity_type: type of activity
        :type activity_type: str
        :param start_date: start date to filter.
            A month from now by default
        :type start_date: str
        :param end_date: end date to filter.
            `Now` by default
        :type end_date: str
        :returns: list of activity dictionaries for patient
        :rtype: list
        """

        start_date = dt.now()-td(days=30) if not start_date else start_date
        end_date = dt.now() if not end_date else end_date
        model_pool = self.pool[self._get_activity_type(
            cr, uid, activity_type, observation=True, context=context)] \
            if activity_type else self.pool['nh.activity']
        domain = [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed'),
            ('date_terminated', '>=', start_date.strftime(DTF)),
            ('date_terminated', '<=', end_date.strftime(DTF))] \
            if activity_type \
            else [('patient_id', '=', patient_id),
                  ('state', 'not in', ['completed', 'cancelled']),
                  ('data_model', '!=', 'nh.clinical.spell')]
        ids = model_pool.search(cr, uid, domain, context=context)
        return model_pool.read(cr, uid, ids, [], context=context)

    def create_activity_for_patient(self, cr, uid, patient_id, activity_type,
                                    context=None):
        """
        Creates an :class:`activity<activity.nh_activity>` of specified
        type for a :class:`patient<base.nh_clinical_patient>` if there
        is no open activity of that type for that patient. Raises
        exception if the activity type is invalid, if there's no open
        spell for the patient or if there are no access rules for the
        activity type.

        :param patient_id: id of the patient
        :type patient_id: int
        :param activity_type: type of activity
        :type activity_type: str
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: id of activity
        :rtype: int
        """

        if not activity_type:
            raise osv.except_osv(_('Error!'), 'Activity type not valid')
        model_name = self._get_activity_type(
            cr, uid, activity_type, observation=True, context=context)
        user_pool = self.pool['res.users']
        spell_pool = self.pool['nh.clinical.spell']
        access_pool = self.pool['ir.model.access']
        activity_pool = self.pool['nh.activity']
        user = user_pool.browse(cr, SUPERUSER_ID, uid, context=context)
        groups = [g.id for g in user.groups_id]
        rules_ids = access_pool.search(
            cr, SUPERUSER_ID, [
                ('model_id', '=', model_name),
                ('group_id', 'in', groups)], context=context)
        if not rules_ids:
            raise osv.except_osv(
                _('Error!'),
                'Access denied, there are no access rules for these activity '
                'type - user groups')
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, patient_id, context=context)
        if not spell_id:
            raise osv.except_osv(
                'Error!',
                'Cannot create a new activity without an open spell!')
        spell_activity_id = spell_pool.browse(
            cr, uid, spell_id, context=context).activity_id.id
        activity_ids = activity_pool.search(
            cr, SUPERUSER_ID, [
                ('parent_id', '=', spell_activity_id),
                ('patient_id', '=', patient_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', model_name)], context=context)
        if activity_ids:
            return activity_ids[0]
        return self._create_activity(
            cr, SUPERUSER_ID, model_name, {}, {'patient_id': patient_id},
            context=context)
