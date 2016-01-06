import logging
import json
import os
from datetime import datetime as dt, timedelta as td

from faker import Faker
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import orm, osv
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)

fake = Faker()


class nh_clinical_api_demo(orm.AbstractModel):
    _name = 'nh.clinical.api.demo'
    _inherit = 'nh.clinical.api.demo'

    @staticmethod
    def _file_loader(cr, uid, config_file):
        with open(config_file) as config:
            data = json.load(config)

        return data

    def demo_loader(self, cr, uid, config_file, return_file):
        """
        Creates the demo environment using the parameters specified in the
        JSON configuration file.
        :param config_file: the JSON file with parameters for your
            demo environment...
            {
                "patients": 10      # per ward
                "wards": 5,
                "beds": 20          # per ward
                "days": 3           # days ago patients were admitted
                "users": {          # users per ward
                            "nurse": 5,
                            "jnr_doctor": 2,
                            "HCA": 3,
                }
            }
        :param return_file: a JSON file that will contain user credentials.
        :return: True
        """
        config = self._file_loader(cr, uid, config_file)
        locations = self.generate_locations(cr, uid, wards=config['wards'],
                                            beds=config['beds'],
                                            hospital=True)
        ward_ids = map(lambda key: locations[key][0], locations)
        user_ids = self._load_users(cr, uid, locations, config['users'])
        adt_uid = user_ids[0]['adt'][0]
        patient_ids = self._load_patients(cr, adt_uid, config['wards'],
                                          config['patients'])
        admitted_patient_ids = self._load_admit_patients(cr, adt_uid,
                                                         ward_ids,
                                                         patient_ids,
                                                         config['days'])
        self._load_place_patients(cr, adt_uid, ward_ids, admitted_patient_ids)

        if return_file:
            directory_name = os.path.dirname(os.path.abspath(config_file))
            logins = self._get_users_login(cr, uid)
            with open(os.path.join(directory_name, return_file), 'w') as outfile:
                json.dump({'logins': logins}, outfile)

        return True

    def _get_users_login(self, cr, uid):
        """
        :return: a list of user names for all users.
        """
        user_pool = self.pool['res.users']
        users = user_pool.read_group(cr, uid, [], ['login'], ['login'])
        return [user['login'] for user in users]

    def _load_users(self, cr, uid, locations, users):
        """
        Creates users for each ward.
        :param locations: a dictionary of location ids per ward
            (see return value for self.generate_locations)
        :param users: dictionary containing the number of users for each ward.
        :return: list of dictionaries for user ids:
            [{'adt': [1], 'nurse': [2, 3]..}, {'adt': [1], 'nurse':[4, 5]}..]
        """
        result = []
        for k in locations:
            result.append(self.generate_users(cr, uid, locations[k], data=users))

        return result

    def _load_patients(self, cr, uid, wards, patients):
        """
        Creates patients for each ward
        :param uid: adt uid
        :param wards: number of wards
        :param patients: number of patients
        :return: nested list of created patient ids [[1, 2], ...[10, 11]]
        """
        patient_ids = []
        for n in range(wards):
            patient_ids.append(self.generate_patients(cr, uid, patients))

        return patient_ids

    def _load_admit_patients(self, cr, uid, ward_ids, patient_ids, days):
        """
        Admit patients in each ward.
        :param uid: adt uid
        :param ward_ids: list of ward ids for hospital
        :param patient_ids: list of lists of patient ids
        :param days: number of days
        :return: nested list of for patient ids for admitted patients
            [[1, 2], ...[10, 11]]
        """
        location_pool = self.pool['nh.clinical.location']
        ward_codes = location_pool.read(cr, uid, ward_ids, ['code'])
        start_date = dt.now() - td(days=days)
        admitted_patient_ids = []

        for n in range(len(patient_ids)):
            data = {'location': ward_codes[n]['code'], 'start_date': start_date}
            admitted_patient_ids.append(self.admit_patients(cr, uid, patient_ids[n], data))

        return admitted_patient_ids

    def _load_place_patients(self, cr, uid, ward_ids, patient_ids, context=None):
        """
        Places patients in each ward.
        :param uid: adt uid
        :param ward_ids: list of ward ids
        :param patient_ids: list of list of patient ids
        :return: nested lists of bed ids: [[1, 2], ...[10, 11]]
        """
        bed_ids = []
        for n in range(len(ward_ids)):
            bed_ids.append(self.place_patients(cr, uid, patient_ids[n], ward_ids[n], context=context))

        return bed_ids

    def generate_locations(self, cr, uid, wards=0, beds=0, hospital=False):
        """
        Generates a specified number of locations (Hospital, wards, bays, beds).
        :param wards: the number of wards in hospital.
        :param beds: the number of beds per ward.
        :return: Dict { 'Ward 1' : [ward_id, bed_id, bed_id], 'Ward 2': [ward_id_2, bed_id, etc. }
        """
        identifiers = dict()
        location_pool = self.pool['nh.clinical.location']
        pos_pool = self.pool['nh.clinical.pos']
        company_pool = self.pool['res.company']
        context_pool = self.pool['nh.clinical.context']

        context_id = context_pool.search(cr, uid, [['name', 'in', ['eobs', 'etakelist']]])

        if hospital:
            hospital_id = location_pool.create(cr, uid, {'name': fake.company()})
            admission_id = location_pool.create(cr, uid, {'name': fake.company()})
            discharge_id = location_pool.create(cr, uid, {'name': fake.company()})
            company_id = company_pool.create(cr, uid, {'name': fake.company()})

            # creates POS (clinical point of service)
            pos_pool.create(cr, uid, {'name': fake.company(), 'location_id': hospital_id,
                'company_id': company_id, 'lot_admission_id': admission_id,
                'lot_discharge_id': discharge_id})
        else:
            hospital_id = location_pool.search(cr, uid, [['id', '>', 0]])[0]

        for ward in range(wards):
            ward_name = 'Ward ' + str(ward + 1)
            ward_code = 'W' + str(ward + 1)
            ward_id = location_pool.create(cr, uid, {
                'name': ward_name, 'usage': 'ward',
                'context_ids': [[6, False, context_id]],
                'parent_id': hospital_id,
                'code': ward_code})
            identifiers.update({ward_name: [ward_id]})
            _logger.info("'%s' created", ward_name)
            # test for unique 'code'.
            for bed in range(beds):
                bed_name = 'Bed ' + str(bed + 1)
                bed_code = ward_code + 'B' + str(bed + 1)
                bed_id = location_pool.create(cr, uid, {
                    'name': bed_name, 'parent_id': ward_id,
                    'usage': 'bed', 'context_ids': [[6, False, context_id]],
                    'code': bed_code})
                identifiers[ward_name].append(bed_id)
                _logger.info("'%s' created", bed_name)

        return identifiers

    def generate_users(self, cr, uid, location_ids, data=dict()):
        """
        Generates a ward manager, nurse, HCA, junior doctor, consultant,
        registrar, receptionist, admin and ADT user. Nurses and HCAs are
        assigned to all beds in ward.
        :param location_ids: ['ward_id', 'bed_id_1', 'bed_id_2'...]
        :return: Dictionary { 'adt' : [id], 'nurse': [id, id], ... }
        """
        identifiers = dict()
        user_pool = self.pool['res.users']
        group_pool = self.pool['res.groups']
        location_pool = self.pool['nh.clinical.location']
        users = [
            ('ward_manager', 'NH Clinical Ward Manager Group'),
            ('nurse', 'NH Clinical Nurse Group'),
            ('hca', 'NH Clinical HCA Group'),
            ('jnr_doctor', 'NH Clinical Junior Doctor Group'),
            ('consultant', 'NH Clinical Consultant Group'),
            ('registrar', 'NH Clinical Registrar Group'),
            ('receptionist', 'NH Clinical Receptionist Group'),
            ('admin', 'NH Clinical Admin Group')
        ]
        pos_id = location_pool.read(cr, uid, [location_ids[0]], ['pos_id'])[0]['pos_id'][0]

        # create adt user if non exists
        adt_group_id = group_pool.search(cr, uid, [
            ['name', 'in', ['NH Clinical ADT Group', 'Contact Creation', 'NH Clinical Admin Group', 'Employee']]])
        adt_uid_ids = user_pool.search(cr, uid, [['groups_id', 'in', adt_group_id], ['pos_id', '=', pos_id]])
        if adt_uid_ids:
            identifiers.update({'adt': [adt_uid_ids[0]]})
        else:
            adt_login = 'adt_login'
            adt_id = user_pool.create(cr, uid, {
                'name': 'ADT', 'login': adt_login,
                'password': adt_login, 'groups_id': [[6, False, adt_group_id]],
                'pos_id': pos_id,
            })
            identifiers.update({'adt': [adt_id]})

        # get number of users for that type of user
        for user in users:
            user_type = user[0]
            if user_type in data:
                number_of_users = data.get(user_type)
            else:
                number_of_users = 1

            for x in range(number_of_users):
                user_login = user_type + '_' + str(x+1) + '_' + str(location_ids[0])
                assign_groups = [user[1], 'Employee']

                if user_type in ('ward_manager', 'admin'):
                    assign_groups.append('Contact Creation')
                if user_type in ('nurse', 'hca'):
                    locations = location_ids[1:]
                else:
                    locations = [location_ids[0]]

                group_id = group_pool.search(cr, uid, [['name', 'in', assign_groups]])
                user_id = user_pool.create(cr, uid, {
                    'name': fake.name(), 'login': user_login,
                    'password': user_login, 'groups_id': [[6, False, group_id]],
                    'pos_id': pos_id, 'location_ids': [[6, False, locations]]})

                if user_type in identifiers:
                    identifiers[user_type].append(user_id)
                else:
                    identifiers.update({user_type: [user_id]})
                _logger.info("'%s' created", user_type)

        return identifiers

    def generate_patients(self, cr, uid, patients, context=None):
        """
        Generates a specified number of patients.
        :param uid: the adt uid
        :param patients: the number of patients to register.
        :return: List of ids of the patients registered.
        """
        identifiers = list()
        api = self.pool['nh.eobs.api']
        patient_pool = self.pool['nh.clinical.patient']

        for data in range(patients):
            gender = fake.random_element(['M', 'F'])
            other_identifier = fake.bothify('#?#?#?#?#')
            patient = {
                'patient_identifier': fake.bothify('#?#?#?#?#'),
                'family_name': fake.last_name(),
                'middle_names': fake.last_name(),
                'given_name': fake.last_name(),
                'dob': fake.date_time(),
                'gender': gender,
                'sex': gender,
                'ethnicity': fake.random_element(patient_pool._ethnicity)[0]
            }

            api.register(cr, uid, other_identifier, patient, context=context)
            _logger.info("Patient '%s' created", other_identifier)
            identifiers += patient_pool.search(cr, uid, [['other_identifier', '=', other_identifier]], context=context)

        return identifiers

    def admit_patients(self, cr, uid, patient_ids, data, context=None):
        """
        Admits a list of patients.
        :param uid: adt uid
        :param patient_ids: list parameter of patient ids.
        :param data: dictionary parameter that contains the following
            location: location code where the patient will be admitted.
            start_date: admission start date.
        :return: list of ids for admitted patients.
        """
        api = self.pool['nh.eobs.api']
        patient_pool = self.pool['nh.clinical.patient']
        activity_pool = self.pool['nh.activity']
        identifiers = list()

        for patient_id in patient_ids:
            patient = patient_pool.browse(cr, uid, patient_id)
            spell_activity_id = activity_pool.search(cr, uid, [
                ('data_model', '=', 'nh.clinical.spell'),
                ('patient_id', '=', patient.id)])

            if not spell_activity_id:
                if api.admit(cr, uid, patient.other_identifier, data, context=context):
                    identifiers.append(patient_id)
                    _logger.info("Patient '%s' admitted", patient.other_identifier)

        return identifiers

    def place_patients(self, cr, uid, patient_ids, ward_id, context=None):
        """
        Places a list of patients in vacant beds in a particular ward.
        :param patient_ids: list of patients to be placed in beds
        :param ward_id: the ward id for the ward to place the patients in.
        :return: list of bed_ids for those beds filled.
        """
        activity_pool = self.pool['nh.activity']
        location_pool = self.pool['nh.clinical.location']
        identifiers = list()

        ward = location_pool.browse(cr, uid, ward_id)
        bed_ids = [bed.id for bed in ward.child_ids if bed.is_available]
        activity_ids = activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.patient.placement'),
            ('patient_id', 'in', patient_ids)])

        for index, bed_id in enumerate(bed_ids):
            if index < len(activity_ids):
                activity_pool.submit(cr, uid, activity_ids[index], {'location_id': bed_id})
                activity_pool.complete(cr, uid, activity_ids[index])
                identifiers.append(bed_id)
                _logger.info("Patient placed in %s", bed_id)
            else:
                break

        return identifiers

    def transfer_patients(self, cr, uid, hospital_numbers, locations, context=None):
        """
        Transfers a list of patients to a list of locations.
        :param hospital_numbers: list of hospital numbers of the patients
        :param locations: list of location codes where the patients will be
            transferred to
        :return: list of hospital numbers for the successfully transferred
            patients
        """
        api = self.pool['nh.eobs.api']
        location_pool = self.pool['nh.clinical.location']
        patients = []

        # filter only available locations
        codes = location_pool.read_group(cr, uid, [
            ('code', 'in', locations), ('is_available', '=', True),
            ], ['code'], ['code'])
        location_codes = [{'location': code['code']} for code in codes]
        # number of patients should equal number of location codes
        hospital_numbers = hospital_numbers[:len(location_codes)]

        for index, hospital_number in enumerate(hospital_numbers):
            try:
                api.transfer(cr, uid, hospital_number,
                             location_codes[index], context=context)
            except osv.except_osv as e:
                _logger.error('Failed to transfer patient!' + str(e))
                continue
            else:
                patients.append(hospital_number)

        return patients

    def discharge_patients(self, cr, uid, hospital_numbers, data, context=None):
        """
        Discharges a list of patients.
        :param hospital_numbers: list of hospital numbers of the patients
        :param data: dictionary parameter that may contain the following keys
            discharge_date: patient discharge date.
        :return: list of hospital numbers for the successfully
            discharged patients
        """
        api = self.pool['nh.eobs.api']
        patients = []

        for hospital_number in hospital_numbers:
            try:
                api.discharge(cr, uid, hospital_number, data, context=context)
            except osv.except_osv as e:
                _logger.error('Failed to discharge patient!' + str(e))
                continue
            else:
                patients.append(hospital_number)

        return patients

    def generate_news_simulation(self, cr, uid, begin_date=False, patient_ids=None, context=None):
        """
        Generates demo news data over a period of time for the patients in patient_ids.
        :param begin_date: Starting point of the demo. If not specified it defaults to now - 1 day.
        :param patient_ids: List of patients that are going to be used. Every patient by default.
        :return: True if successful
        """
        # TODO: work out randomisation for demonstration data
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        if not begin_date:
            begin_date = (dt.now()-td(days=1)).strftime(dtf)
        if not patient_ids:
            patient_ids = patient_pool.search(cr, uid, [], context=context)
        if uid == SUPERUSER_ID:
            group_pool = self.pool['res.groups']
            user_pool = self.pool['res.users']
            nurse_group_id = group_pool.search(cr, uid, [['name', '=', 'NH Clinical Nurse Group']], context=context)
            user_pool.write(cr, uid, SUPERUSER_ID, {'groups_id': [(4, nurse_group_id[0])]})

        ews_activity_ids = activity_pool.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['data_model', '=', 'nh.clinical.patient.observation.ews'],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)
        activity_pool.write(cr, uid, ews_activity_ids, {'date_scheduled': begin_date}, context=context)

        current_date = dt.strptime(begin_date, dtf)
        while current_date < dt.now():
            ews_activity_ids = activity_pool.search(cr, uid, [
                ['patient_id', 'in', patient_ids],
                ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                ['state', 'not in', ['completed', 'cancelled']],
                ['date_scheduled', '<=', current_date.strftime(dtf)]], context=context)

            if not ews_activity_ids:
                return False
            nearest_date = False

            for ews_id in ews_activity_ids:
                ews_data = {
                    'respiration_rate': fake.random_element([18]*90 + [11]*8 + [24]*2),
                    'indirect_oxymetry_spo2': fake.random_element([99]*90 + [95]*8 + [93]*2),
                    'oxygen_administration_flag': fake.random_element([False]*96 + [True]*4),
                    'blood_pressure_systolic': fake.random_element([120]*90 + [110]*8 + [100]*2),
                    'blood_pressure_diastolic': 80,
                    'avpu_text': fake.random_element(['A']*97 + ['V', 'P', 'U']),
                    'pulse_rate': fake.random_element([65]*90 + [50]*8 + [130]*2),
                    'body_temperature': fake.random_element([37.5]*93 + [36.0]*7),
                }
                activity_pool.submit(cr, uid, ews_id, ews_data, context=context)
                activity_pool.complete(cr, uid, ews_id, context=context)
                _logger.info("EWS observation '%s' made", ews_id)
                # set complete date
                complete_date = current_date - td(minutes=10)
                activity_pool.write(cr, uid, ews_id, {'date_terminated': complete_date.strftime(dtf)}, context=context)
                # get frequency of triggered ews
                triggered_ews_id = activity_pool.search(cr, uid, [
                    ['creator_id', '=', ews_id],
                    ['data_model', '=', 'nh.clinical.patient.observation.ews']],
                    context=context)
                if not triggered_ews_id:
                    osv.except_osv('Error!', 'The NEWS observation was not triggered after previous submission!')
                triggered_ews = activity_pool.browse(cr, uid, triggered_ews_id[0], context=context)
                # set scheduled date
                scheduled_date = complete_date + td(minutes=triggered_ews.data_ref.frequency)
                activity_pool.write(cr, uid, triggered_ews_id[0],
                                    {'date_scheduled': scheduled_date.strftime(dtf)}, context=context)
                if not nearest_date or scheduled_date < nearest_date:
                    nearest_date = scheduled_date

            current_date = nearest_date
        return True
