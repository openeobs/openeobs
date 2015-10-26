# -*- coding: utf-8 -*-
"""
`parameters.py` defines a set of activity types to record basic
medical parameters. They have in common that they are not measurements
like the observations.

They can represent a patient state, flag or any simple medical
information that is not measured, but set by the medical staff.

They are represented by activity types mainly for audit purposes as
their static nature would allow them to be fields instead. The last
completed one would represent the current status regarding that specific
parameter.
"""
from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt, timedelta as td
from openerp.addons.nh_observations.helpers import refresh_materialized_views
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
_logger = logging.getLogger(__name__)

frequencies = [
    (15, 'Every 15 Minutes'),
    (30, 'Every 30 Minutes'),
    (60, 'Every Hour'),
    (120, 'Every 2 Hours'),
    (240, 'Every 4 Hours'),
    (360, 'Every 6 Hours'),
    (480, 'Every 8 Hours'),
    (600, 'Every 10 Hours'),
    (720, 'Every 12 Hours'),
    (1440, 'Every Day')
]


class nh_clinical_patient_mrsa(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` MRSA infection status
    to `yes` or `no`. Depending on whether the patient has the infection
    or not.
    """
    _name = 'nh.clinical.patient.mrsa'
    _inherit = ['nh.activity.data'] 
    _columns = {
        'status': fields.boolean('MRSA', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_mrsa, self).complete(cr, uid, activity_id, context)
        return res

class nh_clinical_patient_diabetes(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` diabetes status
    to `yes` or `no`. Depending on whether the patient is diabetic or
    not.
    """
    _name = 'nh.clinical.patient.diabetes'
    _inherit = ['nh.activity.data'] 
    _columns = {
        'status': fields.boolean('Diabetes', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_diabetes, self).complete(cr, uid, activity_id, context)
        return res


class nh_clinical_patient_palliative_care(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` palliative care status
    to `yes` or `no`. This would mainly depend on hospital policy and
    the medical staff assessment.
    """
    _name = 'nh.clinical.patient.palliative_care'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['status'], context=context):
            result[r['id']] = 'Yes' if r['status'] else 'No'
        return result

    _columns = {
        'status': fields.boolean('On Palliative Care?', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        if activity.data_ref.status:
            activity_ids = activity_pool.search(cr, uid, [['patient_id', '=', activity.data_ref.patient_id.id],
                                                          ['state', 'not in', ['completed', 'cancelled']],
                                                          '|', ['data_model', 'ilike', '%observation%'],
                                                          ['data_model', 'ilike', '%notification%']], context=context)
            [activity_pool.cancel(cr, uid, aid, context=context) for aid in activity_ids]
        return super(nh_clinical_patient_palliative_care, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_patient_post_surgery(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` post surgery status
    to `yes` or `no`. This would be set as `yes` after surgery has
    taken place and then set to `no` after recovery has been completed.
    Although mainly depends on hospital policy and medical staff
    assessment.
    """
    _name = 'nh.clinical.patient.post_surgery'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['status'], context=context):
            result[r['id']] = 'Yes' if r['status'] else 'No'
        return result

    _columns = {
        'status': fields.boolean('On Recovery from Surgery?', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }
    _ews_frequency = 60

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        if activity.data_ref.status:
            current_case = ews_pool.get_last_case(cr, uid, activity.data_ref.patient_id.id, context=context)
            current_freq = ews_pool._POLICY['frequencies'][current_case] if isinstance(current_case, int) else 0
            if current_freq > self._ews_frequency:
                api_pool.change_activity_frequency(cr, uid, activity.data_ref.patient_id.id,
                                                   'nh.clinical.patient.observation.ews', self._ews_frequency,
                                                   context=context)
        return super(nh_clinical_patient_post_surgery, self).complete(cr, uid, activity_id, context=context)

    def current_status(self, cr, uid, patient_id, context=None):
        """
        Checks if the provided :class:`patient<base.nh_clinical_patient>`
        had surgery in the last 4 hours.

        :parameter patient_id: :class:`patient<base.nh_clinical_patient>` id.
        :type patient_id: int
        :returns: ``True`` or ``False``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        a_ids = activity_pool.search(cr, uid, [['patient_id', '=', patient_id], ['data_model', '=', self._name],
                                               ['state', '=', 'completed'],
                                               ['date_terminated', '>=', (dt.now()-td(hours=4)).strftime(dtf)]],
                                     order='date_terminated desc, sequence desc', context=context)
        if not a_ids:
            return False
        return activity_pool.browse(cr, uid, a_ids[0], context=context).data_ref.status


class nh_clinical_patient_critical_care(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` critical care status
    to `yes` or `no`. This would mainly depend on hospital policy and
    the medical staff assessment.
    """
    _name = 'nh.clinical.patient.critical_care'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['status'], context=context):
            result[r['id']] = 'Yes' if r['status'] else 'No'
        return result

    _columns = {
        'status': fields.boolean('On Critical Care?', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }
    _ews_frequency = 240

    def current_status(self, cr, uid, patient_id, context=None):
        """
        Checks if the provided :class:`patient<base.nh_clinical_patient>`
        was marked with critical care status within the last 24 hours.

        :parameter patient_id: :class:`patient<base.nh_clinical_patient>` id.
        :type patient_id: int
        :returns: ``True`` or ``False``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        a_ids = activity_pool.search(cr, uid, [['patient_id', '=', patient_id], ['data_model', '=', self._name],
                                               ['state', '=', 'completed'],
                                               ['date_terminated', '>=', (dt.now()-td(hours=24)).strftime(dtf)]],
                                     order='date_terminated desc, sequence desc', context=context)
        if not a_ids:
            return False
        return activity_pool.browse(cr, uid, a_ids[0], context=context).data_ref.status

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        if activity.data_ref.status:
            current_case = ews_pool.get_last_case(cr, uid, activity.data_ref.patient_id.id, context=context)
            current_freq = ews_pool._POLICY['frequencies'][current_case] if isinstance(current_case, int) else 0
            if current_freq > self._ews_frequency:
                api_pool.change_activity_frequency(cr, uid, activity.data_ref.patient_id.id,
                                                   'nh.clinical.patient.observation.ews', self._ews_frequency,
                                                   context=context)
        return super(nh_clinical_patient_critical_care, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_patient_weight_monitoring(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` weight monitoring status
    to `yes` or `no`. This would mainly depend on hospital policy and
    the medical staff assessment.

    This parameter is directly related to the
    :mod:`weight<observations.nh_clinical_patient_observation_weight>`
    observation.
    """
    _name = 'nh.clinical.patient.weight_monitoring'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['status'], context=context):
            result[r['id']] = 'On' if r['status'] else 'Off'
        return result

    _columns = {
        'status': fields.boolean('Weight Monitoring', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    @refresh_materialized_views('weight')
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        weight_pool = self.pool['nh.clinical.patient.observation.weight']
        if activity.data_ref.status:
            activity_pool.cancel_open_activities(cr, uid, activity.parent_id.id, weight_pool._name, context=context)
            weight_activity_id = weight_pool.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})
            activity_pool.schedule(cr, SUPERUSER_ID, weight_activity_id, context=context)

        return super(nh_clinical_patient_weight_monitoring, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_patient_urine_output_target(orm.Model):
    """
    Represents the action of setting the current urine output target
    for the :class:`patient<base.nh_clinical_patient>`. This would
    mainly be decided by the medical staff assessment.

    This parameter is directly related to the
    :mod:`urine output<observations.nh_clinical_patient_observation_urine_output>`
    observation.
    """
    _name = 'nh.clinical.patient.uotarget'
    _inherit = ['nh.activity.data']
    _columns = {
        'volume': fields.integer('Volume', required=True),
        'unit': fields.selection([[1, 'ml/hour'], [2, 'L/day']], 'Unit', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def current_target(self, cr, uid, patient_id, context=None):
        """
        Gets the current urine output target for the provided
        :class:`patient<base.nh_clinical_patient>`

        :returns: ``[volume,unit]``
        :rtype: list
        """
        activity_pool = self.pool['nh.activity']
        a_ids = activity_pool.search(cr, uid, [['patient_id', '=', patient_id], ['data_model', '=', self._name],
                                               ['state', '=', 'completed']],
                                     order='date_terminated desc, sequence desc', context=context)
        if not a_ids:
            return False
        activity = activity_pool.browse(cr, uid, a_ids[0], context=context)
        return [activity.data_ref.volume, activity.data_ref.unit]

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_urine_output_target, self).complete(cr, uid, activity_id, context)
        return res
