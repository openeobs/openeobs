# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestPatientRefusal(TransactionCase):
    """
    Verify correct behaviour after a patient refusal is created. Currently the
    only affect refusals have is that they cap the maximum frequency of the
    next observation that is scheduled which this class tests.

    They also add some UI elements but that is not tested here.
    """
    def setUp(self):
        """
        Set up the test environment.
        """
        super(TestPatientRefusal, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        # nh.eobs.api not available to this module
        self.api_model = self.env['nh.clinical.api']
        self.frequencies_model = \
            self.env['nh.clinical.frequencies.ews']
        self.datetime_test_utils = self.env['datetime_test_utils']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier',
            'other_identifier': 'an_other_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)

        # Fails in spell.get_patient_by_id() if not started.
        self.activity_pool.start(self.env.cr, self.env.uid,
                                 self.spell_activity_id)

        self.spell = self.spell_activity.data_ref

        self.test_utils_model = self.env['nh.clinical.test_utils']

    def test_refusal_with_unknown_clinical_risk(self):
        """
        A patient with unknown clinical risk who refuses has their next
        observation scheduled as expected.
        """
        datetime_utils = self.env['datetime_utils']
        refused_time = datetime_utils.get_current_time(
            as_string=True)
        obs_activity_after_refused = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        expected_after_refused_frequency = \
            self.frequencies_model.get_unknown_risk_refusal_frequency()

        expected = datetime.strptime(
            refused_time, DTF
        ) + timedelta(minutes=expected_after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_no_clinical_risk(self):
        """
        A patient with no clinical risk who refuses has their next
        observation scheduled as expected.
        """
        self.initial_no_risk_obs_activity = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.NO_RISK_DATA
            )
        obs_activity_before_refused = self.ews_model.get_open_obs_activity(
            self.spell_activity_id)
        obs_activity_after_refused = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        expected_after_refused_frequency = \
            self.frequencies_model.get_risk_frequency('no')

        expected = datetime.strptime(
            obs_activity_before_refused.date_terminated, DTF
        ) + timedelta(minutes=expected_after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_low_clinical_risk(self):
        """
        A patient with low clinical risk who refuses has their next
        observation scheduled as expected.
        """
        self.initial_low_risk_obs_activity = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.LOW_RISK_DATA
            )
        obs_activity_before_refused = self.ews_model.get_open_obs_activity(
            self.spell_activity_id)
        obs_activity_after_refused = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        expected_after_refused_frequency = \
            self.frequencies_model.get_risk_frequency('low')

        expected = datetime.strptime(
            obs_activity_before_refused.date_terminated, DTF
        ) + timedelta(minutes=expected_after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_medium_clinical_risk(self):
        """
        A patient with medium clinical risk who refuses has their next
        observation scheduled as expected.
        """
        self.initial_medium_risk_obs_activity = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )
        obs_activity_before_refused = self.ews_model.get_open_obs_activity(
            self.spell_activity_id)
        obs_activity_after_refused = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        expected_after_refused_frequency = \
            self.frequencies_model.get_risk_frequency('medium')

        expected = datetime.strptime(
            obs_activity_before_refused.date_terminated, DTF
        ) + timedelta(minutes=expected_after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_high_clinical_risk(self):
        """
        A patient with high clinical risk who refuses has their next
        observation scheduled as expected.
        """
        self.initial_high_risk_obs_activity = \
            self.test_utils_model.create_and_complete_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.HIGH_RISK_DATA
            )
        obs_activity_before_refused = self.ews_model.get_open_obs_activity(
            self.spell_activity_id)
        obs_activity_after_refused = self.test_utils_model.refuse_open_obs(
            self.patient.id, self.spell_activity_id
        )

        expected_after_refused_frequency = \
            self.frequencies_model.get_risk_frequency('high')

        expected = datetime.strptime(
            obs_activity_before_refused.date_terminated, DTF
        ) + timedelta(minutes=expected_after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)
