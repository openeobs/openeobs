# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestMyDashboard(TransactionCase):
    """
    Test the following aspect of the 'My Dashboard' view
    - It should allow the user to save the filtered dataset of the OLAP
      view to the 'My Dashboard' view.
    """

    # TODO - there is just a pass here
    def test_OLAP_view_is_saved_to_my_dashboard(self):
        """
        Test that My Dashboard saves the filtered dataset of OLAP.
        """
        self.assertTrue(False)
