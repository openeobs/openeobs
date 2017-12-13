from datetime import datetime, timedelta

from openerp import SUPERUSER_ID
from openerp import api
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NHClinicalPatientObservationEWS(orm.Model):
    """
    Override of nh.clinical.patient.observation.ews for generic mental health
    behaviour
    """

    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    _partial_reasons = [
        ['asleep', 'Asleep'],
        ['refused', 'Refused'],
        ['request_by_doctor', 'Request By Doctor'],
        ['patient_aggression', 'Patient Aggression']
    ]

    _columns = {
        'partial_reason': fields.selection(_partial_reasons,
                                           'Reason if partial observation')
    }

    def complete(self, cr, uid, activity_id, context=None):
        """
        Mental health override that ensures Clinical Review tasks are set up
        for refusing patients at the appropriate time using CRON jobs.
        :returns: ``True``
        :rtype: bool
        """
        res = super(NHClinicalPatientObservationEWS, self).complete(
            cr, uid, activity_id, context=context)
        activity_model = self.pool['nh.activity']
        activity = activity_model.browse(cr, uid, activity_id, context=context)
        ews = activity.data_ref
        patient_spell = activity.spell_activity_id.data_ref
        patient_refusing = patient_spell.refusing_obs

        if not ews.is_partial:
            patient_spell.write({'refusing_obs': False})
        if ews.is_partial and not patient_refusing \
                and ews.partial_reason == 'refused':
            api_model = self.pool['nh.eobs.api']
            cron_model = self.pool['ir.cron']
            patient = api_model.get_patients(
                cr, uid, ews.patient_id.ids, context=context)
            days_to_schedule = 1
            higher_risks = ['None', 'Low']
            if patient[0].get('clinical_risk') in higher_risks:
                days_to_schedule = 7
            schedule_date = datetime.now() + timedelta(days=days_to_schedule)
            patient_spell.write({'refusing_obs': True})
            cron_model.create(cr, SUPERUSER_ID, {
                'name': 'Clinical Review Task '
                        'for Activity:{0}'.format(activity_id),
                'user_id': uid,
                'numbercall': 1,
                'model': 'nh.clinical.patient.observation.ews',
                'function': 'schedule_clinical_review_notification',
                'args': '({0},)'.format(activity_id),
                'priority': 0,
                'nextcall': schedule_date.strftime(DTF),
                'interval_type': 'days',
                'interval_number': days_to_schedule
            }, context=context)
        return res

    @api.model
    def schedule_clinical_review_notification(self, activity_id):
        """
        Determines if a Clinical Review notification needs to be created based
        on if a full NEWS observation has been completed since the partial
        NEWS that triggered the call to this method was completed

        :return: Nothing, only side effects
        """
        # Find all ews that have been done since the activity
        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)
        still_valid = self.is_refusal_in_effect(activity_id, mode='child')

        if still_valid:
            self.create_clinical_review_task(activity)

    @api.model
    def create_clinical_review_task(self, activity):
        """
        Create a 'nh.clinical.notification.clinical_review' record and
        associated activity.

        :param activity:
        :type activity: 'nh.activity' record
        """
        clinical_review_model = \
            self.pool['nh.clinical.notification.clinical_review']
        due_date = datetime.now().strftime(DTF)
        clinical_review_model.create_activity(
            self._cr, SUPERUSER_ID,
            {
                'creator_id': activity.id,
                'parent_id': activity.spell_activity_id.id,
                'date_scheduled': due_date,
                'date_deadline': due_date
            },
            {
                'patient_id': activity.data_ref.patient_id.id
            }
        )

    def is_refusal_in_effect(self, cr, uid, activity_id,
                             mode='parent', context=None):
        """
        Use the last_refused_ews SQL view to see if activity_id is part of a
        patient refusal

        :param cr: Odoo cursor
        :param uid: User doing operation
        :param activity_id: <nh.activity> Activity ID
        :param mode: Mode to operate on, parent goes up chain, child goes down
        :param context: Odoo Context
        :return: If the patient is currently in refusal
        """
        activity_model = self.pool['nh.activity']
        activity = activity_model.browse(cr, uid, activity_id)
        if activity.spell_activity_id.state in ['completed', 'cancelled']:
            return False

        column = 'last_activity_id'
        first_act_order = 'DESC'
        if mode == 'child':
            column = 'first_activity_id'
            first_act_order = 'ASC'

        cr.execute(
            'SELECT refused.refused, '
            'acts.date_terminated '
            'FROM refused_ews_activities AS refused '
            'RIGHT OUTER JOIN wb_activity_ranked AS acts '
            'ON acts.id = refused.id '
            'RIGHT OUTER JOIN nh_clinical_spell AS spell '
            'ON spell.activity_id = refused.spell_activity_id '
            'LEFT JOIN wb_transfer_ranked as transfer '
            'ON transfer.spell_id = spell.id '
            'AND transfer.rank = 1 '
            'LEFT JOIN last_finished_obs_stop AS obs_stop '
            'ON obs_stop.spell_id = spell.id '
            'WHERE {column} = {id} '
            'AND coalesce(acts.date_terminated '
            '>= transfer.date_terminated, TRUE) '
            'AND coalesce(acts.date_terminated >= '
            'obs_stop.activity_date_terminated, TRUE) '
            'AND (spell.obs_stop <> TRUE OR spell.obs_stop IS NULL) '
            'ORDER BY refused.spell_activity_id ASC, '
            'refused.first_activity_id {first_act_order}, '
            'refused.last_activity_id DESC '
            'LIMIT 1;'.format(
                column=column,
                id=activity_id,
                first_act_order=first_act_order
            )
        )
        result = cr.dictfetchall()
        if result:
            return result[0].get('refused', False)
        return False
