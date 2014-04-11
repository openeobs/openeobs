from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)
def next_seed():
    global seed
    seed += 1
    return seed

class BaseTest(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, type_pool
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
    
        cr, uid = self.cr, self.uid
              
        patient_pool = self.registry('t4.clinical.patient')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        activity_pool = self.registry('t4.clinical.activity')
        type_pool = self.registry('t4.clinical.activity.type')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        
        super(BaseTest, self).setUp()
        
    def create_activity(self, cr, uid, data_model, vals_activity={}, vals_data={}, context=None):
        model_pool = self.registry(data_model)
        activity_id = model_pool.create_activity(cr, uid, vals_activity, vals_data, context)
        _logger.info("Activity created id=%s, data_model=%s\n vals_activity: %s\n vals_data: %s" 
                     % (activity_id, data_model, vals_activity, vals_data))
        activity = activity_pool.browse(cr, uid, activity_id)
        activity_type_id = type_pool.search(cr, uid, [['data_model','=',data_model]])[0]

        # tests
        self.assertTrue(activity.state == "new", 
                        "activity.state (%s) != 'new'" 
                        % (activity.state)) 
        self.assertTrue(activity.data_model == model_pool._name, 
                        "activity.data_model (%s) != model_pool._name (%s)" 
                        % (activity.data_model, model_pool._name))        
        self.assertTrue(activity.type_id != activity_type_id, 
                        "activity.type_id (%s) != type.id (%s)" 
                        % (activity.type_id, activity_type_id))
        return activity_id
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        res = activity_pool.submit(cr, uid, activity_id, vals, context)
        # tests
        activity = activity_pool.browse(cr, uid, activity_id)
        model_pool = self.registry(activity.data_model)
        activity_data = model_pool.read(cr, uid, activity.data_ref.id,[])
        self.assertTrue(set(vals.keys()) <= set(activity_data.keys()), 
                        "vals is not a subset of activity data. \n vals: %s\n activity data: %s" 
                        % (vals, activity))         

        return res
    
    def complete(self, cr, uid, activity_id, context=None):    
        res = activity_pool.complete(cr, uid, activity_id, context)
        return res       
     
    def create_environment(self): 
        WARD_QTY = 5
        BED_PER_WARD = 3
        
        _logger.info("Executing create_environment()")
        # Create POS
        pos_id = self.create_pos()
        pos = pos_pool.browse(cr, uid, pos_id)

        # Create wards
        ward_location_ids = [self.create_ward(pos.location_id.id) for i in range(WARD_QTY)]
         
        # Create beds 
        bed_location_ids = []
        for ward_location_id in ward_location_ids:
            bed_location_ids.extend([self.create_bed(ward_location_id) for i in range(BED_PER_WARD)])
         
        # Create ADT user
        adt_user = user_pool.browse(cr, uid, self.create_adt_user(pos.id))
        adt_user_id = adt_user.id
         
        # Create nurse users
        nurse_user_ids = [
             self.create_nurse_user(ward_location_ids),
             self.create_nurse_user(ward_location_ids)
         ]

    def create_nurse_user(self, location_ids):
        fake.seed(next_seed())
        nurse_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")   
        name = fake.first_name() 
        data = {
            'name': "Nurse %s" % name,
            'login': name.lower(),
            'password': name.lower(),
            'groups_id': [(4, nurse_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        #import pdb; pdb.set_trace()
        user_id = user_pool.create(cr, uid, data)
        _logger.info("Nurse user created id=%s\n data: %s" % (user_id, data))
        return user_id  

    def create_adt_user(self, pos_id):
        fake.seed(next_seed())
        adt_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")  
        pos = pos_pool.browse(cr, uid, pos_id) 
        data = {
            'name': "ADT user for %s" % pos.name,
            'login': "adt_%s" % pos.location_id.code.lower(),
            'password': "adt_%s" % pos.location_id.code.lower(),
            'groups_id': [(4, adt_group.id)],
            'pos_id': pos_id
        }
        user_id = user_pool.create(cr, uid, data)
        _logger.info("ADT user created id=%s\n data: %s" % (user_id, data))
        return user_id

    def create_bed(self, parent_id):
        fake.seed(next_seed()) 
        code = "B"+str(fake.random_int(min=100, max=999))
        data = {'name': code, 'code': code, 'type': 'poc', 'usage': 'bed', 'parent_id': parent_id}
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Bed location created id=%s\n data: %s" % (location_id, data))
        return location_id
        
    def create_ward(self, parent_id):
        fake.seed(next_seed()) 
        code = "W"+str(fake.random_int(min=100, max=999))
        data = {'name': code, 'code': code, 'type': 'poc', 'usage': 'ward', 'parent_id': parent_id}
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Ward location created id=%s\n data: %s" % (location_id, data))
        return location_id        
    
    def create_pos(self):
        fake.seed(next_seed())
        # POS location 
        code = "POS"+str(fake.random_int(min=1, max=9))
        data = {'name': "POS Location (%s)" % code, 'code': code, 'type': 'pos', 'usage': 'hospital'}
        pos_location_id = location_pool.create(cr, uid, data)
        _logger.info("POS location created id=%s\n data: %s" % (pos_location_id, data))
        # Admission location
        data = {'name': "Admission Location (%s)" % code, 
                'code': "ADML-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_admission_id = location_pool.create(cr, uid, data)
        _logger.info("Admission location created id=%s\n data: %s" % (lot_admission_id, data))
        # Discharge Location
        data = {'name': "Discharge Location (%s)" % code, 
                'code': "DISL-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_discharge_id = location_pool.create(cr, uid, data)   
        _logger.info("Discharge location created id=%s\n data: %s" % (lot_discharge_id, data))             
        # POS        
        data = {'name': "HOSPITAL"+str(fake.random_int(min=1, max=9)),
                'location_id': pos_location_id,
                'lot_admission_id': lot_admission_id,
                'lot_discharge_id': lot_discharge_id}
        pos_id = pos_pool.create(cr, uid, data)
        _logger.info("POS created id=%s\n data: %s" % (pos_id, data))
        return pos_id