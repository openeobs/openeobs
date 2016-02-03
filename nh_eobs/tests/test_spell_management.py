# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from collections import namedtuple
from mock import MagicMock

from openerp.tests.common import SingleTransactionCase


class TestSpellManagement(SingleTransactionCase):

    def setUp(self):
        super(TestSpellManagement, self).setUp()
        self.spellboard_pool = self.registry('nh.clinical.spellboard')

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
        self.spellboard_pool.fetch_patient_id(self.cr, self.uid, data)
        patient_api._revert_method('search')

        self.assertIn('patient_id', data)
        self.assertEqual(data['patient_id'], 47)

    def test_fetch_patient_id_adds_patient_id_false_if_patient_not_found(self):

        patient_api = self.registry('nh.clinical.patient')
        data = {'hospital_number': 'HOSPNUM123'}

        def mock_search_returning_empty_list(*args, **kwargs):
            return []

        patient_api._patch_method('search', mock_search_returning_empty_list)
        self.spellboard_pool.fetch_patient_id(self.cr, self.uid, data)
        patient_api._revert_method('search')

        self.assertIn('patient_id', data)
        self.assertEqual(data['patient_id'], False)

    def test_fetch_patient_id_does_not_change_previous_keys_in_data_dict(self):
        patient_api = self.registry('nh.clinical.patient')
        data = {'hospital_number': 'HOSPNUM123'}

        def mock_search_returning_patient_id(*args, **kwargs):
            return [47]

        patient_api._patch_method('search', mock_search_returning_patient_id)
        self.spellboard_pool.fetch_patient_id(self.cr, self.uid, data)
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


class TestTransferPatientWizard(SingleTransactionCase):

    def setUp(self):
        super(TestTransferPatientWizard, self).setUp()
        self.transfer_wizard = self.registry('nh.clinical.transfer.wizard')
        self.api = self.registry('nh.eobs.api')

        def mock_browse_transfer_wizard(*args, **kwargs):
            """Return mock TransferPatientWizard object."""
            location = namedtuple('Location', ['code'])
            patient = namedtuple('Patient', ['other_identifier'])
            transfer_wizard = namedtuple(
                'TransferWizard', ['patient_id', 'transfer_location_id'])
            bed = location('A')
            patient = patient(2)
            return transfer_wizard(patient, bed)

        self.transfer_wizard._patch_method(
            'browse', mock_browse_transfer_wizard)

    def tearDown(self):
        self.transfer_wizard._revert_method('browse')

    def test_transfer_calls_api_transfer(self):
        cr, uid = self.cr, self.uid
        self.api.transfer = MagicMock(return_value=True)

        result = self.transfer_wizard.transfer(cr, uid, [1], context=None)

        self.assertEqual(result, True)
        self.api.transfer.assert_called_with(
            cr, uid, 2, {'location': 'A'}, context=None)

        del self.api.transfer


class TestDischargePatientWizard(SingleTransactionCase):

    def setUp(self):
        super(TestDischargePatientWizard, self).setUp()
        self.discharge_wizard = self.registry('nh.clinical.discharge.wizard')
        self.api = self.registry('nh.eobs.api')
    
    def test_discharge_calls_api_discharge(self):
        cr, uid = self.cr, self.uid
        self.api.discharge = MagicMock(return_value=True)
	
        def mock_browse_discharge_wizard(*args, **kwargs):
            """Return mock DischargePatientWizard object."""
            patient = namedtuple('Patient', ['other_identifier'])
            discharge_wizard = namedtuple(
                'DischargeWizard', ['patient_id'])
            patient = patient(2)
            return discharge_wizard(patient)

        self.discharge_wizard._patch_method(
            'browse', mock_browse_discharge_wizard)

        result = self.discharge_wizard.discharge(cr, uid, [1], context=None)
	self.discharge_wizard._revert_method('browse')
        
	self.assertEqual(result, True)
        self.assertTrue(self.api.discharge.called)

        del self.api.discharge


class TestCancelAdmitWizard(SingleTransactionCase):

    def setUp(self):
        super(TestCancelAdmitWizard, self).setUp()
        self.visit_wizard = self.registry('nh.clinical.cancel_admit.wizard')
        self.api = self.registry('nh.eobs.api')
    
    def test_cancel_visit_calls_api_cancel_admit(self):
        cr, uid = self.cr, self.uid
        self.api.cancel_admit = MagicMock(return_value=True)
	
        def mock_browse_cancel_visit_wizard(*args, **kwargs):
            """Return mock CancelVisitWizard object."""
            patient = namedtuple('Patient', ['other_identifier'])
            visit_wizard = namedtuple(
                'CancelVisitWizard', ['patient_id'])
            patient = patient(2)
            return visit_wizard(patient)

        self.visit_wizard._patch_method(
            'browse', mock_browse_cancel_visit_wizard)

        result = self.visit_wizard.cancel_admit(cr, uid, [1], context=None)
	self.visit_wizard._revert_method('browse')
        
	self.assertEqual(result, True)
        self.api.cancel_admit.assert_called_with(cr, uid, 2, context=None)

      	del self.api.cancel_admit



