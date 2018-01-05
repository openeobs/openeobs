# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestUpdateNextObsAfterPartial(TransactionCase):
    """
    Test the `update_next_obs_after_partial` method of the
    `nh.clinical.patient.observation.ews` model.
    """
    def setUp(self):
        super(TestUpdateNextObsAfterPartial, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.config_model = self.env['ir.config_parameter']
        self.high_risk_frequency = 360
        self.config_model.set_param('high_risk', self.high_risk_frequency)

        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
        self.test_utils.get_open_obs()

    def test_new_obs_frequency_after_high_risk_then_refusal(self):
        """
        Consider the following series of events:
          1. Full obs.
          2. Refused obs.
          3. New obs scheduled but not yet completed.

        The new obs at step 3 should have been scheduled using the same
        frequency as the full obs before the refusal as that is the patients
        most recent known clinical risk. The frequency is not altered by the
        refusal in this case.
        """
        expected = self.high_risk_frequency
        actual = self.test_utils.ews_activity.data_ref.frequency
        self.assertEqual(expected, actual)

    def test_new_obs_date_scheduled_after_high_risk_then_refusal(self):
        """
        Consider the following series of events:
          1. Full obs.
          2. Refused obs.
          3. New obs scheduled but not yet completed.

        The new obs at step 3 should have been scheduled using the same
        frequency as the full obs before the refusal as that is the patients
        most recent known clinical risk. The frequency is not altered by the
        refusal in this case.

        :return:
        """
        new_obs_create_date = datetime.strptime(
            self.test_utils.ews_activity.create_date, DTF)
        expected = new_obs_create_date \
            + timedelta(minutes=self.high_risk_frequency)
        actual = \
            datetime.strptime(self.test_utils.ews_activity.date_scheduled, DTF)
        self.assertEqual(expected, actual)
