# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from collections import namedtuple

from mock import MagicMock
from openerp.exceptions import ValidationError
from openerp.tests.common import SingleTransactionCase


class TestSpellManagement(SingleTransactionCase):

    def setUp(self):
        super(TestSpellManagement, self).setUp()
        self.spellboard_pool = self.registry('nh.clinical.spellboard')
        self.spellboard_model = self.env['nh.clinical.spellboard']
        self.test_utils = self.env['nh.clinical.test_utils']

    def test_fetch_patient_id_adds_patient_id_to_data_dict_if_found_it(self):

        patient_api = self.registry('nh.clinical.patient')
        data = {'hospital_number': 'HOSPNUM123'}

        def mock_search_returning_patient_id(*args, **kwargs):
            """
            Return a list containing an integer,
            to mock the returning value of the actual Odoo method
            when a patient is searched and found.
            """
            return [47]

        patient_api._patch_method('search', mock_search_returning_patient_id)
        self.spellboard_model.fetch_patient_id(data)
        patient_api._revert_method('search')

        self.assertIn('patient_id', data)
        self.assertEqual(data['patient_id'], 47)

    def test_fetch_patient_id_adds_patient_id_false_if_patient_not_found(self):

        patient_api = self.registry('nh.clinical.patient')
        data = {'hospital_number': 'HOSPNUM123'}

        def mock_search_returning_empty_list(*args, **kwargs):
            return []

        patient_api._patch_method('search', mock_search_returning_empty_list)
        self.spellboard_model.fetch_patient_id(data)
        patient_api._revert_method('search')

        self.assertIn('patient_id', data)
        self.assertEqual(data['patient_id'], False)

    def test_fetch_patient_id_does_not_change_previous_keys_in_data_dict(self):
        patient_api = self.registry('nh.clinical.patient')
        data = {'hospital_number': 'HOSPNUM123'}

        def mock_search_returning_patient_id(*args, **kwargs):
            return [47]

        patient_api._patch_method('search', mock_search_returning_patient_id)
        self.spellboard_model.fetch_patient_id(data)
        patient_api._revert_method('search')

        self.assertIn('hospital_number', data)
        self.assertEqual(data['hospital_number'], 'HOSPNUM123')

    def test_fetch_patient_id_not_adds_patient_id_to_data_dict_if_empty(self):
        patient_api = self.registry('nh.clinical.patient')
        data = {}

        def mock_search_returning_patient_id(*args, **kwargs):
            return [47]

        patient_api._patch_method('search', mock_search_returning_patient_id)
        self.spellboard_pool.fetch_patient_id(self.cr, self.uid, data)
        patient_api._revert_method('search')

        self.assertNotIn('patient_id', data)

    def test_transfer_button_returns_correct_action(self):
        cr, uid = self.cr, self.uid
        self.spellboard_pool._update_context = MagicMock()
        action = self.spellboard_pool.transfer_button(cr, uid, [1])

        self.assertEquals(action['name'], 'Transfer Patient')

        del self.spellboard_pool._update_context

    def test_update_context_updates_with_patient_id_and_context_id(self):
        cr, uid = self.cr, self.uid

        def mock_browse_spell_board(*args, **kwargs):
            """Returns mock NHClinicalSpellboard object."""
            ward = namedtuple('Ward', ['id'])
            patient = namedtuple('Patient', ['id'])
            spell_board = namedtuple(
                'SpellBoard', ['patient_id', 'ward_id', 'nhs_number'])
            bed = ward(1)
            patient = patient(2)
            return spell_board(bed, patient, 'nhsnum1')

        context = {'name': 'me'}
        self.spellboard_pool._patch_method('browse', mock_browse_spell_board)
        context = self.spellboard_pool._update_context(cr, uid, [2], context)
        self.spellboard_pool._revert_method('browse')

        self.assertEqual(context['default_patient_id'], 1)
        self.assertEqual(context['default_ward_id'], 2)
        self.assertEqual(context['default_nhs_number'], 'nhsnum1')

    def test_name_field_value_is_patient_full_name(self):
        """
        The 'name' field is used in the UI for various elements. When viewing
        the register data we want to see the name of the patient the register
        concerns.
        """
        self.test_utils.create_locations()
        self.test_utils.create_and_register_patient()

        self.spellboard_model = self.env['nh.clinical.spellboard']
        spellboard = self.spellboard_model.create({
            'registration': self.test_utils.register.id,
            'location_id': self.test_utils.bed.id
        })
        expected = 'Testersen, Test'
        actual = spellboard.display_name

        self.assertEqual(expected, actual)

    def test_handles_registration_activity_already_created(self):
        self.test_utils.create_locations()
        self.test_utils.create_and_register_patient()

    def test_creates_registration_activity_if_it_doesnt_already_exist(self):
        self.test_utils.create_locations()
        register_model = self.env['nh.clinical.adt.patient.register']
        registration = register_model.create({
            'other_identifier': 'HOS001',
            'given_name': 'Given',
            'family_name': 'Family'
        })

        activity_model = self.env['nh.activity']
        data_ref = '{},{}'.format(register_model._name, registration.id)
        domain = [('data_ref', '=', data_ref)]
        registration_activity_search_results_before = \
            activity_model.search(domain)
        self.assertFalse(registration_activity_search_results_before)

        self.spellboard_model.create({
            'registration': registration.id,
            'location_id': self.test_utils.bed.id
        })

        registration_activity_search_results_after = \
            activity_model.search(domain)
        self.assertTrue(registration_activity_search_results_after)

    def test_returns_friendly_error_if_registration_not_already_created(self):
        """
        Spellboard records cannot be created without an existing registration
        to reference (`registration` is a required field). A friendly error
        message should be returned explaining this is a valid registration ID
        is not passed at creation.
        """
        self.test_utils.create_locations()
        with self.assertRaises(ValidationError) as error:
            self.spellboard_model.create({
                'location_id': self.test_utils.bed.id
            })
        expected = "Missing required field registration. A registration " \
                   "must be created first!"
        actual = error.exception.value
        self.assertEqual(expected, actual)
