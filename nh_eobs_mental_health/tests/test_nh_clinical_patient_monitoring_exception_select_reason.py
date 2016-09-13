# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNhClinicalPatientMonitoringExceptionSelectReason(TransactionCase):
    """
    Tests methods in :class:`PatientMonitoringExceptionSelectReason
    <nh_eobs_mental_health.wizard
    .nh_clinical_patient_monitoring_exception.reason>`.
    """
    def setUp(self):
        super(TestNhClinicalPatientMonitoringExceptionSelectReason, self)\
            .setUp()
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']
        self.pme_model = \
            self.env['nh.clinical.patient_monitoring_exception']
        self.reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']

    def test_creates_patient_monitoring_exception_record(self):
        pme_count_before = self.pme_model.search_count([])
        self.wizard_model.create_patient_monitoring_exception()
        pme_count_after = self.pme_model.search_count([])
        self.assertEquals(pme_count_before + 1, pme_count_after)

    def test_raises_exception_when_no_reason(self):
        no_reason = self.wizard_model.create({})
        with self.assertRaises(ValueError):
            no_reason.start_patient_monitoring_exception()

    def test_raises_exception_when_more_than_one_reason(self):
        reason_one = self.reason_model.create({'display_text': 'reason one'})
        reason_two = self.reason_model.create({'display_text': 'reason two'})
        multiple_reasons = self.wizard_model.create({
            'reasons': [reason_one, reason_two]
        })
        with self.assertRaises(ValueError):
            multiple_reasons.start_patient_monitoring_exception()

    def test_creates_activity(self):
        domain = [
            ('data_model', '=', 'nh.clinical.patient_monitoring_exception'),
            ('state', '=', 'started')
        ]
        activity_count_before = self.pme_model.search_count(domain)
        self.pme_model.create_patient_monitoring_exception()
        activity_count_after = self.pme_model.search_count(domain)
        self.assertEquals(activity_count_before + 1, activity_count_after)
