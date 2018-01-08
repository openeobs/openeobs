# -*- coding: utf-8 -*-
from copy import deepcopy

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestInMinMaxRange(TransactionCase):
    """
    Test the `in_min_max_range` method on the
    `nh.clinical.frequencies.ews_settings` model.
    """
    def setUp(self):
        super(TestInMinMaxRange, self).setUp()
        self.settings_model = self.env['nh.clinical.frequencies.ews_settings']
        self.config_model = self.env['ir.config_parameter']
        self.field_utils = self.env['nh.clinical.field_utils']

        self.field_names = self.field_utils.get_field_names(self.settings_model)
        self.fields_to_be_validated_names = \
            self.field_utils.get_field_names_to_validate(self.settings_model)
        self.create_values = {}
        self.maximum = 3000

        for field_name in self.field_names:
            if 'maximum' in field_name:
                self.create_values[field_name] = self.maximum
            elif 'minimum' in field_name:
                self.create_values[field_name] = 1
            else:
                self.create_values[field_name] = 1500

    def test_all_fields_are_validated(self):
        """
        Test that all the fields on this model that need to be validated are
        in fact validated.

        This is done by making all the fields that should be validated invalid
        one by one and checking that a ValidationError is raised.
        """
        validated = []
        for field_name in self.fields_to_be_validated_names:
            create_values = deepcopy(self.create_values)
            create_values[field_name] = self.maximum + 1
            try:
                self.settings_model.create(create_values)
            except ValidationError, e:
                validated.append(e)

        expected = len(self.fields_to_be_validated_names)
        actual = len(validated)
        self.assertEqual(expected, actual)
