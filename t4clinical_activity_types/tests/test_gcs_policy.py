from openerp.tests import common
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from faker import Faker

gcs_data = {
    'SCORE':    [   3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15],
    'EYES':     [ '1',  'C',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '4',  '4',  '4',  '4'],
    'VERBAL':   [ '1',  'T',  '1',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '5',  '5'],
    'MOTOR':    [ '1',  '2',  '2',  '2',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '6'],
}

faker = Faker()


class TestGcsPolicy(common.SingleTransactionCase):

    def setUp(self):
        global cr, uid
        global patient_pool, activity_pool, gcs_pool, register_pool, admit_pool, placement_pool, location_pool
        global gcs_data

        cr, uid = self.cr, self.uid

        patient_pool = self.registry('t4.clinical.patient')
        activity_pool = self.registry('t4.clinical.activity')
        gcs_pool = self.registry('t4.clinical.patient.observation.gcs')
        register_pool = self.registry('t4.clinical.adt.patient.register')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.clinical.activity')
        placement_pool = self.registry('t4.clinical.patient.placement')
        location_pool = self.registry('t4.clinical.location')

        super(TestGcsPolicy, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id

    def test_ews_policy_cases(self):
        global cr, uid
        global patient_pool, activity_pool, gcs_pool, register_pool, admit_pool, placement_pool, location_pool
        global gcs_data, faker

        adt_uid = self.xml2db_id("demo_user_adt_uhg")
        wm_uid = self.xml2db_id("demo_user_manager")
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
        print "TEST - setting up GCS policy tests - " + "Patient registered."

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
        activity_pool.complete(cr, adt_uid, admit_activity_id)
        print "TEST - setting up GCS policy tests - " + "Patient admitted."
        available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
        if admit_data['location'] == 'W8':
            location_ids = location_pool.search(cr, uid, [
                ('code', '=', 'B'+faker.random_element(array=('1', '2', '3', '4'))),
                ('id','in',available_bed_location_ids)])
        else:
            location_ids = location_pool.search(cr, uid, [
                ('code', '=', 'B'+faker.random_element(array=('5', '6', '7', '8'))),
                ('id','in',available_bed_location_ids)])
        # self.assertTrue(location_ids, msg='Location not found')
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
        print "TEST - setting up GCS policy tests - " + "Patient placement completed."

        for i in range(0, 13):
            gcs = {
                'eyes': gcs_data['EYES'][i],
                'verbal': gcs_data['VERBAL'][i],
                'motor': gcs_data['MOTOR'][i]
            }
            print "TEST - GCS policy tests - " + 'Iteration ' + str(i) + ' score: ' + str(gcs_data['SCORE'][i])
            gcs_ids = gcs_pool.search(cr, uid, [('patient_id', '=', patient_id), ('state', '=', 'scheduled')])
            self.assertTrue(gcs_ids, msg='GCS activity not created')
            gcs_id = gcs_pool.read(cr, uid, gcs_ids[0], ['activity_id'])
            gcs_activity_id = gcs_id['activity_id'][0]
            activity_pool.submit(cr, nur_uid, gcs_activity_id, gcs)
            activity_pool.start(cr, nur_uid, gcs_activity_id)
            activity_pool.complete(cr, nur_uid, gcs_activity_id)
            gcs_activity = activity_pool.browse(cr, uid, gcs_activity_id)
            self.assertTrue(gcs_activity.data_ref.score == gcs_data['SCORE'][i], msg='Score not matching')
            activity_ids = activity_pool.search(cr, nur_uid, [('state', '=', 'scheduled')])
            self.assertTrue(activity_ids)