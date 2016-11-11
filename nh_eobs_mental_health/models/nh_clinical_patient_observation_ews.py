from openerp.osv import orm, fields
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api
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
        It determines which acuity case the current observation is in
        with the stored data and responds to the different policy
        triggers accordingly defined on the ``_POLICY`` dictionary::

            {'ranges': [0, 4, 6], 'case': '0123', --> Used with bisect to
            determine the acuity case based on the score.
            'frequencies': [720, 240, 60, 30], --> frequency of recurrency
            of the NEWS observation, based on the case.
            'notifications': [...],
               Information sent to the trigger_notifications method,
               based on case.
            'risk': ['None', 'Low', 'Medium', 'High']} --> Clinical risk
            of the patient, based on case.

        All the case based lists work in a simple way:
        list[case] --> value used

        After the policy triggers take place the activity is `completed`
        and a new NEWS activity is created. Then the case based
        `frequency` is applied, effectively scheduling it.

        In the case of having a `partial` observation we won't have a new
        frequency so the new activity is scheduled to the same time the
        one just `completed` was, as the need for a complete observation
        is still there.

        :returns: ``True``
        :rtype: bool
        """
        res = super(NHClinicalPatientObservationEWS, self).complete(
            cr, uid, activity_id, context=context)
        activity_model = self.pool['nh.activity']
        activity = activity_model.browse(cr, uid, activity_id, context=context)
        ews = activity.data_ref
        if ews.is_partial and ews.partial_reason == 'refused':
            api_model = self.pool['nh.eobs.api']
            cron_model = self.pool['ir.cron']
            patient = api_model.get_patients(
                cr, uid, ews.patient_id.ids, context=context)
            days_to_schedule = 1
            higher_risks = ['None', 'Low']
            if patient[0].get('clinical_risk') in higher_risks:
                days_to_schedule = 7
            schedule_date = datetime.now() + timedelta(days=days_to_schedule)
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
        ews_gen = self.get_child_activity(
            activity_model, activity, self._name, context=self._context)
        next_full_ews = list(ews_gen)
        next_ews_complete = False
        if next_full_ews:
            next_ews_complete = next_full_ews[0].state == 'completed'
        if not next_full_ews or not next_ews_complete:
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
