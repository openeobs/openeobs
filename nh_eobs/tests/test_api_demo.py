import logging
from openerp.fields import datetime

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

    def test_generate_patients(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.api_demo.generate_patients(cr, uid, 10)
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
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, uid)))
        self.assertEquals(0, len(self.api_demo.generate_patients(cr, uid, -1)))
        self.assertRaises(TypeError, self.api_demo.generate_patients, cr, uid, "test")

    def test_generate_locations(self):
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

    def test_generate_users(self):
        cr, uid = self.cr, self.uid
        hospital_id = self.location_pool.search(cr, uid, [['id', '>', 0]])[0]
        ward_id = self.location_pool.create(cr, uid, {
            'name': 'ward_name', 'parent_id': hospital_id})

        # test for correct location
        user_ids = self.api_demo.generate_users(cr, uid, ward_id)
        user = self.user_pool.browse(cr, uid, user_ids['nurse'])
        self.assertEquals(user.location_ids.id, ward_id)
        self.assertEquals(user.location_ids.name, 'ward_name')
        # test for correct login
        doctor = self.user_pool.browse(cr, uid, user_ids['jnr_doctor'])
        self.assertEquals(doctor.login, 'jnr_doctor_' + str(ward_id))
        # test group is properly assigned
        adt = self.user_pool.browse(cr, uid, user_ids['adt'])
        self.assertIn('NH Clinical ADT Group', [group.name for group in adt.groups_id])

        # Scenario: create a second ward with unique users
        ward_id_2 = self.location_pool.create(cr, uid, {
            'name': 'ward_name_2', 'parent_id': hospital_id})
        user_ids_2 = self.api_demo.generate_users(cr, uid, ward_id_2)
        user_2 = self.user_pool.browse(cr, uid, user_ids_2['nurse'])
        self.assertEquals(user_2.location_ids.id, ward_id_2)
        self.assertEquals(user_2.location_ids.name, 'ward_name_2')
        self.assertNotEquals(user_2.id, user.id)

    def test_admit_patients(self):
        cr, uid, = self.cr, self.uid

        # create and register patients
        patient_ids = self.api_demo.generate_patients(cr, uid, 10)
        # create location
        locations = self.api_demo.generate_locations(cr, uid, wards=1, hospital=True)
        ward_id = locations.get('Ward 1')[0]
        users = self.api_demo.generate_users(cr, uid, ward_id)
        results = self.location_pool.read(cr, uid, [ward_id], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}

        admitted_patient_ids = self.api_demo.admit_patients(cr, uid, patient_ids[:5], users['adt'], data)
        self.assertEquals(patient_ids[:5], admitted_patient_ids)

        # test that admitted patients are not admitted again
        admitted_patient_ids_2 = self.api_demo.admit_patients(cr, uid, patient_ids, users['adt'], data)
        self.assertEquals(admitted_patient_ids_2, patient_ids[5:])
        empty_list = self.api_demo.admit_patients(cr, uid, patient_ids, users['adt'], data)
        self.assertEquals(empty_list, [])

    def test_place_patients(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.api_demo.generate_patients(cr, uid, 10)
        locations = self.api_demo.generate_locations(cr, uid, wards=3, beds=5, hospital=True)

        # Scenario 1: There are vacant beds for all patients.
        p_ids = patient_ids[:3]     # get first 3 patients
        ward_id = locations.get('Ward 1')[0]
        users = self.api_demo.generate_users(cr, uid, ward_id)
        results = self.location_pool.read(cr, uid, [ward_id], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}
        admit_patient_ids = self.api_demo.admit_patients(cr, uid, p_ids, users['adt'], data)

        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, ward_id)
        self.assertEquals(len(bed_ids), 3)
        ward = self.location_pool.browse(cr, uid, ward_id)
        # test the beds have been filled by the patients.
        self.assertEquals(bed_ids, [bed.id for bed in ward.child_ids if not bed.is_available])

        # Scenario 2: There are not enough vacant beds for all patients.
        p_ids = patient_ids[3:9]    # get next 6 patients
        ward_id = locations.get('Ward 2')[0]
        users = self.api_demo.generate_users(cr, uid, ward_id)
        results = self.location_pool.read(cr, uid, [ward_id], ['code'])
        data = {'location': results[0]['code'], 'start_date': datetime.now()}
        admit_patient_ids = self.api_demo.admit_patients(cr, uid, p_ids, users['adt'], data)

        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, ward_id)
        # should be 5 patients placed
        ward = self.location_pool.browse(cr, uid, ward_id)
        self.assertEquals(len(bed_ids), 5)
        self.assertEquals(bed_ids, [bed.id for bed in ward.child_ids if not bed.is_available])

        # Scenario 3: There are no beds available.
        p_ids = patient_ids[9:]
        admit_patient_ids = self.api_demo.admit_patients(cr, uid, p_ids, users['adt'], data)
        bed_ids = self.api_demo.place_patients(cr, uid, admit_patient_ids, ward_id)
        self.assertEquals(len(bed_ids), 0)
        self.assertEquals([], [bed.id for bed in ward.child_ids if bed.is_available])


