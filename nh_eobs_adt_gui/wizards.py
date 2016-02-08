"""Defines wizards used by ADT GUI operations."""
from datetime import datetime as dt

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TransferPatientWizard(osv.TransientModel):
    """Wizard for transferring a patient."""
    _name = 'nh.clinical.transfer.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
        'transfer_location_id': fields.many2one(
            'nh.clinical.location', 'Transfer Location')
    }

    def transfer(self, cr, uid, ids, context=None):
        """
        Button called by view_transfer_wizard view to transfer
        patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.transfer(
            cr, uid, record.patient_id.other_identifier,
            {'location': record.transfer_location_id.code}, context=context
        )
        return result


class DischargePatientWizard(osv.TransientModel):
    """Wizard for discharging a patient."""
    _name = 'nh.clinical.discharge.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
    }

    def discharge(self, cr, uid, ids, context=None):
        """
        Button called by view_discharge_wizard view to discharge
        patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.discharge(
            cr, uid, record.patient_id.other_identifier,
            {'discharge_date': dt.now().strftime(dtf)}, context=context
        )
        return result


class CancelAdmitPatientWizard(osv.TransientModel):
    """Wizard for cancelling the admission of a patient."""
    _name = 'nh.clinical.cancel_admit.wizard'
    _columns = {
        'patient_id': fields.many2one(
            'nh.clinical.patient', 'Patient', required=True),
        'nhs_number': fields.char('NHS Number', size=200),
        'ward_id': fields.many2one('nh.clinical.location', 'Current Ward'),
        'transfer_location_id': fields.many2one(
            'nh.clinical.location', 'Transfer Location')
    }

    def cancel_admit(self, cr, uid, ids, context=None):
        """
        Button called by view_cancel_transfer_wizard to cancel the
        admissions of a patient.
        """
        api = self.pool['nh.eobs.api']
        record = self.browse(cr, uid, ids, context=context)

        result = api.cancel_admit(
            cr, uid, record.patient_id.other_identifier, context=context
        )
        return result

