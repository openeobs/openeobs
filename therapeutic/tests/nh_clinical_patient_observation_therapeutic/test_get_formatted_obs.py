from openerp.tests.common import SavepointCase


class TestGetFormattedObs(SavepointCase):

    def setUp(self):
        super(TestGetFormattedObs, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

    def call_test(self, one_to_one_intervention_needed_value=None):
        therapeutic_model = \
            self.env['nh.clinical.patient.observation.therapeutic']

        creation_values = {
            'patient_id': self.patient.id,
            'patient_status': 'AW'
        }
        if one_to_one_intervention_needed_value is not None:
            creation_values['one_to_one_intervention_needed'] = \
                one_to_one_intervention_needed_value
        therapeutic_obs = therapeutic_model.create(creation_values)

        formatted_ob = therapeutic_obs.get_formatted_obs()[0]
        self.actual = formatted_ob['one_to_one_intervention_needed']

    def test_one_to_one_intervention_needed_set_to_yes(self):
        expected = True
        self.call_test(one_to_one_intervention_needed_value=expected)
        self.assertEqual(expected, self.actual)

    def test_one_to_one_intervention_needed_set_to_no(self):
        expected = False
        self.call_test(one_to_one_intervention_needed_value=expected)
        self.assertEqual(expected, self.actual)

    def test_one_to_one_intervention_needed_not_submitted(self):
        expected = None
        self.call_test(one_to_one_intervention_needed_value=expected)
        self.assertEqual(expected, self.actual)
