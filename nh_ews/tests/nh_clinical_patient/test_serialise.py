from openerp.tests.common import SavepointCase


class TestSerialiseBase(SavepointCase):

    def setUp(self):
        super(TestSerialiseBase, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)


class TestSerialiseTrend(TestSerialiseBase):

    def call_test(self, obs_risks, expected_trend):
        for risk in obs_risks:
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id,
                self.spell.id,
                risk=risk
            )

        patient_dict = self.patient.serialise()[0]
        actual_trend = patient_dict['ews_trend']

        self.assertEqual(expected_trend, actual_trend)

    def test_low_then_high_risk_obs(self):
        self.call_test(obs_risks=['low', 'high'], expected_trend='up')

    def test_low_then_high_risk_obs_followed_by_partial(self):
        self.call_test(
            obs_risks=['low', 'high', 'partial'], expected_trend='up'
        )


class TestSerialiseScore(TestSerialiseBase):

    def call_test(self, obs_risks, expected_score):
        for risk in obs_risks:
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id,
                self.spell.id,
                risk=risk
            )

        patient_dict = self.patient.serialise()[0]
        actual_score = patient_dict['ews_score']

        self.assertEqual(expected_score, actual_score)

    def test_low_then_high_obs(self):
        self.call_test(obs_risks=['low', 'high'], expected_score=10)

    def test_low_then_high_then_partial_obs(self):
        self.call_test(obs_risks=['low', 'high', 'partial'], expected_score=10)
