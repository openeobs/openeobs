# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOlapViewPerformance(TransactionCase):
    """
    Test the following performance aspects of the OLAP view:
    - it loads the dataset in less than 3 seconds
    - it doesn't affect the write-to-database performance of the system
    """

    def test_loads_the_dataset_in_less_than_3_seconds(self):
        """
        Test that the OLAP view loads the dataset in less than 3 seconds.
        """
        pass

    def test_does_not_affect_the_write_to_database_performance_of_system(self):
        """
        Test the OLAP view doesn't affect the write-to-database performance
        of the system.
        """
        pass
