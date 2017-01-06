from openerp import models


class MentalHealthObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        """
        Returns a dictionary that will be used to populate the report.
        Most of the values are themselves dictionaries returned by
        `activity.read()`. However they also have an additional key named
        'values' that contains the model record as dictionaries returned by
        `model.read()`.

        :param data:
        :param ews_only:
        :return:
        :rtype: dict
        """
        report_data = super(MentalHealthObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)

        report_data['draw_graph_js'] = \
            '/nh_eobs_mental_health/static/src/js/observation_report.js'
        report_data['refusal_events_data'] = \
            self.get_refusal_events_data()

        return report_data

    def get_refusal_episodes(self, spell_activity_id):
        """
        Collect the refusal episodes for the spell provided

        :param spell_id: Spell Id for the patient
        :return: list of dicts
        :rtype: list
        """
        self._cr.execute("""
        SELECT * FROM refused_review_chain WHERE spell_activity_id = {0};
        """.format(spell_activity_id))
        return self._cr.dictfetchall()

    def init(self, cr):
        """
        Create or replace the refused_chain_count table for use in
        get_refusal_episodes

        :param cr: Odoo cursor
        """
        sql_model = self.pool['nh.clinical.sql']
        cr.execute("""
        CREATE OR REPLACE VIEW refused_chain_count AS ({refused_chain_sql});
        CREATE OR REPLACE VIEW refused_review_chain AS ({refused_review});
        """.format(
            refused_chain_sql=sql_model.get_refused_chain_count_sql(),
            refused_review=sql_model.get_refused_review_chain_sql()
        ))

    def get_refusal_events_data(self):
        refusal_episodes = self.get_refusal_episodes(self.spell_activity_id)

        patient_refusal_events_data = []
        for episode in refusal_episodes:
            patient_refusal_event_data = {
                'first_refusal':
                    self.get_first_refusal_column_data(episode),
                'refusals_until_news_obs_taken':
                    self.get_refusals_until_news_obs_taken_column_data(episode),
                'clinical_review':
                    self.get_clinical_review_column_data(episode),
                'clinical_review_frequency_set':
                    self.get_clinical_review_frequency_set_column_data(episode)
            }
            patient_refusal_events_data.append(patient_refusal_event_data)

        return patient_refusal_events_data

    def get_first_refusal_column_data(self, refusal_episode):
        key = 'first_refusal_date_terminated'
        self.validate_refusal_episode_dict_key(refusal_episode, key)

        datetime_utils = self.env['datetime_utils']
        first_refusal_column_data = \
            datetime_utils.reformat_server_datetime_for_frontend(
                refusal_episode[key]
            )
        return first_refusal_column_data

    def get_refusals_until_news_obs_taken_column_data(self, refusal_episode):
        key = 'count'
        self.validate_refusal_episode_dict_key(refusal_episode, key)
        return refusal_episode[key]

    def get_clinical_review_column_data(self, refusal_episode):
        return self.get_task_column_data(refusal_episode,
                                  clinical_review_frequency=False)

    def get_clinical_review_frequency_set_column_data(self, refusal_episode):
        return self.get_task_column_data(refusal_episode,
                                  clinical_review_frequency=True)

    def get_task_column_data(self, refusal_episode,
                             clinical_review_frequency=False):
        self.validate_dict(refusal_episode)

        state_key = 'freq_state' if clinical_review_frequency else \
            'review_state'
        date_terminated_key = 'freq_date_terminated' if \
            clinical_review_frequency else 'review_date_terminated'
        terminate_uid_key = 'freq_terminate_uid' if clinical_review_frequency \
            else 'review_terminate_uid'
        task_name = 'clinical review frequency' if \
            clinical_review_frequency else 'clinical review'

        review_state = refusal_episode[state_key]
        if review_state is None:
            return 'N/A'
        elif review_state == 'started':
            return 'Task in progress'
        elif review_state == 'completed':
            exception_message = \
                "{} task's {} is falsey according to the " \
                "passed refusal episode, this should not be the case " \
                "when the clinical review is completed."

            if not refusal_episode[date_terminated_key]:
                raise ValueError(
                    exception_message.format(task_name.title(),
                                             'date terminated')
                )
            if not refusal_episode[terminate_uid_key]:
                raise ValueError(
                    exception_message.format(task_name.title(),
                                             'terminate uid')
                )

            return {
                'date': refusal_episode[date_terminated_key],
                'by': refusal_episode[terminate_uid_key]
            }
        raise ValueError(
            "Unexpected state '{}' for {} task."
                .format(review_state, task_name.title())
        )

    @classmethod
    def validate_dict(cls, dictionary):
        if not isinstance(dictionary, dict):
            raise TypeError("Argument is not a dictionary.")
        if not dictionary:
            raise ValueError("Argument cannot be falsey.")

    def validate_refusal_episode_dict_key(self, refusal_episode, key):
        self.validate_dict(refusal_episode)
        try:
            if refusal_episode[key] is None:
                raise ValueError(
                    "None is not an acceptable value for the {} key, "
                    "something went wrong.".format(key)
                )
        except KeyError, e:
            e.message += "\nExpected a {} key, " \
                         "check return of SQL view.".format(key)
            raise e
