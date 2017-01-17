from openerp.tests.common import SingleTransactionCase
import copy


class TestGetAcuityGroups(SingleTransactionCase):
    """
    Test the get_acuity_groups method overriden to include the new columns for
    EOBS-404
    """

    def setUp(self):
        super(TestGetAcuityGroups, self).setUp()
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.expected_states = {
            'NoScore': True,
            'High': True,
            'Medium': True,
            'Low': True,
            'None': True,
            'ObsStop': True,
            'Refused': True
        }

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
        groups = self.wardboard_model._get_acuity_groups([], [])
        self.assertEqual(groups[0], expected_groups)

    def test_folded_state_no_ids(self):
        """
        Make sure all groups are folded
        """
        groups = self.wardboard_model._get_acuity_groups([], [])
        for key, value in self.expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_noscore(self):
        """
        Make sure only the new patient / obs restart group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['NoScore'] = False
        groups = self.wardboard_model._get_acuity_groups(['NoScore'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_none(self):
        """
        Make sure only the no risk group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['None'] = False
        groups = self.wardboard_model._get_acuity_groups(['None'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_low(self):
        """
        Make sure only the low risk group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['Low'] = False
        groups = self.wardboard_model._get_acuity_groups(['Low'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_medium(self):
        """
        Make sure only the medium group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['Medium'] = False
        groups = self.wardboard_model._get_acuity_groups(['Medium'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_high(self):
        """
        Make sure only the high group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['High'] = False
        groups = self.wardboard_model._get_acuity_groups(['High'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_obs_stop(self):
        """
        Make sure only the medium group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['ObsStop'] = False
        groups = self.wardboard_model._get_acuity_groups(['ObsStop'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_refused(self):
        """
        Make sure only the medium group is unfolded
        """
        expected_states = copy.deepcopy(self.expected_states)
        expected_states['Refused'] = False
        groups = self.wardboard_model._get_acuity_groups(['Refused'], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)

    def test_folded_state_all_ids(self):
        """
        Make sure only the medium group is unfolded
        """
        expected_states = {
            'NoScore': False,
            'High': False,
            'Medium': False,
            'Low': False,
            'None': False,
            'ObsStop': False,
            'Refused': False
        }
        groups = self.wardboard_model._get_acuity_groups(
            [
                'NoScore',
                'High',
                'Medium',
                'Low',
                'None',
                'ObsStop',
                'Refused'
            ], [])
        for key, value in expected_states.iteritems():
            self.assertEqual(groups[1][key], value)
