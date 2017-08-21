# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestWrite(TransactionCase):

    def setUp(self):
        super(TestWrite, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_and_register_patient()
        self.test_utils.create_locations()
        self.test_utils.copy_instance_variables(self)
        self.ward = self.test_utils.ward
        self.register = self.test_utils.register

        self.spellboard_model = self.env['nh.clinical.spellboard']
        self.start_date = '2017-06-01 10:00:00'

    def call_test(self, start_date=None):
        if start_date is None:
            start_date = self.start_date
        values = {
            'location_id': self.ward.id,
            'start_date': start_date,
            'registration': self.register.id
        }
        self.spellboard = self.spellboard_model.create(values)

    def test_admission_date_updated_when_no_existing_admission_date(self):
        self.call_test()
        self.assertEqual(self.start_date, self.spellboard.start_date)

        self.new_start_date = '2017-07-01 10:00:00'
        self.spellboard.start_date = self.new_start_date
        self.assertEqual(self.new_start_date, self.spellboard.start_date)

    def test_admission_date_updated_when_existing_admission_date(self):
        initial_start_date = '2017-12-01 10:00:00'
        self.call_test(start_date=initial_start_date)
        self.assertEqual(initial_start_date, self.spellboard.start_date)

        self.new_start_date = '2017-07-01 10:00:00'
        self.spellboard.start_date = self.new_start_date
        self.assertEqual(self.new_start_date, self.spellboard.start_date)
