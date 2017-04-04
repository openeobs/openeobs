# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestSelectReason(TransactionCase):
    """
    Tests methods in :class:`PatientMonitoringExceptionSelectReason
    <nh_eobs_mental_health.wizard
    .nh_clinical_patient_monitoring_exception.reason>`.
    """
    def setUp(self):
        super(TestSelectReason, self).setUp()
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']
        self.obs_stop_model = \
            self.env['nh.clinical.pme.obs_stop']
        self.reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']

    def test_creates_obs_stop_record(self):
        pme_count_before = self.obs_stop_model.search_count([])
        self.wizard_model.start_patient_monitoring_exception()
        pme_count_after = self.obs_stop_model.search_count([])
        self.assertEquals(pme_count_before + 1, pme_count_after)

    def test_raises_exception_when_no_reason(self):
        no_reason = self.wizard_model.create({})
        with self.assertRaises(ValueError):
            no_reason.start_obs_stop()

    def test_raises_exception_when_more_than_one_reason(self):
        reason_one = self.reason_model.create({'display_text': 'reason one'})
        reason_two = self.reason_model.create({'display_text': 'reason two'})
        multiple_reasons = self.wizard_model.create({
            'reasons': [reason_one, reason_two]
        })
        with self.assertRaises(ValueError):
            multiple_reasons.start_obs_stop()

    def test_creates_activity(self):
        domain = [
            ('data_model', '=', 'nh.clinical.pme.obs_stop'),
            ('state', '=', 'started')
        ]
        activity_count_before = self.obs_stop_model.search_count(domain)
        self.obs_stop_model.start_patient_monitoring_exception()
        activity_count_after = self.obs_stop_model.search_count(domain)
        self.assertEquals(activity_count_before + 1, activity_count_after)
