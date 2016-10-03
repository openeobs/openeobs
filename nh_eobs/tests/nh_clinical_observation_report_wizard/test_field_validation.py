# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestFieldValidation(TransactionCase):
    """
    Test that fields on this model are correctly validated.
    """
    def setUp(self):
        super(TestFieldValidation, self).setUp()
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']

    def test_start_time_in_the_future(self):
        with self.assertRaises(ValidationError):
            self.report_wizard_model.create(
                {'start_time': datetime.now() + timedelta(days=1)}
            )

    def test_end_time_in_the_future(self):
        with self.assertRaises(ValidationError):
            self.report_wizard_model.create(
                {'end_time': datetime.now() + timedelta(days=1)}
            )