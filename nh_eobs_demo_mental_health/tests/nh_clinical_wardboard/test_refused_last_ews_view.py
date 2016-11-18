from openerp.tests.common import SingleTransactionCase


class TestRefusedLastEWS(SingleTransactionCase):
    """
    Test that the refused_last_ews SQL view is returning the demo data
    correctly
    """

    def setUp(self):
        super(TestRefusedLastEWS, self).setUp()
        self.cr.execute("SELECT * FROM refused_last_ews;")
        self.refused_ews = self.cr.dictfetchall()

    def test_refused_patient(self):
        """
        Test that the single refused observation is returned and the refused
        boolean is True
        """
        refused_ews = [ews for ews in self.refused_ews
                       if ews.get('spell_id') == 23]
        self.assertTrue(refused_ews)
        self.assertTrue(refused_ews[0].get('refused'))

    def test_full_patient(self):
        """
        Test that the refused observation that has a full after it is
        returned and the refused boolean is False
        """
        partial_ews = [ews for ews in self.refused_ews
                       if ews.get('spell_id') == 22]
        self.assertTrue(partial_ews)
        self.assertFalse(partial_ews[0].get('refused'))
