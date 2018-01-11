# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestUpdateNextObsAfterPartial(TransactionCase):
    """
    Test that :method:`update_next_obs_after_partial` correctly sets
    `frequency` and `date_scheduled` based on the previous observation and
    whether or not it was refused.
    """
    def setUp(self):
        super(TestUpdateNextObsAfterPartial, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.create_patient_and_spell()
        self.test_utils_model.copy_instance_variables(self)
        self.activity_model = self.env['nh.activity']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.activity_obs_1_high_risk = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell.id,
                clinical_risk_sample_data.HIGH_RISK_DATA
            )
        self.activity_obs_2_partial = \
            self.ews_model.get_open_obs_activity(self.spell_activity.id)

    def test_next_obs_has_same_frequency_as_partial(self):
        self.activity_obs_3_new = \
            self.test_utils_model.complete_open_obs_as_partial(
                self.patient.id, self.spell_activity.id,
                'patient_away_from_bed'
            )
        self.assertEqual(self.activity_obs_2_partial.data_ref.frequency,
                         self.activity_obs_3_new.data_ref.frequency)

    def test_next_obs_has_same_date_scheduled_as_partial(self):
        self.activity_obs_3_new = \
            self.test_utils_model.complete_open_obs_as_partial(
                self.patient.id, self.spell_activity.id,
                'patient_away_from_bed'
            )
        expected_date_scheduled = \
            datetime.strptime(self.activity_obs_2_partial.date_scheduled, DTF)
        actual_date_scheduled = \
            datetime.strptime(self.activity_obs_3_new.date_scheduled, DTF)

        self.assertEqual(expected_date_scheduled, actual_date_scheduled)
