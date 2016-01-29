# coding=utf-8
from mock import MagicMock
from collections import namedtuple

from openerp.tests.common import SingleTransactionCase


class TestSpellManagement(SingleTransactionCase):

    def setUp(self):
        super(TestSpellManagement, self).setUp()
        self.spellboard_pool = self.registry('nh.clinical.spellboard')

    def test_transfer_button_returns_correct_action(self):
        cr, uid = self.cr, self.uid
        self.spellboard_pool._update_context = MagicMock()
        action = self.spellboard_pool.transfer_button(cr, uid, [1])

        self.assertEquals(action['name'], 'Transfer Patient')

        del self.spellboard_pool._update_context

    def test_update_context_updates_with_patient_id_and_location_id(self):
        cr, uid = self.cr, self.uid

        def mock_browse_spell_board(*args, **kwargs):
            """Returns mock NHClinicalSpellboard object."""
            location = namedtuple('Location', ['id'])
            patient = namedtuple('Patient', ['id'])
            spell_board = namedtuple(
                'SpellBoard', ['patient_id', 'location_id'])
            bed = location(1)
            patient = patient(2)
            return spell_board(bed, patient)

        context = {'name': 'me'}
        self.spellboard_pool._patch_method('browse', mock_browse_spell_board)
        context = self.spellboard_pool._update_context(cr, uid, [2], context)
        self.spellboard_pool._revert_method('browse')

        self.assertEqual(context['default_patient_id'], 1)
        self.assertEqual(context['default_location_id'], 2)


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

