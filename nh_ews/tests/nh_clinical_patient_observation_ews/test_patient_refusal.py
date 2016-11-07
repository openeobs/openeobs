# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.addons.nh_observations import frequencies
from openerp.addons.nh_odoo_fixes.tests.common.datetime_test_utils import DatetimeTestUtils
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestPatientRefusal(TransactionCase):

    def setUp(self):
        super(TestPatientRefusal, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        # nh.eobs.api not available to this module
        self.api_model = self.env['nh.clinical.api']
        self.datetime_test_utils = DatetimeTestUtils()

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
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

        # TODO Should I do `api_model.admit()` here instead of creating obs?

    def test_refusal_with_unknown_clinical_risk(self):
        refused_obs = self.ews_model.get_open_obs_activity(self.patient.id)
        obs_activity_after_refused = self.refuse_open_obs()

        after_refused_frequency = frequencies \
            .PATIENT_REFUSAL_ADJUSTMENTS['Unknown'][0]

        # TODO This is wrong, should be an existing obs with date_terminated
        expected = datetime.strptime(
            self.spell_activity.create_date, DTF
        ) + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_no_clinical_risk(self):
        self.initial_no_risk_obs = \
            self.create_obs(clinical_risk_sample_data.NO_RISK_DATA)
        refused_obs = self.ews_model.get_open_obs_activity(self.patient.id)
        obs_activity_after_refused = self.refuse_open_obs()

        default_frequency = self.ews_model._POLICY['frequencies'][0]
        after_refused_frequency = frequencies\
            .PATIENT_REFUSAL_ADJUSTMENTS['None'][default_frequency][0]

        expected = \
            datetime.strptime(refused_obs.date_terminated, DTF)\
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_low_clinical_risk(self):
        self.initial_low_risk_obs = \
            self.create_obs(clinical_risk_sample_data.LOW_RISK_DATA)
        refused_obs = self.ews_model.get_open_obs_activity(self.patient.id)
        obs_activity_after_refused = self.refuse_open_obs()

        default_frequency = self.ews_model._POLICY['frequencies'][1]
        after_refused_frequency = frequencies \
            .PATIENT_REFUSAL_ADJUSTMENTS['Low'][default_frequency][0]

        expected = \
            datetime.strptime(refused_obs.date_terminated, DTF) \
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_medium_clinical_risk(self):
        self.initial_medium_risk_obs = \
            self.create_obs(clinical_risk_sample_data.MEDIUM_RISK_DATA)
        refused_obs = self.ews_model.get_open_obs_activity(self.patient.id)
        obs_activity_after_refused = self.refuse_open_obs()

        default_frequency = self.ews_model._POLICY['frequencies'][2]
        after_refused_frequency = frequencies \
            .PATIENT_REFUSAL_ADJUSTMENTS['Medium'][default_frequency][0]

        expected = \
            datetime.strptime(refused_obs.date_terminated, DTF) \
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def test_refusal_with_high_clinical_risk(self):
        self.initial_high_risk_obs = \
            self.create_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
        refused_obs = self.ews_model.get_open_obs_activity(self.patient.id)
        obs_activity_after_refused = self.refuse_open_obs()

        default_frequency = self.ews_model._POLICY['frequencies'][3]
        after_refused_frequency = frequencies \
            .PATIENT_REFUSAL_ADJUSTMENTS['High'][default_frequency][0]

        expected = \
            datetime.strptime(refused_obs.date_terminated, DTF) \
            + timedelta(minutes=after_refused_frequency)
        actual = datetime.strptime(
            obs_activity_after_refused.date_scheduled, DTF
        )

        self.datetime_test_utils\
            .assert_datetimes_equal_disregarding_seconds(expected, actual)

    def refuse_open_obs(self):
        obs_activity_current = \
            self.ews_model.get_open_obs_activity(self.patient.id)
        # If no existing obs then create one.
        if len(obs_activity_current) < 1:
            obs_activity_current_activity_id = self.ews_model.create_activity(
                {'date_scheduled': datetime.now()},
                {'patient_id': self.patient.id}
            )
            obs_activity_current = \
                self.activity_model.browse(obs_activity_current_activity_id)
        self.obs_refused_date_scheduled = obs_activity_current.date_scheduled
        self.activity_pool.submit(
            self.env.cr, self.env.uid,
            obs_activity_current.id,
            {
                'is_partial': True,
                'partial_reason': 'refused'
            }
        )
        self.activity_pool.complete(self.cr, self.uid,
                                    obs_activity_current.id)
        return self.ews_model.get_open_obs_activity(self.patient.id)

    def create_obs(self, obs_data):
        self.obs_activity_id = self.ews_model.create_activity(
            {'date_scheduled': datetime.now()},
            {'patient_id': self.patient.id}
        )
        self.activity_pool.submit(self.env.cr, self.env.uid,
                                  self.obs_activity_id,
                                  obs_data)
        self.activity_pool.complete(self.env.cr, self.env.uid,
                                    self.obs_activity_id)
        return self.activity_model.browse(self.obs_activity_id)
