from openerp.tests import common
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from faker import Faker

faker = Faker()


class TestObservations(common.SingleTransactionCase):

    def setUp(self):
        global cr, uid
        global patient_pool, activity_pool, weight_pool, register_pool, admit_pool, placement_pool, location_pool
        global blood_product_pool, blood_sugar_pool, stools_pool
        global faker, patient_id, nur_uid

        cr, uid = self.cr, self.uid

        patient_pool = self.registry('t4.clinical.patient')
        activity_pool = self.registry('t4.activity')
        weight_pool = self.registry('t4.clinical.patient.observation.weight')
        register_pool = self.registry('t4.clinical.adt.patient.register')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.activity')
        placement_pool = self.registry('t4.clinical.patient.placement')
        location_pool = self.registry('t4.clinical.location')
        blood_product_pool = self.registry('t4.clinical.patient.observation.blood_product')
        blood_sugar_pool = self.registry('t4.clinical.patient.observation.blood_sugar')
        stools_pool = self.registry('t4.clinical.patient.observation.stools')

        super(TestObservations, self).setUp()

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
        print "TEST - setting up Observations tests - " + "Patient registered."

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
        print "TEST - setting up Observations tests - " + "Patient admitted."
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
        print "TEST - setting up Observations tests - " + "Patient placement completed."

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id

    def test_weight_observation(self):
        global cr, uid
        global activity_pool, weight_pool
        global faker, patient_id, nur_uid

        weight_activity_id = weight_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.assertTrue(weight_activity_id, msg='Weight Observation activity not created')
        weight = float(faker.random_int(min=40, max=200))
        activity_pool.submit(cr, nur_uid, weight_activity_id, {'weight': weight})
        activity_pool.complete(cr, nur_uid, weight_activity_id)
        self.assertTrue(activity_pool.browse(cr, uid, weight_activity_id).data_ref.weight == weight)
        
    def test_blood_product_observation(self):
        global cr, uid
        global activity_pool, blood_product_pool
        global faker, patient_id, nur_uid

        blood_product_activity_id = blood_product_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.assertTrue(blood_product_activity_id, msg='Blood product Observation activity not created')
        vol = float(faker.random_int(min=1, max=10))
        product = faker.random_element(array=('rbc', 'ffp', 'platelets', 'has', 'dli', 'stem'))
        activity_pool.submit(cr, nur_uid, blood_product_activity_id, {'vol': vol, 'product': product})
        activity_pool.complete(cr, nur_uid, blood_product_activity_id)
        blood_product = activity_pool.browse(cr, uid, blood_product_activity_id)
        self.assertTrue(blood_product.data_ref.vol == vol)
        self.assertTrue(blood_product.data_ref.product == product)
        
    def test_blood_sugar_observation(self):
        global cr, uid
        global activity_pool, blood_sugar_pool
        global faker, patient_id, nur_uid

        blood_sugar_activity_id = blood_sugar_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.assertTrue(blood_sugar_activity_id, msg='Blood sugar Observation activity not created')
        blood_sugar = float(faker.random_int(min=1, max=100))
        activity_pool.submit(cr, nur_uid, blood_sugar_activity_id, {'blood_sugar': blood_sugar})
        activity_pool.complete(cr, nur_uid, blood_sugar_activity_id)
        self.assertTrue(activity_pool.browse(cr, uid, blood_sugar_activity_id).data_ref.blood_sugar == blood_sugar)
        
    def test_stools_observation(self):
        global cr, uid
        global activity_pool, stools_pool
        global faker, patient_id, nur_uid

        stools_activity_id = stools_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.assertTrue(stools_activity_id, msg='Bristol stools Observation activity not created')
        stools_data = {
            'bowel_open': faker.random_int(min=0, max=1),
            'nausea': faker.random_int(min=0, max=1),
            'vomiting': faker.random_int(min=0, max=1),
            'quantity': faker.random_element(array=('large', 'medium', 'small')),
            'colour': faker.random_element(array=('brown', 'yellow', 'green', 'black', 'red', 'clay')),
            'bristol_type': str(faker.random_int(min=1, max=7)),
            'offensive': faker.random_int(min=0, max=1),
            'strain': faker.random_int(min=0, max=1),
            'laxatives': faker.random_int(min=0, max=1),
            'samples': faker.random_element(array=('none', 'micro', 'virol', 'm+v')),
            'rectal_exam': faker.random_int(min=0, max=1),
        }
        activity_pool.submit(cr, nur_uid, stools_activity_id, stools_data)
        activity_pool.complete(cr, nur_uid, stools_activity_id)
        stools = activity_pool.browse(cr, uid, stools_activity_id)
        self.assertTrue(stools.data_ref.bowel_open == bool(stools_data['bowel_open']))
        self.assertTrue(stools.data_ref.nausea == bool(stools_data['nausea']))
        self.assertTrue(stools.data_ref.vomiting == bool(stools_data['vomiting']))
        self.assertTrue(stools.data_ref.quantity == stools_data['quantity'])
        self.assertTrue(stools.data_ref.colour == stools_data['colour'])
        self.assertTrue(stools.data_ref.bristol_type == stools_data['bristol_type'])
        self.assertTrue(stools.data_ref.offensive == bool(stools_data['offensive']))
        self.assertTrue(stools.data_ref.strain == bool(stools_data['strain']))
        self.assertTrue(stools.data_ref.laxatives == bool(stools_data['laxatives']))
        self.assertTrue(stools.data_ref.samples == stools_data['samples'])
        self.assertTrue(stools.data_ref.rectal_exam == bool(stools_data['rectal_exam']))