import logging
import json
from datetime import datetime as dt, timedelta as td

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import orm, osv
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

from faker import Faker
from faker.providers import BaseProvider
fake = Faker()


class nh_clinical_api_demo(orm.AbstractModel):
    _name = 'nh.clinical.api.demo'
    _inherit = 'nh.clinical.api.demo'

    @staticmethod
    def _file_loader(cr, uid, config_file):
        with open(config_file) as config:
            data = json.load(config)

        return data

    def demo_loader(self, cr, uid, config_file):
        """
        Takes a dictionary objects for demo environment.
        :return: True
        """
        config = self._file_loader(cr, uid, config_file)
        locations = self.generate_locations(cr, uid, wards=config['wards'],
                                            beds=config['beds'],
                                            hospital=True)
        ward_ids = [locations[key][0] for key in locations]
        user_ids = self._load_users(cr, uid, ward_ids, config['users'])
        adt_uid = user_ids[0]['adt'][0]
        patient_ids = self._load_patients(cr, adt_uid, config['wards'],
                                          config['patients'])
        admitted_patient_ids = self._load_admit_patients(cr, adt_uid,
                                                         ward_ids,
                                                         patient_ids,
                                                         config['days'])
        bed_ids = self._load_place_patients(cr, adt_uid, ward_ids,
                                            admitted_patient_ids)
        return user_ids

    def _load_users(self, cr, uid, ward_ids, users):
        """
        Creates users for each ward.
        :param ward_ids: list of ward ids
        :param users: dictionary containing the number of users fo each ward.
        :return: list of dictionaries for user ids:
            [{'adt': [1], 'nurse': [2, 3]..}, {'adt': [1], 'nurse':[4, 5]}..]
        """
        user_ids = []
        for ward in ward_ids:
            user_ids.append(self.generate_users(cr, uid, ward, data=users))

        return user_ids

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

        context_id = context_pool.search(cr, uid, [['name', '=', 'eobs']])

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

    def generate_users(self, cr, uid, location_id, data=dict()):
        """
        Generates a ward manager, nurse, HCA, junior doctor, consultant,
        registrar, receptionist, admin and ADT user.
        :param location_id: the id of the location the users will be assigned to.
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
        pos_id = location_pool.read(cr, uid, [location_id], ['pos_id'])[0]['pos_id'][0]

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
                user_login = user_type + '_' + str(x+1) + '_' + str(location_id)
                assign_groups = [user[1], 'Employee']
                if user_type in ('ward_manager', 'admin'):
                    assign_groups.append('Contact Creation')

                group_id = group_pool.search(cr, uid, [['name', 'in', assign_groups]])
                user_id = user_pool.create(cr, uid, {
                    'name': fake.name(), 'login': user_login,
                    'password': user_login, 'groups_id': [[6, False, group_id]],
                    'pos_id': pos_id, 'location_ids': [[6, False, [location_id]]]})

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

        # loop through ADT user ids, creating patients for each ADT.
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
            # create patient
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
                # a list of lists of bed ids of placed patients
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

    def build_unit_test_env(self, cr, uid, wards=None, bed_count=2, patient_admit_count=2, patient_placement_count=1,
                            ews_count=1, context=False, weight_count=0, blood_sugar_count=0, height_count=0, o2target_count=0,
                            users=None):
        """
        Create a default unit test environment for basic unit tests.
            2 WARDS - U and T
            2 beds per ward - U01, U02, T01, T02
            2 patients admitted per ward
            1 patient placed in bed per ward
            1 ews observation taken per patient
        The environment is customizable, the wards parameter must be a list of ward codes. All the other parameters are
        the number of beds, patients, placements and observations we want.

        users parameter expects a dictionary with the following format:
            {
                'ward_managers': {
                    'name': ['login', 'ward_code']
                },
                'nurses': {
                    'name': ['login', [list of locations]]
                },
                'hcas': {
                    'name': ['login', [list of locations]]
                },
                'doctors': {
                    'name': ['login', [list of locations]]
                }
            }
            if there is no data the default behaviour will be to add a ward manager per ward i.e. 'WMU' and 'WMT' and
            a nurse responsible for all beds in the ward i.e. 'NU' and 'NT'
        """
        if not wards:
            wards = ['U', 'T']
        assert patient_admit_count >= patient_placement_count
        assert bed_count >= patient_placement_count
        fake = self.next_seed_fake()
        activity_pool = self.pool['nh.activity']
        location_pool = self.pool['nh.clinical.location']
        context_pool = self.pool['nh.clinical.context']
        user_pool = self.pool['res.users']
        pos_id = self.create(cr, uid, 'nh.clinical.pos')
        pos_location_id = location_pool.search(cr, uid, [('pos_id', '=', pos_id)])[0]

        adt_uid = self.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_id})

        if context:
            context_ids = context_pool.search(cr, uid, [['name', '=', context]])
            context = [[6, False, context_ids]] if context_ids else False

        # LOCATIONS
        ward_ids = [self.create(cr, uid, 'nh.clinical.location', 'location_ward', {'context_ids': context, 'parent_id': pos_location_id, 'name': 'Ward '+w, 'code': w}) for w in wards]
        i = 0
        bed_ids = {}
        bed_codes = {}
        for wid in ward_ids:
            bed_ids[wards[i]] = [self.create(cr, uid, 'nh.clinical.location', 'location_bed', {'context_ids': context, 'parent_id': wid, 'name': 'Bed '+str(n), 'code': wards[i]+str(n)}) for n in range(bed_count)]
            bed_codes[wards[i]] = [wards[i]+str(n) for n in range(bed_count)]
            i += 1

        # USERS
        if not users:
            users = {'ward_managers': {}, 'nurses': {}, 'hcas': {}}
            for w in wards:
                users['ward_managers']['WM'+w] = ['WM'+w, w]
                users['nurses']['N'+w] = ['N'+w, bed_codes[w]]
                users['hcas']['H'+w] = ['H'+w, bed_codes[w]]

        if users.get('ward_managers'):
            wm_ids = {}
            for wm in users['ward_managers'].keys():
                wid = location_pool.search(cr, uid, [('code', '=', users['ward_managers'][wm][1])])
                wm_ids[wm] = self.create(cr, uid, 'res.users', 'user_ward_manager', {'name': wm, 'login': users['ward_managers'][wm][0], 'location_ids': [[6, False, wid]]})

        if users.get('nurses'):
            n_ids = {}
            for n in users['nurses'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['nurses'][n][1])])
                n_ids[n] = self.create(cr, uid, 'res.users', 'user_nurse', {'name': n, 'login': users['nurses'][n][0], 'location_ids': [[6, False, lids]]})

        if users.get('hcas'):
            h_ids = {}
            for h in users['hcas'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['hcas'][h][1])])
                h_ids[h] = self.create(cr, uid, 'res.users', 'user_hca', {'name': h, 'login': users['hcas'][h][0], 'location_ids': [[6, False, lids]]})

        if users.get('doctors'):
            d_ids = {}
            for d in users['doctors'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['doctors'][d][1])])
                d_ids[d] = self.create(cr, uid, 'res.users', 'user_doctor', {'name': d, 'login': users['doctors'][d][0], 'location_ids': [[6, False, lids]]})

        for wcode in wards:
            activity_pool = self.pool['nh.activity']
            adt_register_pool = self.pool['nh.clinical.adt.patient.register']
            adt_admit_pool = self.pool['nh.clinical.adt.patient.admit']
            reg_activity_ids = [adt_register_pool.create_activity(cr, adt_uid, {},
                                                                  {'other_identifier': 'hn_'+wcode+str(i)})
                                for i in range(patient_admit_count)]
            [activity_pool.complete(cr, adt_uid, id) for id in reg_activity_ids]
            admit_activity_ids = [adt_admit_pool.create_activity(cr, adt_uid, {},
                                                                 {'other_identifier': 'hn_'+wcode+str(i),
                                                                  'location': wcode})
                                  for i in range(patient_admit_count)]
            [activity_pool.complete(cr, adt_uid, id) for id in admit_activity_ids]

        for wid in ward_ids:
            code = location_pool.read(cr, uid, wid, ['code'])['code']
            wmuid = user_pool.search(cr, uid, [('location_ids', 'in', [wid]), ('groups_id.name', 'in', ['NH Clinical Ward Manager Group'])])
            wmuid = uid if not wmuid else wmuid[0]
            placement_activity_ids = activity_pool.search(cr, uid, [
                ('data_model', '=', 'nh.clinical.patient.placement'),
                ('state', 'not in', ['completed', 'cancelled']), ('user_ids', 'in', [wmuid])])
            if not placement_activity_ids:
                continue
            for i in range(patient_placement_count):
                placement_activity_id = fake.random_element(placement_activity_ids)
                bed_location_id = fake.random_element(bed_ids[code])
                activity_pool.submit(cr, wmuid, placement_activity_id, {'location_id': bed_location_id})
                activity_pool.complete(cr, wmuid, placement_activity_id)
                placement_activity_ids.remove(placement_activity_id)
                bed_ids[code].remove(bed_location_id)

        for i in range(ews_count):
            ews_activity_ids = []
            for wid in ward_ids:
                ews_activity_ids += activity_pool.search(cr, uid, [
                    ('data_model', '=', 'nh.clinical.patient.observation.ews'),
                    ('state', 'not in', ['completed', 'cancelled']), ('location_id', 'child_of', wid)])
            for ews in activity_pool.browse(cr, uid, ews_activity_ids):
                nuid = user_pool.search(cr, uid, [('location_ids', 'in', [ews.location_id.id]), ('groups_id.name', 'in', ['NH Clinical Nurse Group'])])
                nuid = uid if not nuid else nuid[0]
                activity_pool.assign(cr, uid, ews.id, nuid)
                activity_pool.submit(cr, nuid, ews.id, self.demo_data(cr, uid, 'nh.clinical.patient.observation.ews'))
                activity_pool.complete(cr, nuid, ews.id)

        return True

    def build_eobs_uat_env(self, cr, uid, data, context=None):
        wards = data.get('wards') if data.get('wards') else 10
        beds = data.get('beds') if data.get('beds') else 10
        patients = data.get('patients') if data.get('patients') else 10
        begin_date = data.get('begin_date') if data.get('begin_date') else dt.now().strftime(dtf)
        fake = self.next_seed_fake()
        api = self.pool['nh.eobs.api']
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        location_pool = self.pool['nh.clinical.location']
        context_pool = self.pool['nh.clinical.context']
        user_pool = self.pool['res.users']
        pos_pool = self.pool['nh.clinical.pos']
        pos_ids = pos_pool.search(cr, uid, [], context=context)
        if not pos_ids:
            pos_ids = [self.create(cr, uid, 'nh.clinical.pos')]
        pos_location_id = location_pool.search(cr, uid, [('pos_id', '=', pos_ids[0])])[0]

        adt_uid = user_pool.search(cr, uid, [['groups_id.name', 'in', ['NH Clinical ADT Group']]], context=context)
        if not adt_uid:
            adt_uid = self.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_ids[0]})
        else:
            adt_uid = adt_uid[0]

        context_ids = context_pool.search(cr, uid, [['name', '=', 'eobs']], context=context)

        # LOCATIONS

        ward_ids = [self.create(cr, uid, 'nh.clinical.location', 'location_ward', {'context_ids': [[6, False, context_ids]], 'parent_id': pos_location_id, 'name': 'Ward '+str(w), 'code': str(w)})
                    if not location_pool.search(cr, uid, [['code', '=', str(w)], ['parent_id', '=', pos_location_id], ['usage', '=', 'ward']], context=context)
                    else location_pool.search(cr, uid, [['code', '=', str(w)], ['parent_id', '=', pos_location_id], ['usage', '=', 'ward']], context=context)[0] for w in range(wards)]
        bed_ids = {}
        bed_codes = {}
        for w in range(wards):
            bed_ids[str(w)] = [self.create(cr, uid, 'nh.clinical.location', 'location_bed', {'context_ids': [[6, False, context_ids]], 'parent_id': ward_ids[w], 'name': 'Bed '+str(b), 'code': str(w)+str(b)})
                               if not location_pool.search(cr, uid, [['code', '=', str(w)+str(b)], ['parent_id.code', '=', str(w)], ['usage', '=', 'bed']], context=context)
                               else location_pool.search(cr, uid, [['code', '=', str(w)+str(b)], ['parent_id.code', '=', str(w)], ['usage', '=', 'bed']], context=context)[0] for b in range(beds)]
            for b in range(beds):
                bed = location_pool.read(cr, uid, bed_ids[str(w)][b], ['is_available'], context=context)
                bed_codes[str(w)+str(b)] = {'available': bed['is_available'], 'ward': str(w)}

        # USERS

        wm_ids = {}
        n_ids = {}
        h_ids = {}
        d_ids = {}
        for w in range(wards):
            wm_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_ward_manager', {'name': 'WM'+str(w), 'login': 'WM'+str(w), 'password': 'WM'+str(w), 'location_ids': [[6, False, [ward_ids[w]]]]}) if not user_pool.search(cr, uid, [['login', '=', 'WM'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'WM'+str(w)]], context=context)[0]
            n_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_nurse', {'name': 'N'+str(w), 'login': 'N'+str(w), 'password': 'N'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'N'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'N'+str(w)]], context=context)[0]
            h_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_hca', {'name': 'H'+str(w), 'login': 'H'+str(w), 'password': 'H'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'H'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'H'+str(w)]], context=context)[0]
            d_ids[str(w)] = self.create(cr, uid, 'res.users', 'user_doctor', {'name': 'D'+str(w), 'login': 'D'+str(w), 'password': 'D'+str(w), 'location_ids': [[6, False, bed_ids[str(w)]]]}) if not user_pool.search(cr, uid, [['login', '=', 'D'+str(w)]], context=context) else user_pool.search(cr, uid, [['login', '=', 'D'+str(w)]], context=context)[0]

        # PATIENT REGISTER

        patient_identifiers = []
        for p in range(patients):
            hospital_number = BaseProvider.numerify('#######')
            while patient_pool.search(cr, uid, [['other_identifier', '=', hospital_number]], context=context):
                hospital_number = BaseProvider.numerify('#######')
            nhs_number = BaseProvider.numerify('##########')
            while patient_pool.search(cr, uid, [['patient_identifier', '=', nhs_number]], context=context):
                nhs_number = BaseProvider.numerify('##########')
            gender = fake.random_element(['M', 'F'])
            data = {
                'patient_identifier': nhs_number,
                'family_name': fake.last_name(),
                'given_name': fake.first_name(),
                'dob': fake.date_time_between(start_date="-85y", end_date="now").strftime(dtf),
                'gender': gender,
                'sex': gender,
                'ethnicity': fake.random_element(patient_pool._ethnicity)[0]
            }
            api.register(cr, adt_uid, hospital_number, data, context=context)
            patient_identifiers.append(hospital_number)

        # PATIENT ADMISSION

        count = 0
        for b in bed_codes.keys():
            if not bed_codes[b]['available']:
                continue
            if len(patient_identifiers) <= count:
                break
            data = {
                'location': bed_codes[b]['ward'],
                'start_date': begin_date
            }
            wm_uid = wm_ids[bed_codes[b]['ward']]
            api.admit(cr, adt_uid, patient_identifiers[count], data, context=context)
            placement_id = activity_pool.search(cr, uid, [['patient_id.other_identifier', '=', patient_identifiers[count]], ['data_model', '=', 'nh.clinical.patient.placement']], context=context)
            if not placement_id:
                osv.except_osv('Error!', 'The patient placement was not triggered after admission!')
            location_id = location_pool.search(cr, uid, [['usage', '=', 'bed'], ['code', '=', b], ['parent_id.usage', '=', 'ward'], ['parent_id.code', '=', bed_codes[b]['ward']]], context=context)
            if not location_id:
                osv.except_osv('Error!', 'Cannot complete placement. Location not found!')
            activity_pool.submit(cr, wm_uid, placement_id[0], {'date_started': begin_date, 'location_id': location_id[0]}, context=context)
            activity_pool.complete(cr, wm_uid, placement_id[0], context=context)
            activity_pool.write(cr, uid, placement_id[0], {'date_terminated': begin_date}, context=context)
            count += 1

        # SUBMIT NEWS OBSERVATIONS OVER A PERIOD OF TIME

        ews_activity_ids = activity_pool.search(cr, uid, [['patient_id.other_identifier', 'in', patient_identifiers], ['data_model', '=', 'nh.clinical.patient.observation.ews'], ['state', 'not in', ['completed', 'cancelled']]], context=context)
        activity_pool.write(cr, uid, ews_activity_ids, {'date_scheduled': begin_date}, context=context)

        current_date = dt.strptime(begin_date, dtf)
        while current_date < dt.now():
            ews_activity_ids = activity_pool.search(cr, uid, [['patient_id.other_identifier', 'in', patient_identifiers], ['data_model', '=', 'nh.clinical.patient.observation.ews'], ['state', 'not in', ['completed', 'cancelled']], ['date_scheduled', '<=', current_date.strftime(dtf)]], context=context)
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
                ews_activity = activity_pool.browse(cr, uid, ews_id, context=context)
                n_uid = n_ids[ews_activity.location_id.parent_id.code]
                activity_pool.submit(cr, n_uid, ews_id, ews_data, context=context)
                activity_pool.complete(cr, n_uid, ews_id, context=context)
                ews_activity = activity_pool.browse(cr, uid, ews_id, context=context)
                overdue = fake.random_element([False, False, False, False, False, False, False, True, True, True])
                if overdue:
                    complete_date = current_date + td(days=1)
                else:
                    complete_date = current_date + td(minutes=ews_activity.data_ref.frequency-10)
                activity_pool.write(cr, uid, ews_id, {'date_terminated': complete_date.strftime(dtf)}, context=context)
                triggered_ews_id = activity_pool.search(cr, uid, [['creator_id', '=', ews_id], ['data_model', '=', 'nh.clinical.patient.observation.ews']], context=context)
                if not triggered_ews_id:
                    osv.except_osv('Error!', 'The NEWS observation was not triggered after previous submission!')
                triggered_ews = activity_pool.browse(cr, uid, triggered_ews_id[0], context=context)
                activity_pool.write(cr, uid, triggered_ews_id[0], {'date_scheduled': (complete_date + td(minutes=triggered_ews.data_ref.frequency)).strftime(dtf)}, context=context)
                if not nearest_date or complete_date + td(minutes=triggered_ews.data_ref.frequency) < nearest_date:
                    nearest_date = complete_date + td(minutes=triggered_ews.data_ref.frequency)
            current_date = nearest_date
        return True