import logging
import time

from openerp.addons.nh_eobs_mental_health\
    .tests.common.transaction_observation import TransactionObservationCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data

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
        self.spell_model = self.env['nh.clinical.spell']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.pme_reason = pme_reason_model.browse(1)

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

        self.completed_obs = []

    def tearDown(self):
        _logger.info('reverting get_setting')
        self.settings_model._revert_method('get_setting')
        super(TestGetActivitiesRefused, self).tearDown()

    def get_refusal_in_effect(self, obs_list=None, patient_id=None):
        if not obs_list:
            obs_list = []
        if not patient_id:
            patient_id = self.patient_id
        self.get_obs(patient_id)
        for ob in obs_list:
            self.completed_obs.append(self.ews_activity_id)
            self.complete_obs(ob)
            self.get_obs(patient_id)
        _logger.info('Getting activities')
        activities = self.api_pool.get_activities(self.cr, self.user_id, [])
        for activity in activities:
            if activity.get('id') == self.ews_activity_id:
                return activity.get('refusal_in_effect')
        return False

    def test_refused_first_obs(self):
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_refused_no_risk(self):
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.NO_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_refused_low_risk(self):
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.LOW_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_refused_medium_risk(self):
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.MEDIUM_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_refused_high_risk(self):
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.HIGH_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_refused_obs_stop(self):
        """
        Test that refusal not in effect after refusal -> stop obs.
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.HIGH_RISK_DATA,
                clinical_risk_sample_data.REFUSED_DATA
            ]
        )
        wardboard = self.wardboard_model.browse(self.spell_id)
        wardboard.start_obs_stop(
            self.pme_reason, self.spell_id, self.spell_activity_id)
        activities = self.api_pool.get_activities(self.cr, self.user_id, [])
        refusal_in_effect = [
            act.get('refusal_in_effect') for act in activities
            if act.get('id') == self.ews_activity_id]
        self.assertFalse(refusal_in_effect)

    def test_refused_obs_restart(self):
        """
        Test that refusal not in effect after refusal -> stop obs -> restart
        obs.
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.HIGH_RISK_DATA,
                clinical_risk_sample_data.REFUSED_DATA
            ]
        )
        time.sleep(2)
        wardboard = self.wardboard_model.browse(self.spell_id)
        wardboard.start_obs_stop(
            self.pme_reason, self.spell_id, self.spell_activity_id)
        wardboard.end_obs_stop()
        self.get_obs()
        activities = self.api_pool.get_activities(self.cr, self.user_id, [])
        refusal_in_effect = [
            act.get('refusal_in_effect') for act in activities
            if act.get('id') == self.ews_activity_id]
        self.assertFalse(refusal_in_effect[0])

    def test_refused_transfer(self):
        cr, uid = self.cr, self.uid
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.HIGH_RISK_DATA,
                clinical_risk_sample_data.REFUSED_DATA
            ], patient_id=self.patient_2_id
        )
        time.sleep(2)
        self.api_pool.transfer(
            cr, self.adt_id, 'TESTHN002', {'location': 'TESTWARD'})
        self.api_pool.discharge(self.cr, self.adt_id, 'TESTHN001', {})
        placement_id = self.activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.patient_2_id],
                ['state', '=', 'scheduled']
            ]
        )
        self.activity_pool.submit(
            cr, uid, placement_id[0], {'location_id': self.bed_ids[0]}
        )
        self.activity_pool.complete(cr, uid, placement_id[0])
        self.get_obs(self.patient_2_id)
        activities = self.api_pool.get_activities(self.cr, self.user_id, [])
        refusal_in_effect = [
            act.get('refusal_in_effect') for act in activities
            if act.get('id') == self.ews_activity_id]
        self.assertFalse(refusal_in_effect[0])
