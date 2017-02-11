# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestGetFormDescription(SingleTransactionCase):

    def setUp(self):
        super(TestGetFormDescription, self).setUp()
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        self.neuro_test_model = \
            self.env['nh.clinical.test.neurological.common']
        self.form_description = self.neuro_model.get_form_description(None)

    def test_has_fields(self):
        form_description_field_names = \
            [field.get('name') for field in self.form_description]
        all_fields = self.neuro_test_model.get_all_fields()
        field_names = self.neuro_test_model.get_field_names(all_fields)

        form_description_field_names_set = set(form_description_field_names)
        field_names_set = set(field_names)

        self.assertTrue(
            field_names_set.issubset(form_description_field_names_set)
        )

    def test_mandatory_keys_on_fields(self):
        mandatory_field_names = \
            self.neuro_test_model.get_mandatory_field_names()
        form_description_mandatory_fields = \
            [field for field in self.form_description
             if field.get('name') in mandatory_field_names]

        self.assertEqual(len(form_description_mandatory_fields),
                         len(mandatory_field_names))

    def test_eyes_selection(self):
        expected = self.neuro_model._eyes_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'eyes']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_verbal_selection(self):
        expected = self.neuro_model._verbal_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'verbal']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_motor_selection(self):
        expected = self.neuro_model._motor_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] == 'motor']

        self.assertEqual(len(actual), 1)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_pupil_size_selection(self):
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
        pupil_reaction_fields = self.neuro_test_model.get_pupil_reaction_fields()
        pupil_reaction_fields_names = \
            self.neuro_test_model.get_field_names(pupil_reaction_fields)

        expected = self.neuro_model._pupil_reaction_selection
        actual = [field['selection'] for field in self.form_description
                  if field['name'] in pupil_reaction_fields_names]

        self.assertEqual(len(actual), 2)
        actual = actual[0]

        self.assertEqual(expected, actual)

    def test_limb_movement_selection(self):
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
        all_fields = self.neuro_test_model.get_all_fields()
        expected = self.neuro_test_model.get_field_labels(all_fields)
        actual = [field['label'] for field in self.form_description
                  if 'label' in field]

        self.assertTrue(all([field in actual for field in expected]))

    def test_contains_only_obs_fields_and_meta(self):
        field_utils = self.env['nh.clinical.patient.observation.field_utils']
        all_fields = self.neuro_test_model.get_all_fields()
        obs_fields = [field for field in all_fields
                      if field_utils.is_obs_field(field)]
        expected = self.neuro_test_model.get_field_names(obs_fields)
        expected.append('meta')
        actual = \
            [field['name'] for field in self.form_description]

        self.assertEqual(sorted(expected), sorted(actual))