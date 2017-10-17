# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.tools.misc import mute_logger
from psycopg2 import IntegrityError


class TestReasonRequired(TransactionCase):
    """
    Test the nh.clinical.patient_monitoring_exception.obs_stop model.
    """
    def setUp(self):
        super(TestReasonRequired, self) \
            .setUp()
        self.obs_stop_model = self.env['nh.clinical.pme.obs_stop']

    @mute_logger('openerp.sql_db')
    def test_cannot_create_without_a_reason(self):
        """
        Test that a patient monitoring exception record cannot be created
        without a reason.
        """
        with self.assertRaises(IntegrityError):
            self.obs_stop_model.create({})
