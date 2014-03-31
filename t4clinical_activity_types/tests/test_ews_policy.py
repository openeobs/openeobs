from openerp.tests import common
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from faker import Faker

ews_data = {
    'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,    3,    4,   20],
    'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
    'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   91,   91,   91,   91,   91,   91,   91,   99,   99,   91],
    'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
    'BT':       [37.5, 36.5, 36.5, 36.0, 36.0, 36.0, 38.5, 38.5, 38.5, 38.5, 38.5, 35.5, 39.5, 35.0, 35.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
    'BPS':      [ 120,  115,  115,  115,  110,  110,  110,  110,  100,  100,  100,  100,  100,  100,   90,  220,  220,  220,  120,  120,  220],
    'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
    'PR':       [  65,   55,   55,   55,   55,   50,  110,   50,   50,  130,  130,  130,  130,  130,  130,  135,  135,  135,   65,   65,  135],
    'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
}

faker = Faker()

"""
TESTS
case 0 (score 0) -> we expect no notifications
case 1 (score 1-4) -> we expect assess patient notification
case 2.1 (score 5-6) -> we expect urgently inform medical team notification
case 2.2 (three in one) -> we expect urgently inform medical team notification
case 3 (score 7+) -> we expect immediately inform medical team notification

if we submit ews_data[PARAMETER][X] for every parameter in EWS we should obtain a score of X
except for special cases X = 18 and X = 19 which contain score 3 and 4 respectively but with three in one true.
"""

class TestEwsPolicy(common.SingleTransactionCase):

    def setUp(self):
        global cr, uid
        global patient_pool, activity_pool, ews_pool, register_pool, admit_pool, placement_pool, location_pool
        global ews_data

        cr, uid = self.cr, self.uid

        patient_pool = self.registry('t4.clinical.patient')
        activity_pool = self.registry('t4.clinical.activity')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        register_pool = self.registry('t4.clinical.adt.patient.register')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.clinical.activity')
        placement_pool = self.registry('t4.clinical.patient.placement')
        location_pool = self.registry('t4.clinical.location')

        super(TestEwsPolicy, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id

    def test_ews_policy_cases(self):
        global cr, uid
        global patient_pool, activity_pool, ews_pool, register_pool, admit_pool, placement_pool, location_pool
        global ews_data, faker

        adt_uid = self.xml2db_id("demo_user_adt_uhg")
        wm_uid = self.xml2db_id("demo_user_manager")
        hca_uid = self.xml2db_id("demo_user_hca")
        nur_uid = self.xml2db_id("demo_user_nurse")

        gender = faker.random_element(array=('M', 'F'))
        patient_data = {
            'family_name': faker.last_name(),
            'other_identifier': str(faker.random_int(min=1001, max=9999)),
            'dob': faker.date_time_between(start_date="-80y", end_date="-10y").strftime(DTF),
            'gender': gender,
            'sex': gender,
            'given_name': faker.first_name()
        }
        reg_activity_id = register_pool.create_activity(cr, adt_uid, {}, patient_data)
        self.assertTrue(reg_activity_id, msg='Error trying to register patient')
        print "TEST - setting up EWS policy tests - " + "Patient registered."

        patient_domain = [(k, '=', v) for k, v in patient_data.iteritems()]
        patient_id = patient_pool.search(cr, adt_uid, patient_domain)
        self.assertTrue(patient_id, msg='Patient not created')
        patient_id = patient_id[0]
        admit_data = {
            'code': str(faker.random_int(min=10001, max=99999)),
            'other_identifier': patient_data['other_identifier'],
            'location': 'W'+faker.random_element(array=('8', '9')),
            'start_date': faker.date_time_between(start_date="-1w", end_date="-1h").strftime(DTF)
        }
        admit_activity_id = admit_pool.create_activity(cr, adt_uid, {}, admit_data)
        self.assertTrue(admit_activity_id, msg='Error trying to admit patient')
        print "TEST - setting up EWS policy tests - " + "Patient admitted."
        available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
        if admit_data['location'] == 'W8':
            location_ids = location_pool.search(cr, uid, [
                ('code', '=', 'B'+faker.random_element(array=('1', '2', '3', '4'))),
                ('id','in',available_bed_location_ids)])
        else:
            location_ids = location_pool.search(cr, uid, [
                ('code', '=', 'B'+faker.random_element(array=('5', '6', '7', '8'))),
                ('id','in',available_bed_location_ids)])
        #self.assertTrue(location_ids, msg='Location not found')
        if not location_ids:
            print "No available locations found for parent location %s" % admit_data['location']
            return
        location_id = location_ids[0]
        placement_activity_ids = placement_pool.search(cr, uid, [('patient_id', '=', patient_id)])
        self.assertTrue(placement_activity_ids, msg='Placement activity not created')
        placement_id = placement_pool.read(cr, uid, placement_activity_ids[0], ['activity_id'])
        placement_activity_id = placement_id['activity_id'][0]

        activity_pool.submit(cr, wm_uid, placement_activity_id, {'location_id': location_id})

        activity_pool.complete(cr, wm_uid, placement_activity_id)
        print "TEST - setting up EWS policy tests - " + "Patient placement completed."

        for i in range(0, 20):
            print "TEST - EWS policy tests - " + 'Iteration' + str(i)
            ews_ids = ews_pool.search(cr, uid, [('patient_id', '=', patient_id), ('state', '=', 'scheduled')])
#             if not ews_ids:
#                 import pdb; pdb.set_trace()
            self.assertTrue(ews_ids, msg='EWS activity not created')
            ews_id = ews_pool.read(cr, uid, ews_ids[0], ['activity_id'])
            ews_activity_id = ews_id['activity_id'][0]
            ews = {
                'respiration_rate': ews_data['RR'][i],
                'indirect_oxymetry_spo2': ews_data['O2'][i],
                'oxygen_administration_flag': ews_data['O2_flag'][i],
                'body_temperature': ews_data['BT'][i],
                'blood_pressure_systolic': ews_data['BPS'][i],
                'blood_pressure_diastolic': ews_data['BPD'][i],
                'pulse_rate': ews_data['PR'][i],
                'avpu_text': ews_data['AVPU'][i]
            }
            activity_pool.submit(cr, nur_uid, ews_activity_id, ews)
            activity_pool.start(cr, nur_uid, ews_activity_id)
            activity_pool.complete(cr, nur_uid, ews_activity_id)
            ews_activity = activity_pool.browse(cr, uid, ews_activity_id)
            self.assertTrue(ews_activity.data_ref.score == ews_data['SCORE'][i], msg='Score not matching')
            activity_ids = activity_pool.search(cr, nur_uid, [('state', '=', 'scheduled')])
            self.assertTrue(activity_ids)