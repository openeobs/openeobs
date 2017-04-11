# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_observations import frequencies
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestPatientRefusalAfterPatientMonitoringException(TransactionCase):

    def setUp(self):
        super(TestPatientRefusalAfterPatientMonitoringException, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()

        self.nurse = self.test_utils_model.nurse
        self.spell_activity_id = self.test_utils_model.spell_activity_id

        self.env.uid = self.nurse.id
        self.patient_id = self.test_utils_model.patient.id

        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.patient = self.patient_model.browse(self.patient_id)
        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.datetime_test_utils = self.env['datetime_test_utils']

    def test_obs_after_refusal_due_in_one_hour(self):
        reason_one = self.reason_model.create({'display_text': 'reason one'})
        self.wardboard.start_patient_monitoring_exception(
            reason_one,
            self.spell_activity.data_ref.id,
            self.spell_activity_id
        )
        self.wardboard.end_patient_monitoring_exception()

        refused_obs = \
            self.ews_model.get_open_obs_activity(self.spell_activity_id)
        obs_activity_after_refused = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        after_refused_frequency = \
            frequencies.PATIENT_REFUSAL_ADJUSTMENTS['Obs Restart'][0]

        expected = \
            datetime.strptime(refused_obs.date_terminated, DTF) \
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils \
            .assert_datetimes_equal_disregarding_seconds(expected, actual)
