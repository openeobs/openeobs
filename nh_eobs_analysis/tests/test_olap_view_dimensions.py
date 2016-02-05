# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOlapViewDimensions(TransactionCase):
    """
    Test the following dimensions for the OLAP view
    - Who the observation was taken by
    - The date the observation was scheduled
    - The date the observation was carried out
    - The location the observation was carried out at
    - The ward the observation was carried out in
    - The activity that triggered the observation
      (patient placed, a previous observation)
    - The score that was calculated from the observation values
    - The clinical risk determined by the observation values
    - Indication if the observation was carried out on time or not
    - The number of minutes overdue (delayed) the observation was completed
    - The number of minutes early the observation was completed
    - The type of staff that completed the observation (HCA, Nurse)
    - The reason a partial observation was submitted
    - The previous clinical risk for the patient at the time the observation
      was taken
    - The previous score for the patient at the time the observation was taken
    - Indication if the patient's score increased after the observation was
      taken
    - Indication if the patient's score decreased after the observation was
      taken
    - Indication if the patient's score stayed the same after observation was
      taken
    """

    def setUp(self):
        super(TestOlapViewDimensions, self).setUp()
        self.olap = self.registry('nh.eobs.news.report')

    def test_has_dimension_who_the_observation_was_taken_by(self):
        """
        Test that the OLAP view has a dimension for who took the observation
        """
        self.assertTrue('user_id' in self.olap, 'User ID not in OLAP model')

    def test_has_dimension_date_the_observation_was_scheduled(self):
        """
        Test that the OLAP view has a dimension for the date the observation
        was scheduled
        """
        self.assertTrue('date_scheduled' in self.olap,
                        'Date Scheduled not in OLAP model')

    def test_has_dimension_date_the_observation_was_carried_out(self):
        """
        Test that the OLAP view has a dimension for the date the observation
        was completed
        """
        self.assertTrue('date_terminated' in self.olap,
                        'Date Terminated not in OLAP model')

    def test_has_dimension_ward_the_observation_was_carried_out_in(self):
        """
        Test that the OLAP view has a dimension for the ward that the
        observation was carried out in
        """
        self.assertTrue('ward_id' in self.olap, 'Ward ID not in OLAP model')
    #
    # def test_has_dimension_type_activity_that_triggered_observation(self):
    #     """
    #     Test that the OLAP view has a dimension for the type of the activity
    #     that triggered the observation
    #     """
    #     self.assertTrue('type' in self.olap,
    # 'Trigger Type not in OLAP model')

    def test_has_dimension_observation_clinical_risk(self):
        """
        Test that the OLAP view has a dimension for the clinical risk that
        was assigned based on the early warning score
        """
        self.assertTrue('clinical_risk' in self.olap,
                        'Current Clinical Risk not in OLAP model')

    def test_has_dimension_observation_was_carried_out_on_time(self):
        """
        Test that the OLAP view has a dimension for indicating if the
        observation was carried out on time or not
        """
        self.assertTrue('on_time' in self.olap,
                        'On time flag not in OLAP model')

    def test_has_dimension_number_of_minutes_overdue(self):
        """
        Test that the OLAP view has a dimension indicating the number of
        minutes that the observation was overdue by
        """
        self.assertTrue('delay' in self.olap,
                        'Minutes Overdue not in OLAP model')

    def test_has_dimension_number_of_minutes_early(self):
        """
        Test that the OLAP view has a dimension indicating the number of
        minutes the observation was completed early by
        """
        self.assertTrue('minutes_early' in self.olap,
                        'Minutes Early not in OLAP model')

    def test_has_dimension_type_of_staff_completed_observation(self):
        """
        Test that the OLAP view has a dimension indicating the type of staff
        that completed the observation (HCA, Nurse)
        """
        self.assertTrue('staff_type' in self.olap,
                        'Staff Type not in OLAP model')
    #
    # def test_has_dimension_reason_a_partial_observation(self):
    #     """
    #     Test that the OLAP view has a dimension for the reason why a partial
    #     observation was completed if the observation was a partial one
    #     """
    #     self.assertTrue('partial_reason' in self.olap,
    #                     'Partial Reason not in OLAP model')

    def test_has_dimension_score_for_previous_observation(self):
        """
        Test that the OLAP view has a dimension for the early warning score
        of the patient's previous observation
        """
        self.assertTrue('previous_score' in self.olap,
                        'Previous EWS not in OLAP model')

    def test_has_dimension_patient_score_increased(self):
        """
        Test that the OLAP view has a dimension indicating if the current
        observation score is higher than the patient's previous observation
        score
        """
        self.assertTrue('trend_up' in self.olap, 'Trend Up not in OLAP model')

    def test_has_dimension_patient_score_decreased(self):
        """
        Test that the OLAP view has a dimension indicating if the current
        observation score is lower than the patient's previous observation
        score
        """
        self.assertTrue('trend_down' in self.olap,
                        'Trend Down not in OLAP model')

    def test_has_dimension_patient_score_same(self):
        """
        Test that the OLAP view has a dimension indicating if the current
        observation score is the same as the patient's previous observation
        score
        """
        self.assertTrue('trend_same' in self.olap,
                        'Trend Same not in OLAP model')
