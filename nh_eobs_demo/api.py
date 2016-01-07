# coding=utf-8
import logging
from datetime import datetime

from faker import Faker
from openerp.osv import orm, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

_logger = logging.getLogger(__name__)

fake = Faker()


class nh_eobs_demo_loader(orm.AbstractModel):
    """Discharges Patients."""
    _name = 'nh.eobs.demo.loader'

    def discharge_patients(self, cr, uid, ward_code, amount, context=None):
        api_demo = self.pool['nh.clinical.api.demo']

        # get the hospital numbers of placed patients in a particular ward
        hospital_numbers = self._get_patient_hospital_numbers_by_ward(
            cr, uid, ward_code, context=context
        )

        # find patients who are placed in ward with clinical risk 0... To do.

        # set the discharge date
        discharge_date = datetime.now().strftime(dtf)
        data = {'discharge_date': discharge_date}

        # select the patients to discharge
        patients_to_discharge = hospital_numbers[:amount]

        # discharge patients
        patients = api_demo.discharge_patients(
            cr, uid, patients_to_discharge, data, context=context)

        return patients

    def transfer_patients(self, cr, uid, ward_codes, amount, context=None):
        pass

    def _get_patient_hospital_numbers_by_ward(self, cr, uid, ward_code, context=None):
        location_pool = self.pool['nh.clinical.location']
        patient_pool = self.pool['nh.clinical.patient']

        # get the location_ids by ward code
        location_id = location_pool.get_by_code(
            cr, uid, ward_code, context=context
        )
        # get patients who are placed in a ward (i.e. in a bed)
        patient_ids = patient_pool.search(
            cr, uid, [('current_location_id', 'child_of', location_id)],
            context=context
        )
        # get the hospital numbers of patients
        hospital_numbers = []
        patients = patient_pool.browse(cr, uid, patient_ids, context=context)
        for patient in patients:
            hospital_numbers.append(patient.other_identifier)

        return hospital_numbers




