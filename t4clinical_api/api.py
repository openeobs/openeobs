from openerp.osv import orm, osv, fields
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api.external'
    #_inherit = 't4.clinical.api'

    def _check_activity_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return True

    def check_activity_access(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            return False
        return True

    def _create_activity(self, cr, uid, data_model, vals_activity=None, vals_data=None, context=None):
        model_pool = self.pool[data_model]
        activity_id = model_pool.create_activity(cr, uid, vals_activity, vals_data, context=context)
        _logger.info("Activity created id=%s, data_model=%s\n vals_activity: %s\n vals_data: %s"
                     % (activity_id, data_model, vals_activity, vals_data))
        return activity_id

    def _check_hospital_number(self, cr, uid, hospital_number, context=None):
        patient_pool = self.pool['t4.clinical.patient']
        domain = [('other_identifier', '=', hospital_number)]
        return patient_pool.search(cr, uid, domain, context=context)

    def _cancel_activity(self, cr, uid, patient_id, activity_type, context=None):
        # Y: what if more than one activities of the type for the patient exist?
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        domain = [('data_model', '=', activity_type), ('state', '=', 'completed')]
        admit_activity = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        return activity_pool.cancel(cr, uid, admit_activity[0], context=context)

    def _frequency(self, cr, uid, patient_id, activity_type, operation, data=None, context=None):
        if not activity_type:
            raise osv.except_osv(_('Error!'), 'Activity type not valid')
        field_name = activity_type+'_frequency'
        spell_pool = self.pool['t4.clinical.spell']
        domain = [('patient_id', '=', patient_id), ('state', 'not in', ['completed', 'cancelled'])]
        spell_ids = spell_pool.search(cr, SUPERUSER_ID, domain, context=context)
        if not spell_ids:
            raise osv.except_osv(_('Error!'), 'Spell not found')
        if operation == 'get':
            return spell_pool.read(cr, SUPERUSER_ID, spell_ids, [field_name], context=context)
        else:
            return spell_pool.write(cr, SUPERUSER_ID, spell_ids, {field_name: data['frequency']}, context=context)

    # # # # # # # #
    #  ACTIVITIES #
    # # # # # # # #

    def get_activities(self, cr, uid, ids, context=None):
        """
        Return a list of activities
        :param ids: ids of the activities we want. If empty returns all activities.
        """

        domain = [('id', 'in', ids)] if ids else [
            ('state', 'not in', ['completed', 'cancelled']),
            '|', ('date_scheduled', '<=', (dt.now()+td(days=1)).strftime(DTF)),
            ('date_deadline', '<=', (dt.now()+td(days=1)).strftime(DTF))
        ]
        activity_pool = self.pool['t4.activity']
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activity_ids_sql = ','.join(map(str, activity_ids))
        sql = """
        with
            completed_ews as(
                select
                    ews.id,
                    spell.patient_id,
                    ews.score,
                    ews.clinical_risk,
                    rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
                from t4_clinical_spell spell
                left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
                inner join t4_activity activity on ews.activity_id = activity.id
                where activity.state = 'completed'
            )
        select activity.id,
            activity.summary,
            ews1.clinical_risk,
            case
                when date_scheduled is not null then date_scheduled::text
                when date_deadline is not null then date_deadline::text
                else ''
            end as deadline,
            case
                when activity.date_scheduled is not null and greatest(now() at time zone 'UTC',activity.date_scheduled) != activity.date_scheduled then 'overdue: ' || to_char(justify_hours(greatest(now() at time zone 'UTC',activity.date_scheduled) - least(now() at time zone 'UTC',activity.date_scheduled)), 'HH24:MI') || ' hours'
                when activity.date_scheduled is not null and greatest(now() at time zone 'UTC',activity.date_scheduled) = activity.date_scheduled then to_char(justify_hours(greatest(now() at time zone 'UTC',activity.date_scheduled) - least(now() at time zone 'UTC',activity.date_scheduled)), 'HH24:MI') || ' hours'
                when activity.date_deadline is not null and greatest(now() at time zone 'UTC',activity.date_deadline) != activity.date_deadline then 'overdue: ' || to_char(justify_hours(greatest(now() at time zone 'UTC',activity.date_deadline) - least(now() at time zone 'UTC',activity.date_deadline)), 'HH24:MI') || ' hours'
                when activity.date_deadline is not null and greatest(now() at time zone 'UTC',activity.date_deadline) = activity.date_deadline then to_char(justify_hours(greatest(now() at time zone 'UTC',activity.date_deadline) - least(now() at time zone 'UTC',activity.date_deadline)), 'HH24:MI') || ' hours'
                else to_char((interval '0s'), 'HH24:MI') || ' hours'
            end as deadline_time,
            coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
            location.name as location,
            location_parent.name as parent_location,
            case
                when ews1.score is not null then ews1.score::text
                else ''
            end as ews_score,
            case
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'down'
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'up'
                when ews1.id is null and ews2.id is null then 'none'
                when ews1.id is not null and ews2.id is null then 'first'
                when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen.
            end as ews_trend,
            case
                when position('notification' in activity.data_model)::bool then true
                else false
            end as notification
        from t4_activity activity
        inner join t4_clinical_patient patient on patient.id = activity.patient_id
        inner join t4_clinical_location location on location.id = activity.location_id
        inner join t4_clinical_location location_parent on location_parent.id = location.parent_id
        left join completed_ews ews1 on ews1.patient_id = activity.patient_id and ews1.rank = 1
        left join completed_ews ews2 on ews2.patient_id = activity.patient_id and ews2.rank = 2
        where activity.id in (%s)
        """ % activity_ids_sql
        activity_values = []
        if activity_ids:
            cr.execute(sql)
            activity_values = cr.dictfetchall()
        return activity_values

    def cancel(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        activity_pool.submit(cr, uid, activity_id, data, context=context)
        return activity_pool.cancel(cr, uid, activity_id, context=context)

    def submit(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.submit(cr, uid, activity_id, data, context=context)

    def unassign(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        return activity_pool.unassign(cr, uid, activity_id, context=context)

    def assign(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        user_pool = self.pool['res.users']
        user_id = uid
        self._check_activity_id(cr, uid, activity_id, context=context)
        if data.get('user_id'):
            user_id = data['user_id']
            domain = [('id', '=', user_id)]
            user_ids = user_pool.search(cr, uid, domain, context=context)
            if not user_ids:
                raise osv.except_osv(_('Error!'), 'User ID not found: %s' % user_id)
        return activity_pool.assign(cr, uid, activity_id, user_id, context=context)

    # def complete(self, cr, uid, activity_id, data, context=None):
    #     activity_pool = self.pool['t4.activity']
    #     self._check_activity_id(cr, uid, activity_id, context=context)
    #     return activity_pool.complete(cr, uid, activity_id, data)

    def complete(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        self._check_activity_id(cr, uid, activity_id, context=context)
        activity_pool.submit(cr, uid, activity_id, data, context=context)
        return activity_pool.complete(cr, uid, activity_id, context=context)

    def get_cancel_reasons(self, cr, uid, context=None):
        cancel_pool = self.pool['t4.cancel.reason']
        reason_ids = cancel_pool.search(cr, uid, [], context=context)
        reasons = []
        for reason in cancel_pool.browse(cr, uid, reason_ids, context=context):
            if not reason.system:
                reasons.append({'id':reason.id, 'name': reason.name})
        return reasons

    # # # # # # #
    #  PATIENTS #
    # # # # # # #

    def get_patients(self, cr, uid, ids, context=None):
        """
        Return a list of patients in dictionary format (containing every field from the table)
        :param ids: ids of the patients we want. If empty returns all patients.
        """
        domain = [
            ('state', '=', 'started'),
            ('patient_id', 'in', ids),
            ('data_model', '=', 't4.clinical.spell')
        ] if ids else [
            ('state', '=', 'started'),
            ('data_model', '=', 't4.clinical.spell')
        ]
        activity_pool = self.pool['t4.activity']
        spell_ids = activity_pool.search(cr, uid, domain, context=context)
        spell_ids_sql = ','.join(map(str, spell_ids))
        sql = """
        with
            completed_ews as(
                select
                    ews.id,
                    spell.patient_id,
                    ews.score,
                    ews.clinical_risk,
                    rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
                from t4_clinical_spell spell
                left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
                inner join t4_activity activity on ews.activity_id = activity.id
                where activity.state = 'completed'
            ),
            scheduled_ews as(
                select
                    spell.patient_id,
                    activity.date_scheduled,
                    ews.frequency,
                    rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
                from t4_clinical_spell spell
                left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
                inner join t4_activity activity on ews.activity_id = activity.id
                where activity.state = 'scheduled'
            )
        select patient.id,
            patient.dob,
            patient.gender,
            patient.sex,
            patient.other_identifier,
            coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
            case
                when ews0.date_scheduled is not null and greatest(now() at time zone 'UTC',ews0.date_scheduled) != ews0.date_scheduled then 'overdue: ' || to_char(justify_hours(greatest(now() at time zone 'UTC',ews0.date_scheduled) - least(now() at time zone 'UTC',ews0.date_scheduled)), 'HH24:MI') || ' hours'
                when ews0.date_scheduled is not null and greatest(now() at time zone 'UTC',ews0.date_scheduled) = ews0.date_scheduled then to_char(justify_hours(greatest(now() at time zone 'UTC',ews0.date_scheduled) - least(now() at time zone 'UTC',ews0.date_scheduled)), 'HH24:MI') || ' hours'
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
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'down'
                when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'up'
                when ews1.id is null and ews2.id is null then 'none'
                when ews1.id is not null and ews2.id is null then 'first'
                when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen.
            end as ews_trend
        from t4_activity activity
        inner join t4_clinical_patient patient on patient.id = activity.patient_id
        inner join t4_clinical_location location on location.id = activity.location_id
        inner join t4_clinical_location location_parent on location_parent.id = location.parent_id
        left join completed_ews ews1 on ews1.patient_id = activity.patient_id and ews1.rank = 1
        left join completed_ews ews2 on ews2.patient_id = activity.patient_id and ews2.rank = 2
        left join scheduled_ews ews0 on ews0.patient_id = activity.patient_id and ews0.rank = 1
        where activity.state = 'started' and activity.data_model = 't4.clinical.spell' and activity.id in (%s)
        """ % spell_ids_sql
        patient_values = []
        if spell_ids:
            cr.execute(sql)
            patient_values = cr.dictfetchall()
        return patient_values

    def update(self, cr, uid, patient_id, data, context=None):
        activity_pool = self.pool['t4.activity']
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            _logger.warn("Patient registered from an update call - data available:%s" % data)
            self.register(cr, uid, patient_id, data, context=context)
        data.update({'other_identifier': patient_id})
        update_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.update', {}, {}, context=context)
        res = activity_pool.submit(cr, uid, update_activity, data, context=context)
        activity_pool.complete(cr, uid, update_activity, context=context)
        _logger.info("Patient updated\n data: %s" % data)
        return res

    def register(self, cr, uid, patient_id, data, context=None):
        """
        Registers a new patient into the system
        :param patient_id: Hospital Number of the patient
        :param data: dictionary parameter that may contain the following keys:
            patient_identifier: NHS number
            family_name: Surname
            given_name: Name
            middle_names: Middle names
            dob: Date of birth
            gender: Gender (M/F)
            sex: Sex (M/F)
        """
        activity_pool = self.pool['t4.activity']
        register_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.register', {}, {}, context=context)
        data.update({'other_identifier': patient_id})
        activity_pool.submit(cr, uid, register_activity, data, context=context)
        activity_pool.complete(cr, uid, register_activity, context=context)
        _logger.info("Patient registered\n data: %s" % data)
        return True

    def admit(self, cr, uid, patient_id, data, context=None):
        """
        Admits a patient into the specified location.
        :param patient_id: Hospital number of the patient
        :param data: dictionary parameter that may contain the following keys:
            location: location code where the patient will be admitted. REQUIRED
            start_date: admission start date.
            doctors: consulting and referring doctors list of dictionaries. expected format:
               [...
               {
               'type': 'c' or 'r',
               'code': code string,
               'title':, 'given_name':, 'family_name':, }
               ...]
                if doctor doesn't exist, we create partner, but don't create user for that doctor.
        """
        activity_pool = self.pool['t4.activity']
        data.update({'other_identifier': patient_id})
        admit_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.admit', {}, {}, context=context)
        activity_pool.submit(cr, uid, admit_activity, data, context=context)
        activity_pool.complete(cr, uid, admit_activity, context=context)
        _logger.info("Patient admitted\n data: %s" % data)
        return True
    
    def admit_update(self, cr, uid, patient_id, data, context=None):
        """
        Updates the spell information of the patient. Accepts the same parameters as admit.
        """
        activity_pool = self.pool['t4.activity']
        data.update({'other_identifier': patient_id})
        update_activity = self._create_activity(cr, uid, 't4.clinical.adt.spell.update', {}, {}, context=context)
        activity_pool.submit(cr, uid, update_activity, data, context=context)
        activity_pool.complete(cr, uid, update_activity, context=context)
        _logger.info("Admission updated\n data: %s" % data)
        return True
        
    def cancel_admit(self, cr, uid, patient_id, context=None):
        """
        Cancels the open admission of the patient.
        """
        activity_pool = self.pool['t4.activity']
        data = {'other_identifier': patient_id}
        cancel_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.cancel_admit', {}, {}, context=context)
        activity_pool.submit(cr, uid, cancel_activity, data, context=context)
        activity_pool.complete(cr, uid, cancel_activity, context=context)
        _logger.info("Admission cancelled\n data: %s" % data)
        return True

    def discharge(self, cr, uid, patient_id, data, context=None):
        """
        Discharges the patient.
        :param patient_id: Hospital number of the patient
        :param data: dictionary parameter that may contain the following keys:
            discharge_date: patient discharge date.
        """
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        patient_pool = self.pool['t4.clinical.patient']
        patientdb_id = patient_pool.search(cr, uid, [('other_identifier', '=', patient_id)], context=context)
        discharge_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.discharge', {'patient_id': patientdb_id[0]}, {'other_identifier': patient_id, 'discharge_date': data.get('discharge_date')}, context=context)
        activity_pool.complete(cr, uid, discharge_activity, context=context)
        _logger.info("Patient discharged: %s" % patient_id)
        return True

    def cancel_discharge(self, cr, uid, patient_id, context=None):
        """
        Cancels the last discharge of the patient.
        """
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        patient_pool = self.pool['t4.clinical.patient']
        patientdb_id = patient_pool.search(cr, uid, [('other_identifier', '=', patient_id)], context=context)
        cancel_discharge_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.cancel_discharge', {'patient_id': patientdb_id[0]}, {}, context=context)
        activity_pool.submit(cr, uid, cancel_discharge_activity, {'other_identifier': patient_id}, context=context)
        activity_pool.complete(cr, uid, cancel_discharge_activity, context=context)
        _logger.info("Discharge cancelled for patient: %s" % patient_id)
        return True

    def merge(self, cr, uid, patient_id, data, context=None):
        """
        Merges a specified patient into the patient.
        :param patient_id: Hospital number of the patient we want to merge INTO
        :param data: dictionary parameter that may contain the following keys:
            from_identifier: Hospital number of the patient we want to merge FROM
        """
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        data.update({'into_identifier': patient_id})
        merge_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.merge', {}, {}, context=context)
        activity_pool.submit(cr, uid, merge_activity, data, context=context)
        activity_pool.complete(cr, uid, merge_activity, context=context)
        _logger.info("Patient merged\n data: %s" % data)
        return True

    def transfer(self, cr, uid, patient_id, data, context=None):
        """
        Transfers the patient to the specified location.
        :param patient_id: Hospital number of the patient
        :param data: dictionary parameter that may contain the following keys:
            location: location code where the patient will be transferred. REQUIRED
        """
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        data.update({'other_identifier': patient_id})
        transfer_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.transfer', {}, {}, context=context)
        activity_pool.submit(cr, uid, transfer_activity, data, context=context)
        activity_pool.complete(cr, uid, transfer_activity, context=context)
        _logger.info("Patient transferred\n data: %s" % data)
        return True

    def cancel_transfer(self, cr, uid, patient_id, context=None):
        """
        Cancels the last transfer of the patient.
        """
        if not self._check_hospital_number(cr, uid, patient_id, context=context):
            raise osv.except_osv(_('Error!'), 'Patient ID not found: %s' % patient_id)
        activity_pool = self.pool['t4.activity']
        patient_pool = self.pool['t4.clinical.patient']
        patientdb_id = patient_pool.search(cr, uid, [('other_identifier', '=', patient_id)], context=context)
        cancel_transfer_activity = self._create_activity(cr, uid, 't4.clinical.adt.patient.cancel_transfer', {'patient_id': patientdb_id[0]}, {}, context=context)
        activity_pool.submit(cr, uid, cancel_transfer_activity, {'other_identifier': patient_id}, context=context)
        activity_pool.complete(cr, uid, cancel_transfer_activity, context=context)
        _logger.info("Transfer cancelled for patient: %s" % patient_id)
        return True

    def get_activities_for_patient(self, cr, uid, patient_id, activity_type, start_date=dt.now()+td(days=-30),
                                end_date=dt.now(), context=None):
        """
        Returns a list of activities in dictionary format (containing every field from the table)
        :param patient_id: Postgres ID of the patient to get the activities from.
        :param activity_type: Type of activity we want.
        :param start_date: start date to filter. A month from now by default.
        :param end_date: end date to filter. Now by default.
        """
        model_pool = self.pool['t4.clinical.patient.observation.'+activity_type] if activity_type else self.pool['t4.activity']
        domain = [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed'),
            ('date_terminated', '>=', start_date.strftime(DTF)),
            ('date_terminated', '<=', end_date.strftime(DTF))] if activity_type \
            else [('patient_id', '=', patient_id), ('state', 'not in', ['completed', 'cancelled'])]
        ids = model_pool.search(cr, uid, domain, context=context)
        return model_pool.read(cr, uid, ids, [], context=context)

    def create_activity_for_patient(self, cr, uid, patient_id, activity_type, context=None):
        if not activity_type:
            raise osv.except_osv(_('Error!'), 'Activity type not valid')
        model_name = 't4.clinical.patient.observation.'+activity_type
        user_pool = self.pool['res.users']
        access_pool = self.pool['ir.model.access']
        user = user_pool.browse(cr, SUPERUSER_ID, uid, context=context)
        rules_ids = access_pool.search(cr, SUPERUSER_ID, [('model_id', '=', model_name), ('group_id', 'in', user.groups_id)], context=context)
        if not rules_ids:
            raise osv.except_osv(_('Error!'), 'Access denied, there are no access rules for these activity type - user groups')
        rules_values = access_pool.read(cr, SUPERUSER_ID, rules_ids, ['perm_responsibility'], context=context)
        if not any([r['perm_responsibility'] for r in rules_values]):
            raise osv.except_osv(_('Error!'), 'Access denied, the user is not responsible for this activity type')
        return self._create_activity(cr, SUPERUSER_ID, model_name, {}, {'patient_id': patient_id}, context=context)

    def get_frequency(self, cr, uid, patient_id, activity_type, context=None):
        return self._frequency(cr, uid, patient_id, activity_type, 'get', context=context)

    def set_frequency(self, cr, uid, patient_id, activity_type, data, context=None):
        return self._frequency(cr, uid, patient_id, activity_type, 'set', data=data, context=context)



