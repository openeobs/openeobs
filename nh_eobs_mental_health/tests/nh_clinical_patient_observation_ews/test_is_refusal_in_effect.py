from openerp.tests.common import TransactionCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
import logging
import time

_logger = logging.getLogger(__name__)


class TestIsRefusalInEffect(TransactionCase):
    """
    Test that the get_activities method is returning the refusal_in_effect
    column as true for patient's who are currently refusing obs
    """

    def setUp(self):
        super(TestIsRefusalInEffect, self).setUp()
        self.ews_model = self.registry('nh.clinical.patient.observation.ews')
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.get_open_obs()
        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.completed_ews_ids = []

    def get_refusal_in_effect(self, list_of_obs, mode='parent'):
        """
        Complete two obs and then call is_refusal_in_effect

        :param list_of_obs: List of observation value dictionaries
        :param mode: 'child' or 'parent'
        :return: output of is_refusal_in_effect
        """
        for ob in list_of_obs:
            self.test_utils_model.get_open_obs()
            self.completed_ews_ids.append(
                self.test_utils_model.ews_activity.id)
            self.test_utils_model.complete_obs(ob)
        _logger.info('Getting activities')
        return self.ews_model.is_refusal_in_effect(
            self.cr, self.uid, self.test_utils_model.ews_activity.id,
            mode=mode)

    def test_parent_refused_first_obs(self):
        """
        Test that if the patient refuses their first observation then
        refusal_in_effect is set to True using parent mode
        """
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        refused = self.ews_model.is_refusal_in_effect(
            self.cr, self.uid, self.test_utils_model.ews_activity.id)
        self.assertTrue(refused)

    def test_child_refused_first_obs(self):
        """
        Test that if the patient refuses their first observation then
        refusal_in_effect is set to True using child mode
        """
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        refused = self.ews_model.is_refusal_in_effect(
            self.cr, self.uid, self.test_utils_model.ews_activity.id,
            mode='child')
        self.assertTrue(refused)

    def test_parent_refused_after_full(self):
        """
        Test that if the patient refuses and has No clinical risk then
        refusal_in_effect is set to True using parent mode
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.NO_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ]
            )
        )

    def test_parent_partial_after_refused(self):
        """
        Test that if the patient refuses and has partial then
        refusal_in_effect is set to True using parent mode
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.REFUSED_DATA,
                    clinical_risk_sample_data.PARTIAL_DATA_ASLEEP
                ]
            )
        )

    def test_parent_full_after_refused(self):
        """
        Test that if the patient refuses and has partial then
        refusal_in_effect is set to True using parent mode
        """
        self.assertFalse(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.REFUSED_DATA,
                    clinical_risk_sample_data.NO_RISK_DATA
                ]
            )
        )

    def test_child_refused_after_full(self):
        """
        Test that if the patient refuses and has No clinical risk then
        refusal_in_effect is set to True using child mode
        """
        self.assertTrue(
            self.get_refusal_in_effect(
                [
                    clinical_risk_sample_data.NO_RISK_DATA,
                    clinical_risk_sample_data.REFUSED_DATA
                ],
                mode='child'
            )
        )

    def test_child_refused_after_refused(self):
        """
        Test that if the patient refuses and refuses again then
        refusal_in_effect is set to True using child mode
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.REFUSED_DATA,
                clinical_risk_sample_data.REFUSED_DATA
            ]
        )
        first_ews = self.completed_ews_ids[0]
        self.assertTrue(
            self.ews_model.is_refusal_in_effect(
                self.cr, self.uid, first_ews, mode='child')
        )

    def test_child_partial_after_refused(self):
        """
        Test that if the patient refuses and has a partial again then
        refusal_in_effect is set to True using child mode
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.REFUSED_DATA,
                clinical_risk_sample_data.PARTIAL_DATA_ASLEEP
            ]
        )
        first_ews = self.completed_ews_ids[0]
        self.assertTrue(
            self.ews_model.is_refusal_in_effect(
                self.cr, self.uid, first_ews, mode='child')
        )

    def test_child_full_after_refused(self):
        """
        Test that if the patient refuses and has a full obs then
        refusal_in_effect is set to True using child mode
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.REFUSED_DATA,
                clinical_risk_sample_data.NO_RISK_DATA
            ]
        )
        first_ews = self.completed_ews_ids[0]
        self.assertFalse(
            self.ews_model.is_refusal_in_effect(
                self.cr, self.uid, first_ews, mode='child')
        )

    def test_child_two_refusal_episodes(self):
        """
        Test that if the patient refuses and has a full obs then
        refuses again
        refusal_in_effect is set to True using child mode
        """
        self.get_refusal_in_effect(
            [
                clinical_risk_sample_data.REFUSED_DATA,
                clinical_risk_sample_data.NO_RISK_DATA,
                clinical_risk_sample_data.REFUSED_DATA,
                clinical_risk_sample_data.PARTIAL_DATA_ASLEEP
            ]
        )
        first_refusal = self.completed_ews_ids[0]
        second_refusal = self.completed_ews_ids[2]
        self.assertFalse(
            self.ews_model.is_refusal_in_effect(
                self.cr, self.uid, first_refusal, mode='child')
        )
        self.assertTrue(
            self.ews_model.is_refusal_in_effect(
                self.cr, self.uid, second_refusal, mode='child')
        )

    def test_refused_then_pme(self):
        """
        Test that if the patient refuses their first observation then
        have a PME that refusal_in_effect is set to False
        """
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        self.test_utils_model.start_pme()
        refused = self.ews_model.is_refusal_in_effect(
            self.cr, self.uid, self.test_utils_model.ews_activity.id)
        self.assertFalse(refused)

    def test_refused_then_transfer(self):
        """
        Test that if the patient refuses their first observation then
        they are transferred that refusal_in_effect is set to False
        """
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        time.sleep(2)
        self.test_utils_model.transfer_patient('WB')
        refused = self.ews_model.is_refusal_in_effect(
            self.cr, self.uid, self.test_utils_model.ews_activity.id)
        self.assertFalse(refused)
