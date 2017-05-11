from openerp import models, api
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class FoodAndFluidReview(models.Model):
    """
    Food and Fluid Review task
    """

    _name = 'nh.clinical.notification.food_fluid_review'
    _inherit = 'nh.clinical.notification'

    _description = 'F&F - {} Fluid Intake Review'

    trigger_times = [15, 6]

    ESCALATION_TASKS = {
        0: [
            'Confirm adequate intake'
        ],
        1: [
            'Encourage fluid intake to above 1500ml',
            'Keep monitoring',
            'Inform Shift Coordinator'
        ],
        2: [
            'Encourage hourly fluids immediately',
            'Inform Shift Coordinator'
        ],
        3: [
            'Inform medical staff immediately'
        ]
    }

    @api.model
    def should_trigger_review(self):
        """
        Take the current localised time for the user and figure out if the
        review task should be triggered
        :return: True if correct localised time
        :rtype: bool
        """
        dateutils_model = self.env['datetime_utils']
        localised_time = dateutils_model.get_localised_time()
        if localised_time.hour in self.trigger_times:
            return True
        return False

    @api.model
    def get_review_task_summary(self):
        """
        Get the summary for the review task
        :return: string for summary
        :rtype: str
        """
        dateutils_model = self.env['datetime_utils']
        localised_time = dateutils_model.get_localised_time()
        return self._description.format(
            datetime.strftime(localised_time, '%-I%p').lower())

    @api.model
    def trigger_review_tasks_for_active_periods(self):
        """
        Method to trigger F&F review tasks for any active periods in the system
        Called by Scheduled Action every hour
        """
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        is_time_to_trigger_review = self.should_trigger_review()
        if is_time_to_trigger_review:
            activity_model = self.env['nh.activity']
            spell_activities = activity_model.search(
                [
                    ['data_model', '=', 'nh.clinical.spell'],
                    ['state', 'not in', ['completed', 'cancelled']]
                ]
            )
            for spell_activity in spell_activities:
                if food_fluid_model.active_food_fluid_period(
                        spell_activity.id):
                    self.schedule_review(spell_activity)

    def schedule_review(self, spell_activity):
        """
        Create the activity for the Food and Fluid Review Task
        :param spell_activity: Activity for patient's spell
        :return: activity ID
        """
        dateutils_model = self.env['datetime_utils']
        return self.create_activity(
            {
                'parent_id': spell_activity.id,
                'spell_activity_id': spell_activity.id,
                'patient_id': spell_activity.patient_id.id,
                'summary': self.get_review_task_summary(),
                'location_id': spell_activity.location_id.id,
                'date_scheduled': dateutils_model.get_current_time(
                    as_string=True)
            },
            {
                'patient_id': spell_activity.patient_id.id
            }
        )

    def get_view_description(self, form_desc):
        """
        Transform the form description into view description that can
        be used by the mobile. This will return a list of dicts similar to :
        [
            {
                'type': 'template',
                'template': 'nh_observation.custom_template'
            },
            {
                'type': 'task',
                'inputs': []
            }
        ]
        :param form_desc: List of dicts representing the inputs for the form
        :type form_desc: list
        :return: list of dicts representing a view description
        """
        view_desc = super(FoodAndFluidReview, self)\
            .get_view_description(form_desc)
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        food_fluid_obs_acts = food_fluid_model.get_obs_activities_for_period(
            self.activity_id.spell_activity_id.id,
            self.activity_id.date_scheduled
        )
        food_fluid_obs = \
            [rec.data_ref.read()[0] for rec in food_fluid_obs_acts]
        period = food_fluid_model.get_period_dictionaries(
            food_fluid_obs, include_units=True)[0]
        period = self.process_period_datetimes(period)
        score = period.get('score')
        view_desc[0] = {
            'type': 'template',
            'template': 'nh_food_and_fluid.review_task',
            'view_data': {
                'title': '<strong>{}</strong>'.format(
                    self.activity_id.summary),
                'period_start': period.get('period_start_datetime'),
                'period_end': period.get('period_end_datetime'),
                'period_fluid_intake': period.get('total_fluid_intake'),
                'period_fluid_balance': period.get('fluid_balance'),
                'period_score': score,
                'period_escalation_tasks':
                    self.get_escalation_tasks_for_score(score),
                'submit_title': 'Confirm Action'
            }
        }
        return view_desc

    def get_escalation_tasks_for_score(self, score):
        """
        Get the list of escalation tasks associated with a given F&F score
        :param score: F&F score for period
        :return: list of escalation task names
        """
        if score not in self.ESCALATION_TASKS.keys():
            raise ValueError('Supplied score out of range')
        return self.ESCALATION_TASKS.get(score)

    @staticmethod
    def process_period_datetimes(period):
        """
        Change the format in the supplied period to be similar to
        7am dd/mm
        :param period: period dictionary
        :return: period dictionary
        """
        datetime_keys = ['period_start_datetime', 'period_end_datetime']
        for datetime_key in datetime_keys:
            if period.get(datetime_key):
                period[datetime_key] = datetime.strptime(
                    period.get(datetime_key), dtf)\
                    .strftime('%-I%p %d/%m').lower()
        return period
