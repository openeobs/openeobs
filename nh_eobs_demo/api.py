# coding=utf-8
import logging
import random
from datetime import datetime

from faker import Faker
from openerp.osv import orm, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

_logger = logging.getLogger(__name__)

fake = Faker()


class nh_eobs_demo_loader(orm.AbstractModel):
    """Defines methods for loading data for demonstration purposes."""
    _name = 'nh.eobs.demo.loader'

    def discharge_patients(self, cr, uid, ward_code, amount, context=None):
        """
        Discharges a given number of patients from a chosen ward,
        returning the hospital numbers of the patients successfully
        discharged.
        """
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

    def transfer_patients(self, cr, uid, origin_ward, destination_ward, amount,
                          context=None):
        """
        Transfers a given number of patients from an origin ward to a
        destination ward, returning the hospital numbers of the
        patients successfully transferred.
        """
        api_demo = self.pool['nh.clinical.api.demo']

        # get the hospital numbers of placed patients in a particular ward
        hospital_numbers = self._get_patient_hospital_numbers_by_ward(
            cr, uid, origin_ward, context=context
        )

        # get the available bed locations in to_location ward
        available_beds = self._get_available_beds_in_ward(
            cr, uid, destination_ward, context=context
        )

        # select the patients to transfer
        patients_to_transfer = hospital_numbers[:amount]

        # transfer_patients
        patients = api_demo.transfer_patients(
            cr, uid, patients_to_transfer, available_beds, context=context
        )

        return patients

    def simulate_news_for_ward(self, cr, uid, ward_code, days, context=None):
        # for each patient in ward ...
        # simulate news for patient
        pass

    def _simulate_news_for_patient(self, cr, uid, patient_id, context=None):
        # get nurse and hca user_ids
        # select a user_id randomly
        pass

    def _take_news_for_patient(self, cr, uid, hospital_number, context=None):
        # get user responsible for patient take news observation
        pass

    def _get_nurse_hca_user_ids(self, cr, uid):
        """Gets nurse and hca nurse ids."""
        group_pool = self.pool['res.groups']
        user_pool = self.pool['res.users']
        # only HCA and nurse users submit/complete obs
        group_ids = group_pool.search(
            cr, uid, [['name', 'in', [
                    'NH Clinical Nurse Group', 'NH Clinical HCA Group']]]
        )
        user_ids = user_pool.search(
            cr, uid, [['groups_id', 'in', group_ids]])
        return user_ids

    def _get_random_user_id(self, cr, uid, user_ids):
        """Gets randomly a user_id from a list of user_ids."""
        return random.choice(user_ids)

    def _get_patient_hospital_numbers_by_ward(self, cr, uid, ward_code,
                                              context=None):
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

    def _get_available_beds_in_ward(self, cr, uid, ward_code, context=None):
        location_pool = self.pool['nh.clinical.location']
        ward_id = location_pool.search(
            cr, uid, [('code', '=', ward_code)], context=context)

        bed_ids = location_pool.search(
            cr, uid, [('parent_id', 'in', ward_id),
                      ('is_available', '=', True)],
            context=context
        )
        beds = location_pool.browse(cr, uid, bed_ids, context=context)
        codes = [bed.code for bed in beds]
        return codes






