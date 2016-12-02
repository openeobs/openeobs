from openerp.addons.nh_eobs_mental_health\
    .tests.common.transaction_observation import TransactionObservationCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
import logging

_logger = logging.getLogger(__name__)


class TestGetActivitiesRefused(TransactionObservationCase):
    """
    Test that the get_activities method is returning the refusal_in_effect
    column as true for patient's who are currently refusing obs
    """

    def setUp(self):
        _logger.info('Setting up TestGetActivitiesRefused')
        super(TestGetActivitiesRefused, self).setUp()
        self.settings_model = self.registry('nh.clinical.settings')

        def patch_settings_activity_period(*args, **kwargs):
            _logger.info('inside patch of get settings')
            if len(args) > 3 and args[3] == 'activity_period':
                _logger.info('Returning a day')
                return 1440
            _logger.info('Returning origin method')
            return patch_settings_activity_period.origin(*args, **kwargs)

        _logger.info('patching get_setting')
        self.settings_model._patch_method(
            'get_setting', patch_settings_activity_period)

    def tearDown(self):
        _logger.info('reverting get_setting')
        self.settings_model._revert_method('get_setting')
        super(TestGetActivitiesRefused, self).tearDown()

    def get_refusal_in_effect(self, obs_data):
        _logger.info('Completing first obs')
        self.complete_obs(obs_data)
        self.get_obs()
        _logger.info('Completing refused obs')
        self.complete_obs(clinical_risk_sample_data.REFUSED_DATA)
        self.get_obs()
        _logger.info('Getting activities')
        activities = self.api_pool.get_activities(self.cr, self.user_id, [])
        for activity in activities:
            if activity.get('id') == self.ews_activity_id:
                return activity.get('refusal_in_effect')
        return False

    def test_refused_first_obs(self):
        """
        Test that if the patient refuses their first observation then
        refusal_in_effect is set to True
        """
        self.complete_obs(clinical_risk_sample_data.REFUSED_DATA)
        activities = self.api_pool.get_activities(
            self.cr, self.user_id, [self.patient_id])
        self.assertTrue(activities[1].get('refusal_in_effect'))

    def test_refused_no_risk(self):
        """
        Test that if the patient refuses and has No clinical risk then
        refusal_in_effect is set to True
        """
        self.assertTrue(
            self.get_refusal_in_effect(clinical_risk_sample_data.NO_RISK_DATA))

    def test_refused_low_risk(self):
        """
        Test that if the patient refuses and has Low clinical risk then
        refusal_in_effect is set to True
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                clinical_risk_sample_data.LOW_RISK_DATA))

    def test_refused_medium_risk(self):
        """
        Test that if the patient refuses and has Medium clinical risk then
        refusal_in_effect is set to True
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                clinical_risk_sample_data.MEDIUM_RISK_DATA))

    def test_refused_high_risk(self):
        """
        Test that if the patient refuses and has High clinical risk then
        refusal_in_effect is set to True
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                clinical_risk_sample_data.HIGH_RISK_DATA))
