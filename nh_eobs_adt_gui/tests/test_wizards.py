from collections import namedtuple
from mock import MagicMock

from openerp.tests.common import SingleTransactionCase


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

