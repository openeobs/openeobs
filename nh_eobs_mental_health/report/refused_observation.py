# -*- coding: utf-8 -*-
from datetime import datetime

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
        report_data['patient_refusal_events'] = \
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
        """
        Get a dictionary containing all the information necessary to populate
        the 'Patient Refusal Events Data' section of the observation report.

        :return:
        :rtype: dict
        """
        refusal_episodes = self.get_refusal_episodes(self.spell_activity_id)

        patient_refusal_events_data = []
        for episode in refusal_episodes:
            patient_refusal_event_data = {
                'first_refusal':
                    self.get_first_refusal_column_data(episode),
                'refusals_until_news_obs_taken':
                    self.get_refusals_until_news_obs_taken_column_data(
                        episode),
                'clinical_review':
                    self.get_clinical_review_column_data(episode),
                'clinical_review_frequency_set':
                    self.get_clinical_review_frequency_set_column_data(episode)
            }
            patient_refusal_events_data.append(patient_refusal_event_data)
        return self.sort_patient_refusal_events_data(
            patient_refusal_events_data
        )

    def sort_patient_refusal_events_data(self, patient_refusal_events_data):
        datetime_utils = self.env['datetime_utils']
        datetime_format = datetime_utils.format_string.format(
            datetime_utils.date_format, datetime_utils.time_format
        )

        def get_sort_key(patient_refusal_event):
            return datetime.strptime(patient_refusal_event['first_refusal'],
                                     datetime_format)

        patient_refusal_events_data = sorted(patient_refusal_events_data,
                                             key=get_sort_key, reverse=True)
        return patient_refusal_events_data


    def get_first_refusal_column_data(self, refusal_episode):
        """
        Get the data necessary to populate the 'First Refusal' column of the
        'Patient Refusal Events Data' section of the observation report.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :return:
        :rtype: dict
        """
        key = 'first_refusal_date_terminated'
        self.validate_refusal_episode_dict_key(refusal_episode, key)

        datetime_utils = self.env['datetime_utils']
        first_refusal_column_data = \
            datetime_utils.reformat_server_datetime_for_frontend(
                refusal_episode[key], date_first=True
            )
        return first_refusal_column_data

    def get_refusals_until_news_obs_taken_column_data(self, refusal_episode):
        """
        Get the data necessary to populate the 'Refusals Until News Obs Taken'
        column of the 'Patient Refusal Events Data' section of the observation
        report.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :return:
        :rtype: dict
        """
        key = 'count'
        self.validate_refusal_episode_dict_key(refusal_episode, key)
        return refusal_episode[key]

    def get_clinical_review_column_data(self, refusal_episode):
        """
        Get the data necessary to populate the 'Clinical Review' column of the
        'Patient Refusal Events Data' section of the observation report.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :return:
        :rtype: dict
        """
        return self.get_task_column_data(refusal_episode,
                                         clinical_review_frequency=False)

    def get_clinical_review_frequency_set_column_data(self, refusal_episode):
        """
        Get the data necessary to populate the 'Clinical Review Frequency Set'
        column of the 'Patient Refusal Events Data' section of the observation
        report.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :return:
        :rtype: dict
        """
        return self.get_task_column_data(refusal_episode,
                                         clinical_review_frequency=True)

    def get_task_column_data(self, refusal_episode,
                             clinical_review_frequency=False):
        """
        Generic method that can get the necessary data for multiple different
        columns that display information about different types of task.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :param clinical_review_frequency: Indicates whether to create a
        clinical_review_frequency task or something else. This only works
        because there is currently only 2 different types of task created by
        this method.
        :type clinical_review_frequency: bool
        :return:
        """
        self.validate_dict(refusal_episode)

        # Setup differently depending on task type.
        state_key = 'freq_state' if clinical_review_frequency else \
            'review_state'
        date_terminated_key = 'freq_date_terminated' if \
            clinical_review_frequency else 'review_date_terminated'
        terminate_uid_key = 'freq_terminate_uid' if clinical_review_frequency \
            else 'review_terminate_uid'
        task_name = 'clinical review frequency' if \
            clinical_review_frequency else 'clinical review'

        # Determine what to return.
        review_state = refusal_episode[state_key]
        if review_state is None:
            return 'N/A'
        elif review_state == 'new':
            return 'Task in progress'
        elif review_state == 'completed':
            # Check values to be used on the report are valid.
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
            # Get formatted date of task completion.
            datetime_utils = self.env['datetime_utils']
            date_terminated = datetime_utils\
                .reformat_server_datetime_for_frontend(
                    refusal_episode[date_terminated_key], date_first=True
                )
            # Get name of user who completed task.
            user_model = self.env['res.users']
            user_id = refusal_episode[terminate_uid_key]
            user = user_model.browse(user_id)
            return {
                'date_terminated': date_terminated,
                'user_id': user.name
            }
        raise ValueError(
            "Unexpected state '{}' for {} task.".format(
                review_state, task_name.title())
        )

    @classmethod
    def validate_dict(cls, dictionary):
        """
        Validate that a passed argument is a dictionary that is not empty.

        :param dictionary:
        :return: No return, raises if invalid.
        """
        if not isinstance(dictionary, dict):
            raise TypeError("Argument is not a dictionary.")
        if not dictionary:
            raise ValueError("Argument cannot be falsey.")

    def validate_refusal_episode_dict_key(self, refusal_episode, key):
        """
        Validate that a 'refusal episode' dictionary has the desired key and
        that the key does not have a value of None.

        :param refusal_episode: Raw data from the database.
        :type refusal_episode: dict
        :param key: Key to be validated.
        :type key: str
        :return:
        """
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
