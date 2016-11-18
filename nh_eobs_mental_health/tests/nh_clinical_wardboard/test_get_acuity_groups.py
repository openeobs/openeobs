from openerp.tests.common import SingleTransactionCase


class TestGetAcuityGroups(SingleTransactionCase):
    """
    Test the get_acuity_groups method overriden to include the new columns for
    EOBS-404
    """

    def setUp(self):
        super(TestGetAcuityGroups, self).setUp()
        wardboard_model = self.env['nh.clinical.wardboard']
        self.groups = wardboard_model._get_acuity_groups(0, [])

    def test_groups_returned(self):
        """
        Make sure that the new groups are returned
        """
        expected_groups = [
            ('NoScore', 'New Pt / Obs Restart'),
            ('High', 'High Risk'),
            ('Medium', 'Medium Risk'),
            ('Low', 'Low Risk'),
            ('None', 'No Risk'),
            ('ObsStop', 'Obs Stop'),
            ('Refused', 'Refused')
        ]
        self.assertEqual(self.groups[0], expected_groups)

    def test_folded_state(self):
        """
        Make sure none of the groups are folded
        """
        expected_states = \
            {
                'NoScore': False,
                'High': False,
                'Medium': False,
                'Low': False,
                'None': False,
                'ObsStop': False,
                'Refused': False
            }
        for key, value in expected_states.iteritems():
            self.assertEqual(self.groups[1][key], value)
