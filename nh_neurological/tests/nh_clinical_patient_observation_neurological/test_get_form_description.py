# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestGetFormDescription(SingleTransactionCase):
    """Test getting of the form description dictionary."""
    def setUp(self):
        super(TestGetFormDescription, self).setUp()
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        self.neuro_test_model = \
            self.env['nh.clinical.test.neurological.common']
        self.form_description = self.neuro_model.get_form_description(None)

    def test_has_fields(self):
        """
        Form description contains an entry for all the observation fields.
        """
        form_description_field_names = \
            [field.get('name') for field in self.form_description]
        all_fields = self.neuro_test_model.get_all_obs_fields()
        field_names = self.neuro_test_model.get_field_names(all_fields)

        form_description_field_names_set = set(form_description_field_names)
        field_names_set = set(field_names)

        self.assertTrue(
            field_names_set.issubset(form_description_field_names_set)
        )

    def test_mandatory_keys_on_fields(self):
        """
        Form description has a 'mandatory' key for each field item.
        """
        mandatory_field_names = \
            self.neuro_test_model.get_mandatory_field_names()
        form_description_mandatory_fields = \
            [field for field in self.form_description
             if field.get('name') in mandatory_field_names]

        self.assertEqual(len(form_description_mandatory_fields),
                         len(mandatory_field_names))

    def test_eyes_selection(self):
        """
        Eyes field item in the form description has a selection key with a
        value equal to the selection defined on the Odoo field.
        """
        expected = self.neuro_model._eyes_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'eyes']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_verbal_selection(self):
        """
        Verbal field item in the form description has a selection key with a
        value equal to the selection defined on the Odoo field.
        """
        expected = self.neuro_model._verbal_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'verbal']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_motor_selection(self):
        """
        Motor field item in the form description has a selection key with a
        value equal to the selection defined on the Odoo field.
        """
        expected = self.neuro_model._motor_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'motor']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_pupil_size_selection(self):
        """
        Pupil size field items in the form description has a selection key with
        a value equal to the selection defined on the Odoo field.
        """
        pupil_size_fields = self.neuro_test_model.get_pupil_size_fields()
        pupil_size_field_names = \
            self.neuro_test_model.get_field_names(pupil_size_fields)

        expected = self.neuro_model._pupil_size_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] in pupil_size_field_names]

        self.assertEqual(len(actual), 2)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_pupil_reaction_selection(self):
        """
        Pupil reaction field items in the form description has a selection key
        with a value equal to the selection defined on the Odoo field.
        """
        pupil_reaction_fields = \
            self.neuro_test_model.get_pupil_reaction_fields()
        pupil_reaction_fields_names = \
            self.neuro_test_model.get_field_names(pupil_reaction_fields)

        expected = self.neuro_model._pupil_reaction_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] in pupil_reaction_fields_names]

        self.assertEqual(len(actual), 2)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_limb_movement_selection(self):
        """
        Limb movement field items in the form description has a selection key
        with a value equal to the selection defined on the Odoo field.
        """
        limb_movement_fields = self.neuro_test_model.get_limb_movement_fields()
        limb_movement_field_names = \
            self.neuro_test_model.get_field_names(limb_movement_fields)

        expected = self.neuro_model._limb_movement_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] in limb_movement_field_names]

        self.assertEqual(len(actual), 4)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_labels(self):
        """
        Each field item in the form description has a 'label' entry equal to
        the one defined on the Odoo field.
        """
        all_fields = self.neuro_test_model.get_all_obs_fields()
        expected = self.neuro_test_model.get_field_labels(all_fields)
        actual = [field['label'] for field in self.form_description
                  if 'label' in field]

        self.assertTrue(all([field in actual for field in expected]))

    def test_contains_only_obs_fields_and_meta(self):
        """
        Form description contains only field items and a 'meta' item.
        """
        field_utils = self.env['nh.clinical.field_utils']
        all_fields = self.neuro_test_model.get_all_obs_fields()
        obs_fields = [field for field in all_fields
                      if field_utils.is_obs_field(field)]
        expected = self.neuro_test_model.get_field_names(obs_fields)
        expected.append('meta')
        actual = \
            [field['name'] for field in self.form_description]

        self.assertEqual(sorted(expected), sorted(actual))

    def test_field_order(self):
        """
        Order of field items in form description is the same as the order of
        the form `_required` class variable.
        """
        expected = self.neuro_model.get_obs_field_order()
        actual = [field['name'] for field in self.form_description]
        self.assertTrue(expected, actual)

    def test_form_description_meta_has_parital_flow_key(self):
        """
        Form description `meta` item has a `partial_flow` key.
        """
        meta_dict = [item for item in self.form_description
                     if item.get('type') == 'meta']
        self.assertTrue(len(meta_dict) is 1)

        meta_dict = meta_dict[0]
        self.assertTrue('partial_flow' in meta_dict)

    def test_partial_flow_key_has_value_score(self):
        """
        The `partial_flow` key has a value of `score`.
        """
        meta_dict = [item for item in self.form_description
                     if item.get('type') == 'meta']
        self.assertTrue(len(meta_dict) is 1)
        meta_dict = meta_dict[0]

        partial_flow = meta_dict.get('partial_flow')
        self.assertEqual('score', partial_flow)
