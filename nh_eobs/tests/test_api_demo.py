import logging
from mock import MagicMock

from datetime import datetime, timedelta
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestApiDemo(TransactionCase):

    def setUp(self):
        super(TestApiDemo, self).setUp()
        cr, uid = self.cr, self.uid
        self.api_demo = self.registry('nh.clinical.api.demo')
        self.user_pool = self.registry('res.users')
        self.group_pool = self.registry('res.groups')
        self.location_pool = self.registry('nh.clinical.location')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.activity_pool = self.registry('nh.activity')

        self.adtgroup_id = self.group_pool.search(cr, uid, [['name', '=', 'NH Clinical ADT Group']])
        self.adtuid_ids = self.user_pool.search(cr, uid, [['groups_id', 'in', self.adtgroup_id]])
        if not self.adtuid_ids:
            raise osv.except_osv('No ADT User!', 'ADT user required to register patient.')

    ##############
    # Unit Tests #
    ##############

    def test_01_load_users_calls_generate_users(self):
        cr, uid = self.cr, self.uid
        config = {
            'patients': 2,
            'users': {'nurse': 2, 'jnr_doctor': 2},
            'wards': 2, 'beds': 2,
        }
        self.api_demo.generate_users = MagicMock()
        self.api_demo._load_users(cr, uid, [1, 2], config['users'])

        self.assertEquals(self.api_demo.generate_users.call_count, 2)
        self.api_demo.generate_users.assert_any_call(cr, uid, 1, data=config['users'])
        self.api_demo.generate_users.assert_any_call(cr, uid, 2, data=config['users'])

        del self.api_demo.generate_users

    def test_02_load_patients_calls_generate_patients(self):
        cr, uid = self.cr, self.uid
        self.api_demo.generate_patients = MagicMock()
        self.api_demo._load_patients(cr, uid, 2, 2)

        self.assertEquals(self.api_demo.generate_patients.call_count, 2)
        self.api_demo.generate_patients.assert_any_call(cr, uid, 2)
        self.api_demo.generate_patients.assert_any_call(cr, uid, 2)

        del self.api_demo.generate_patients

    def test_03_load_admit_patients_calls_admit_patients(self):
        cr, uid = self.cr, self.uid
        location_pool = self.registry('nh.clinical.location')
        location_pool.read = MagicMock(return_value=[{'code': 'W1'}, {'code': 'W2'}])

        self.api_demo.admit_patients = MagicMock(side_effect=([1, 2], [3, 4]))

        result = self.api_demo._load_admit_patients(cr, uid, [1, 2], [[1, 2], [3, 4]], days=2)
        call_count = self.api_demo.admit_patients.call_count
        self.assertEquals(2, call_count)
        self.assertEquals([[1, 2], [3, 4]], result)

        del self.api_demo.admit_patients
        del location_pool.read

    def test_04_load_place_patients_calls_place_patients(self):
        cr, uid = self.cr, self.uid
        self.api_demo.place_patients = MagicMock(side_effect=([1, 2], [3, 4]))

        results = self.api_demo._load_place_patients(cr, uid, [1, 2], [[1, 2], [3, 4]], context=None)
        self.assertEquals([[1, 2], [3, 4]], results)
        call_count = self.api_demo.place_patients.call_count
        self.assertEquals(2, call_count)
        self.api_demo.place_patients.assert_any_call(cr, uid, [1, 2], 1, context=None)
        self.api_demo.place_patients.assert_any_call(cr, uid, [3, 4], 2, context=None)

        del self.api_demo.place_patients

    def test_04_transfer_patients_calls_transfer(self):
        cr, uid = self.cr, self.uid
        api = self.registry('nh.eobs.api')
        api.transfer = MagicMock()
        location_pool = self.registry('nh.clinical.location')
        location_pool.read_group = MagicMock(return_value=[{'code': 'bed1'}, {'code': 'bed2'}])

        self.api_demo.transfer_patients(cr, uid, ['TESTN1', 'TESTN2'], ['bed1', 'bed2'], context=None)
        self.assertEquals(api.transfer.call_count, 2)
        api.transfer.assert_any_call(cr, uid, 'TESTN1', {'location': 'bed1'}, context=None)
        api.transfer.assert_any_call(cr, uid, 'TESTN2', {'location': 'bed2'}, context=None)

        del api.transfer
        del location_pool.read_group

    def test_05_transfer_patients_when_there_is_no_patient_or_spell(self):
        cr, uid = self.cr, self.uid
        api = self.registry('nh.eobs.api')
        api.transfer = MagicMock(side_effect=osv.except_osv('Error!', 'Patient not found!'))
        location_pool = self.registry('nh.clinical.location')
        location_pool.read_group = MagicMock(return_value=[{'code': 'bed1'}])

        result = self.api_demo.transfer_patients(cr, uid, ['TESTN1'], ['bed1'], context=None)
        self.assertEquals(result, [])

        del api.transfer
        del location_pool.read_group

    def test_06_transfer_patients_when_more_patients_than_available_locations(self):
        cr, uid = self.cr, self.uid
        api = self.registry('nh.eobs.api')
        api.transfer = MagicMock()
        location_pool = self.registry('nh.clinical.location')
        location_pool.read_group = MagicMock(return_value=[{'code': 'bed1'}])

        self.api_demo.transfer_patients(cr, uid, ['TESTN1', 'TESTN2'], ['bed1'])
        self.assertEquals(api.transfer.call_count, 1)
        api.transfer.assert_called_once_with(cr, uid, 'TESTN1', {'location': 'bed1'}, context=None)

        del api.transfer
        del location_pool.read_group

    def test_07_discharge_patients_calls_discharge(self):
        cr, uid = self.cr, self.uid
        api = self.registry('nh.eobs.api')
        api.discharge = MagicMock()

        self.api_demo.discharge_patients(cr, uid, [1, 2], {'discharge_date': '2015-01-01 00:00:00'})
        self.assertEquals(api.discharge.call_count, 2)
        api.discharge.assert_any_call(cr, uid, 1, {'discharge_date': '2015-01-01 00:00:00'}, context=None)
        api.discharge.assert_any_call(cr, uid, 2, {'discharge_date': '2015-01-01 00:00:00'}, context=None)
        del api.discharge

    def test_08_discharge_patients_when_there_is_no_patient_or_spell(self):
        cr, uid = self.cr, self.uid
        api = self.registry('nh.eobs.api')
        api.discharge = MagicMock(side_effect=osv.except_osv('Error!', 'Patient not found!'))

        result = self.api_demo.discharge_patients(cr, uid, [1], {'discharge_date': '2015-01-01 00:00:00'})
        self.assertEquals(result, [])
        del api.discharge

    def test_09_get_users_login(self):
        cr, uid = self.cr, self.uid
        return_value = [
            {'login': 'nurse_login'}, {'login': 'dr_login'}
        ]
        self.user_pool.read_group = MagicMock(return_value=return_value)

        result = self.api_demo._get_users_login(cr, uid)
        self.assertEquals(result, ['nurse_login', 'dr_login'])
        del self.user_pool.read_group

    #####################
    # Integration Tests #
    #####################

    def test_09_generate_locations(self):
        cr, uid = self.cr, self.uid

        identifiers = self.api_demo.generate_locations(cr, uid, wards=2, beds=2)
        # test number of wards created
        self.assertEquals(2, len(identifiers))
        # test number of beds created. Length of list is 3 because first element is Ward ID.
        self.assertEquals(3, len(identifiers['Ward 1']))
        self.assertEquals(3, len(identifiers['Ward 2']))

        # test number of wards/beds is 0 when nothing is passed
        identifiers = self.api_demo.generate_locations(cr, uid)
        self.assertEquals(0, len(identifiers))

    def test_10_generate_users(self):
        cr, uid = self.cr, self.uid
        hospital_id = self.location_pool.search(cr, uid, [['id', '>', 0]])[0]
        ward_id = self.location_pool.create(cr, uid, {
            'name': 'ward_name', 'parent_id': hospital_id, 'usage': 'ward'})
        bed_id = self.location_pool.create(cr, uid, {
            'name': 'bed_name', 'parent_id': ward_id, 'usage': 'bed'
        })

        # test for correct location
        user_ids = self.api_demo.generate_users(cr, uid, [ward_id, bed_id])
        user = self.user_pool.browse(cr, uid, user_ids['nurse'])
        self.assertEquals(user.location_ids.id, bed_id)
        self.assertEquals(user.location_ids.name, 'bed_name')
        # test for correct login
        doctor = self.user_pool.browse(cr, uid, user_ids['jnr_doctor'])
        self.assertEquals(doctor.login, 'jnr_doctor_' + str(1) + '_' + str(ward_id))
        # test group is properly assigned
        adt = self.user_pool.browse(cr, uid, user_ids['adt'])
        # self.assertIn('NH Clinical Admin Group', [group.name for group in adt.groups_id])
        self.assertIn('Employee', [group.name for group in adt.groups_id])

        # Scenario: create a second ward with unique users
        ward_id_2 = self.location_pool.create(cr, uid, {
            'name': 'ward_name_2', 'parent_id': hospital_id, 'usage': 'ward'})
        bed_id_2 = self.location_pool.create(cr, uid, {
            'name': 'bed_name_2', 'parent_id': ward_id_2, 'usage': 'bed'
        })

        user_ids_2 = self.api_demo.generate_users(cr, uid, [ward_id_2, bed_id_2])
        user_2 = self.user_pool.browse(cr, uid, user_ids_2['nurse'])
        self.assertEquals(user_2.location_ids.id, bed_id_2)
        self.assertEquals(user_2.location_ids.name, 'bed_name_2')
        self.assertNotEquals(user_2.id, user.id)

    def test_11_generate_users_with_multiple_users_of_identical_type(self):
        cr, uid = self.cr, self.uid
        hospital_id = self.location_pool.search(cr, uid, [['id', '>', 0]])[0]
        ward_id = self.location_pool.create(cr, uid, {
            'name': 'ward_name', 'parent_id': hospital_id, 'usage': 'ward'})
        bed_id = self.location_pool.create(cr, uid, {
            'name': 'bed_name', 'parent_id': ward_id, 'usage': 'bed'
        })
        users = {'nurse': 4, 'jnr_doctor': 2}

        # test for 4 nurses
        user_ids = self.api_demo.generate_users(cr, uid, [ward_id, bed_id], data=users)
        nurses = self.user_pool.browse(cr, uid, user_ids['nurse'])
        self.assertEquals(len(nurses), 4)
        self.assertEquals(nurses[0].location_ids.id, bed_id)
        # test for 2 nurses
        doctors = self.user_pool.browse(cr, uid, user_ids['jnr_doctor'])
        self.assertEquals(len(doctors), 2)
        self.assertEquals(doctors[0].location_ids.id, ward_id)
        # test for 1 nurse
        registrar = self.user_pool.browse(cr, uid, user_ids['registrar'])
        self.assertEquals(len(registrar), 1)
        self.assertEquals(registrar[0].location_ids.id, ward_id)

    def test_12_generate_patients(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.api_demo.generate_patients(cr, self.adtuid_ids[0], 10)
        self.assertEquals(10, len(patient_ids))
        # test if gender, sex, ethnicity, names, dob have been assigned.
        for id in patient_ids:
            patient = self.patient_pool.browse(cr, uid, id)
            self.assertIn(patient.gender, ['M', 'F'])
            self.assertIn(patient.sex, ['M', 'F'])
            self.assertIn(patient.ethnicity, [e[0] for e in self.patient_pool._ethnicity])
            self.assertEquals(len(patient.family_name) > 0, True)
            self.assertEquals(len(patient.middle_names) > 0, True)
            self.assertEquals(len(patient.given_name) > 0, True)
            self.assertEquals(len(patient.dob) > 0, True)

        # test for unexpected arguments.
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, self.adtuid_ids[0], 0)))
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, self.adtuid_ids[0], -1)))
        self.assertRaises(TypeError, self.api_demo.generate_patients, cr, self.adtuid_ids[0], "test")

    def test_13_admit_patients(self):
        cr, uid, = self.cr, self.uid

        # create patients and locations, register patients.
        locations = self.api_demo.generate_locations(cr, uid, wards=1, hospital=True)
        location_ids = locations.get('Ward 1')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 10)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}

        # Scenario 1: test patients can be successfully admitted.
        admitted_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids[:5], data)
        self.assertEquals(patient_ids[:5], admitted_patient_ids)

        # Scenario 2: test patients cannot be admitted more than once.
        admitted_patient_ids_2 = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)
        self.assertEquals(admitted_patient_ids_2, patient_ids[5:])
        empty_list = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)
        self.assertEquals(empty_list, [])

    def test_14_place_patients(self):
        cr, uid = self.cr, self.uid

        locations = self.api_demo.generate_locations(cr, uid, wards=3, beds=5, hospital=True)

        # Scenario 1: There are vacant beds for all patients.
        location_ids = locations.get('Ward 1')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 3)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)

        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, location_ids[0])
        self.assertEquals(len(bed_ids), 3)
        ward = self.location_pool.browse(cr, uid, location_ids[0])
        # test the beds have been filled by the patients.
        self.assertEquals(bed_ids, [bed.id for bed in ward.child_ids if not bed.is_available])

        # Scenario 2: There are not enough vacant beds for all patients.
        location_ids = locations.get('Ward 2')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 6)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)

        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, location_ids[0])
        # should be 5 patients placed
        ward = self.location_pool.browse(cr, uid, location_ids[0])
        self.assertEquals(len(bed_ids), 5)
        self.assertEquals(bed_ids, [bed.id for bed in ward.child_ids if not bed.is_available])

        # Scenario 3: There are no beds available.
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 3)
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)
        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, location_ids[0])
        self.assertEquals(len(bed_ids), 0)
        self.assertEquals([], [bed.id for bed in ward.child_ids if bed.is_available])

    def test_15_transfer_patients_will_transfer_patients(self):
        cr, uid = self.cr, self.uid
        locations = self.api_demo.generate_locations(cr, uid, wards=1, beds=4, hospital=True)
        location_ids = locations.get('Ward 1')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 2)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        start_date = '2014-12-31 00:00:00'
        data = {'location': results[0]['code'], 'start_date': start_date}
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)
        res = self.patient_pool.read(cr, uid, admit_patient_ids, ['other_identifier'])
        other_identifiers = [res[0]['other_identifier'], res[1]['other_identifier']]
        objects = self.location_pool.browse(cr, uid, locations.get('Ward 1'))
        codes = [i.code for i in objects]

        hospital_numbers = self.api_demo.transfer_patients(cr, users['adt'][0], other_identifiers, codes)
        self.assertEquals(hospital_numbers, other_identifiers)

    def test_16_discharge_patients_will_discharge_patients(self):
        cr, uid = self.cr, self.uid
        locations = self.api_demo.generate_locations(cr, uid, wards=1, beds=2, hospital=True)
        location_ids = locations.get('Ward 1')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 2)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        start_date = '2014-12-31 00:00:00'
        data = {'location': results[0]['code'], 'start_date': start_date}
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)
        res = self.patient_pool.read(cr, uid, admit_patient_ids, ['other_identifier'])
        other_identifiers = [res[0]['other_identifier'], res[1]['other_identifier']]

        dod = datetime.now().strftime(dtf)
        hospital_numbers = self.api_demo.discharge_patients(cr, users['adt'][0], other_identifiers, {'discharge_date': dod})
        self.assertEquals(hospital_numbers, other_identifiers)

        spell_activity_ids = self.activity_pool.search(cr, uid, [
            ('data_model', '=', 'nh.clinical.spell'),
            ('patient_id', 'in', patient_ids),
            ('state', '=', 'completed')])
        self.assertEquals(len(spell_activity_ids), 2)
        spells = self.activity_pool.browse(cr, uid, spell_activity_ids)
        self.assertTrue(dod == spells[0].date_terminated == spells[1].date_terminated)

    def test_17_generate_news_simulation(self):
        cr, uid = self.cr, self.uid

        locations = self.api_demo.generate_locations(cr, uid, wards=1, beds=3, hospital=True)
        location_ids = locations.get('Ward 1')
        users = self.api_demo.generate_users(cr, uid, location_ids)
        patient_ids = self.api_demo.generate_patients(cr, users['adt'][0], 3)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])
        # generate eobs for 2 days
        start_date = datetime.now() - timedelta(days=2)
        data = {'location': results[0]['code'], 'start_date': start_date}
        admit_patient_ids = self.api_demo.admit_patients(cr, users['adt'][0], patient_ids, data)

        self.api_demo.place_patients(cr, uid, admit_patient_ids, location_ids[0])
        result = self.api_demo.generate_news_simulation(cr, uid, begin_date=datetime.strftime(start_date, dtf),
                                                        patient_ids=admit_patient_ids)
        self.assertEquals(result, True)
        scheduled_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['data_model', '=', 'nh.clinical.patient.observation.ews'],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEquals(len(scheduled_ids), 3)
