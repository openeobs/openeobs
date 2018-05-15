from openerp.addons.nh_ews.tests.common.clinical_risk_sample_data \
    import LOW_RISK_DATA
from openerp.osv.osv import except_osv
from openerp.tests.common import SavepointCase


class TestApiComplete(SavepointCase):

    def setUp(self):
        super(TestApiComplete, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.ews_activity = self.test_utils_model._get_open_obs(
            self.patient.id, 'nh.clinical.patient.observation.ews'
        )

        self.api_model = self.env['nh.eobs.api']

    def call_test(self, user, activity_id=None, data=None):
        activity_id = activity_id or self.ews_activity.id
        data = data or LOW_RISK_DATA
        self.api_model.sudo(user).complete(activity_id, data)

    def test_hca_can_complete_news_obs(self):
        self.call_test(self.hca)

    def test_nurse_can_complete_news_obs(self):
        self.call_test(self.nurse)

    def test_shift_coordinator_can_complete_news_obs(self):
        shift_coordinator = self.test_utils_model.create_shift_coordinator()
        self.call_test(shift_coordinator)

    def test_shift_coordinator_can_complete_height_obs(self):
        shift_coordinator = self.test_utils_model.create_shift_coordinator()
        height_obs_model = self.env['nh.clinical.patient.observation.height']
        activity_id = height_obs_model.create_activity(
            {},
            {
                'patient_id': self.patient.id
            }
        )
        self.call_test(
            shift_coordinator, activity_id=activity_id, data={'height': 1.7}
        )

    def test_doctor_can_complete_news_obs(self):
        self.call_test(self.doctor)

    def test_senior_manager_cannot_complete_news_obs(self):
        with self.assertRaises(except_osv):
            senior_manager = self.test_utils_model.create_senior_manager()
            self.call_test(senior_manager)
