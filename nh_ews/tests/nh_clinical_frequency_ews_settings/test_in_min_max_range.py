# -*- coding: utf-8 -*-
from copy import deepcopy

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestInMinMaxRange(TransactionCase):
    def setUp(self):
        super(TestInMinMaxRange, self).setUp()
        self.settings_model = self.env['nh.clinical.frequencies.ews_settings']
        self.config_model = self.env['ir.config_parameter']

        self.field_names = self.settings_model._get_field_names()
        self.fields_to_be_validated_names = []
        self.create_values = {}
        self.maximum = 3000

        for field_name in self.field_names:
            if 'maximum' in field_name:
                self.create_values[field_name] = self.maximum
            elif 'minimum' in field_name:
                self.create_values[field_name] = 1
            else:
                self.create_values[field_name] = 1500
                self.fields_to_be_validated_names.append(field_name)

    def test_all_fields_are_validated(self):
        validated = []
        for field_name in self.fields_to_be_validated_names:
            create_values = deepcopy(self.create_values)
            create_values[field_name] = self.maximum + 1
            try:
                self.settings_model.create(create_values)
            except ValidationError, e:
                validated.append(e)

        expected = len(self.field_names)
        actual = len(validated)
        self.assertEqual(expected, actual)
