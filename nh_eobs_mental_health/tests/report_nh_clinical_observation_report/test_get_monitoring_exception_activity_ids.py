# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetMonitoringExceptionActivityIds(TransactionCase):

    def setUp(self):
        super(TestGetMonitoringExceptionActivityIds, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.activity_model = self.env['nh.activity']

        self.obs_stop_ids = []
        self.rapid_tranq_ids = []

        obs_stop_1_activity = self.test_utils.create_activity_obs_stop()
        self.obs_stop_ids.append(obs_stop_1_activity.id)
        obs_stop_1_activity.data_ref.start(obs_stop_1_activity.id)
        rapid_tranq_1_activity = self.test_utils.create_activity_rapid_tranq()
        self.rapid_tranq_ids.append(rapid_tranq_1_activity.id)
        rapid_tranq_1_activity.data_ref.start(rapid_tranq_1_activity.id)
        rapid_tranq_2_activity = self.test_utils.create_activity_rapid_tranq()
        self.rapid_tranq_ids.append(rapid_tranq_2_activity.id)
        rapid_tranq_2_activity.data_ref.start(rapid_tranq_2_activity.id)
        rapid_tranq_2_activity.data_ref.complete(rapid_tranq_2_activity.id)
        obs_stop_1_activity.data_ref.complete(obs_stop_1_activity.id)
        rapid_tranq_1_activity.data_ref.complete(rapid_tranq_1_activity.id)

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.pme_ids = self.report_model\
            .get_patient_monitoring_exception_activity_ids(
                self.spell_activity.id)

    def test_returns_obs_stop_ids(self):
        issubset = set(self.obs_stop_ids).issubset(set(self.pme_ids))
        self.assertTrue(issubset)

    def test_returns_rapid_tranq_ids(self):
        issubset = set(self.rapid_tranq_ids).issubset(set(self.pme_ids))
        self.assertTrue(issubset)

    def test_correct_number_of_pmes_in_total(self):
        expected = len(self.rapid_tranq_ids + self.obs_stop_ids)
        actual = len(self.pme_ids)
        self.assertEqual(expected, actual)
