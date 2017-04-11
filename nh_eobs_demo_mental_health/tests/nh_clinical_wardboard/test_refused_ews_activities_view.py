from openerp.tests.common import SingleTransactionCase


class TestRefusedEWSActivities(SingleTransactionCase):
    """
    Test that the refused_ews_activities SQL view is returning the demo data
    correctly
    """

    def setUp(self):
        super(TestRefusedEWSActivities, self).setUp()
        self.cr.execute("SELECT * FROM refused_ews_activities;")
        self.refused_ews = self.cr.dictfetchall()

    def test_single_refused(self):
        """
        Test that the single refused observation is returned and the refused
        boolean is True
        """
        refused_record = \
            self.env.ref('nh_eobs_demo_mental_health.nhc_refused_news_23_0').id
        refused_ews = [ews for ews in self.refused_ews
                       if ews.get('ews_id') == refused_record]
        self.assertTrue(refused_ews)
        self.assertTrue(refused_ews[0].get('refused'))

    def test_refused_partial(self):
        """
        Test that the refused observation that has a partial after it is
        returned and the refused boolean is True
        """
        partial_record = \
            self.env.ref('nh_eobs_demo_mental_health.nhc_partial_news_23_0').id
        partial_ews = [ews for ews in self.refused_ews
                       if ews.get('ews_id') == partial_record]
        self.assertTrue(partial_ews)
        self.assertTrue(partial_ews[0].get('refused'))

    def test_post_refused_full(self):
        """
        Test that the refused observation that has a full after it is
        returned and the refused boolean is False
        """
        partial_record = \
            self.env.ref('nh_eobs_demo_mental_health.nhc_full_news_22_0').id
        partial_ews = [ews for ews in self.refused_ews
                       if ews.get('ews_id') == partial_record]
        self.assertTrue(partial_ews)
        self.assertFalse(partial_ews[0].get('refused'))
