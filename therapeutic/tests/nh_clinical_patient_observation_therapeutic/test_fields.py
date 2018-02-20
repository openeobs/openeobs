# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestFields(TransactionCase):

    def test_has_location_field(self):
        self.assertFalse(True)

    def test_has_one_to_one_field(self):
        self.assertFalse(True)

    def test_has_notes_field(self):
        self.assertFalse(True)

    def test_location_field_valid_values(self):
        expected_values = [
            'Configured value 1',
            'Configured value 2',
            'Location unknown'
        ]
        self.assertFalse(True)

    def test_one_to_one_field_valid_values(self):
        expected_values = [
            'Starting one-to-one',
            'Ending one-to-one',
            'Starting one-to-one remaining within arms reach',
            'Ending one-to-one remaining within arms reach'
        ]
        self.assertFalse(True)
