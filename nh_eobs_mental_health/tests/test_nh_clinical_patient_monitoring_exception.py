# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from openerp.tests.common import TransactionCase
from openerp.tools.misc import mute_logger


class TestNhClinicalPatientMonitoringException(TransactionCase):
    """
    Test the nh.clinical.patient_monitoring_exception model.
    """
    def setUp(self):
        super(TestNhClinicalPatientMonitoringException, self) \
            .setUp()
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']
        self.select_reason_model = self.env['nh.clinical.patient_monitoring_exception.select_reason']

    @mute_logger('openerp.sql_db')
    def test_cannot_create_without_a_reason(self):
        """
        Test that a patient monitoring exception record cannot be created
        without a reason.
        :return:
        """
        with self.assertRaises(IntegrityError):
            self.pme_model.create({})
