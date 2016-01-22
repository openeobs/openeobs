# coding=utf-8
import logging
import random

from datetime import datetime as dt, timedelta as td
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
        patient_pool = self.pool['nh.clinical.patient']
        location_pool = self.pool['nh.clinical.location']

        # get the hospital numbers of placed patients in a particular ward
        hospital_numbers = self._get_hospital_numbers_by_ward_not_placed(
            cr, uid, ward_code, context=context
        )

        # select the patients to discharge
        random.shuffle(hospital_numbers)
        patients_to_discharge = hospital_numbers[:amount]

        # place patients
        patient_ids = patient_pool.search(cr, uid, [(
            'other_identifier', 'in', patients_to_discharge)]
        )
        location_id = location_pool.search(cr, uid, [('code', '=', ward_code)])
        api_demo.place_patients(cr, uid, patient_ids, location_id)

        # submit observations
        self.complete_first_ews_for_placed_patients(
            cr, uid, patient_ids
        )

        # set the discharge date
        discharge_date = dt.now().strftime(dtf)
        data = {'discharge_date': discharge_date}

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

        # get the available bed location in destination ward
        available_beds = self._get_available_beds_in_ward(
            cr, uid, destination_ward, context=context
        )

        # select the patients to transfer
        random.shuffle(hospital_numbers)
        patients_to_transfer = hospital_numbers[:amount]

        # transfer_patients
        patients = api_demo.transfer_patients(
            cr, uid, patients_to_transfer, available_beds, context=context
        )

        return patients

    def complete_first_ews_for_placed_patients(self, cr, uid, patient_ids,
                                               context=None):
        """Completes observations for placed patients in order to
        schedule further observations"""

        activity_pool = self.pool['nh.activity']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']

        ews_data = {
            'respiration_rate': 15,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'avpu_text': 'A',
            'pulse_rate': 65,
            'body_temperature': 37.5,
        }

        nurse_hca_uids = self._get_nurse_hca_user_ids(cr, uid)

        for patient_id in patient_ids:
            taker_uid = self._get_random_user_id(cr, uid, nurse_hca_uids)

            ews_activity_id = ews_pool.create_activity(
                cr, taker_uid, {}, {'patient_id': patient_id}, context=context)
            activity_pool.submit(
                cr, taker_uid, ews_activity_id, ews_data, context=context)
            activity_pool.complete(cr, taker_uid, ews_activity_id,
                                   context=context)
            _logger.info("EWS observation '%s' made", ews_activity_id)

            # set complete date
            complete_date = dt.now() - td(hours=12)
            activity_pool.write(
                cr, uid, ews_activity_id,
                {'date_terminated': complete_date.strftime(dtf)},
                context=context)

            # get frequency of triggered ews
            triggered_ews_id = activity_pool.search(cr, uid, [
                ['creator_id', '=', ews_activity_id],
                ['data_model', '=', 'nh.clinical.patient.observation.ews']
                ], context=context)

            if not triggered_ews_id:
                osv.except_osv('Error!',
                               'The NEWS observation was not triggered '
                               'after previous submission!')

            triggered_ews = activity_pool.browse(
                cr, uid, triggered_ews_id[0], context=context)

            # set scheduled date
            scheduled_date = complete_date + td(
                minutes=triggered_ews.data_ref.frequency)
            activity_pool.write(
                cr, uid, triggered_ews_id[0],
                {'date_scheduled': scheduled_date.strftime(dtf)},
                context=context)

            activity_pool.submit(
                cr, taker_uid, triggered_ews_id[0], ews_data, context=context)
            activity_pool.complete(cr, taker_uid, triggered_ews_id[0],
                                   context=context)
            _logger.info("EWS observation '%s' made", triggered_ews_id[0])

        return True

    def _get_nurse_hca_user_ids(self, cr, uid):
        """Gets nurse and hca nurse ids."""
        group_pool = self.pool['res.groups']
        user_pool = self.pool['res.users']
        # only HCA and nurse users submit/complete obs
        group_ids = group_pool.search(
            cr, uid, [['name', 'in',
                       ['NH Clinical Nurse Group', 'NH Clinical HCA Group']]])
        user_ids = user_pool.search(
            cr, uid, [['groups_id', 'in', group_ids]])
        return user_ids

    def _get_random_user_id(self, cr, uid, user_ids):
        """Gets randomly a user_id from a list of user_ids."""
        return random.choice(user_ids)

    def _partial_news(self, cr, uid, ews_data):
        """Sets an observation to a partial obs and adds reason."""
        partial = [i for i in range(30)]
        measurements = ['avpu_text',
                        'blood_pressure_diastolic',
                        'oxygen_administration_flag']
        reasons = ['patient_away_from_bed', 'patient_refused',
                   'emergency_situation', 'doctors_request']

        if random.choice(partial) == 1:
            keys = []
            for key in ews_data:
                if key not in measurements:
                    keys.append(key)
            k = random.choice(keys)
            del ews_data[k]
            ews_data.update({'partial_reason': random.choice(reasons)})

        return ews_data

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
            if patient.current_location_id.usage == 'bed':
                hospital_numbers.append(patient.other_identifier)

        return hospital_numbers

    def _get_hospital_numbers_by_ward_not_placed(self, cr, uid, ward_code,
                                                 context=None):
        location_pool = self.pool['nh.clinical.location']
        patient_pool = self.pool['nh.clinical.patient']

        # get the location_ids by ward code
        location_id = location_pool.get_by_code(
            cr, uid, ward_code, context=context
        )
        # get patients who are placed in a ward (i.e. in a bed)
        patient_ids = patient_pool.search(
            cr, uid, [('current_location_id', '=', location_id)],
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

    def _get_patients_placed(self, cr, uid):
        patient_pool = self.pool['nh.clinical.patient']
        patient_ids = patient_pool.search(cr, uid, [])
        patients = patient_pool.browse(cr, uid, patient_ids)
        patient_in_bed_ids = []
        for patient in patients:
            if patient.current_location_id.usage == 'bed':
                patient_in_bed_ids.append(patient.id)
        return patient_in_bed_ids
