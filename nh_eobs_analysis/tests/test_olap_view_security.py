# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOlapViewSecurity(TransactionCase):
    """
    Test the following security aspects of the OLAP view:
    - it only show data from the wards the user is assigned to
    - it's accessible only by users belonging to 'Senior Manager' and
      'Ward Manager' groups/roles
    - it doesn't show data from any of the other columns in the DB tables
      used to compute the dimensions
    """

    def test_shows_only_data_from_wards_the_user_is_assigned_to(self):
        """
        Test the OLAP view shows only data from wards the user is assigned to.
        """
        pass

    def test_is_accessible_only_by_senior_manager_and_ward_manager(self):
        """
        Test the OLAP view is accessible only be users belonging to
        groups/roles 'Senior Manager' and 'Ward Manager'.
        """
        pass

    def test_shows_only_data_from_columns_used_in_dimensions_computation(self):
        """
        Test the OLAP view doesn't show data stored in any DB tables' columns
        other than the ones actually used for constructing the dimensions.
        """
        pass
