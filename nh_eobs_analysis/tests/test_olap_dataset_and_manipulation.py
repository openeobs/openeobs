# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOlapDatasetAndManipulation(TransactionCase):
    """
    Test the dataset & manipulation functionality of the OLAP view
    - It should aggregate the data in the dimensions
    - It should allow for filtering on the dimensions and the period of time
      being analysed
    - It should only show data from the wards the user is assigned to
    - It should only show data within the last 8 days
    - It should only show scheduled and completed observations
    - It should allow the user to reduce the time period under analyse to
      the last 48 hours
    """

    def test_aggregates_data_in_dimensions(self):
        """
        Test that the OLAP view aggregates the data in the dimensions
        """
        pass

    def test_filters_dataset_on_dimensions(self):
        """
        Test that the OLAP view allows to filter the data set via the
        dimensions
        """
        pass

    def test_filters_dataset_on_time_period(self):
        """
        Test that the OLAP view allows to filter the data set via the time
        period
        """
        pass

    def test_filters_dataset_on_ward_assignment_of_user(self):
        """
        Test that the OLAP view filters the dataset to only show the wards the
        user is assigned to
        """
        pass

    def test_filters_dataset_to_show_last_eight_days(self):
        """
        Test that the OLAP view filters the dataset to only show the last 8
        days
        """
        pass

    def test_only_shows_scheduled_and_completed_observations(self):
        """
        Test that the OLAP view only contains data for scheduled and completed
        observations
        """
        pass

    def test_filters_dataset_for_last_48_hours(self):
        """
        Test that the OLAP view filters the dataset on the last 48 hours
        """
        pass
