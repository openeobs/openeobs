from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
#from t4_base.tools import xml2db_id

from openerp import tools
from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.tests.test_base import BaseTest

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


class ADTTest(BaseTest):
 
    def setUp(self):
        global cr, uid, \
                register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool, user_pool, imd_pool
               
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        
        cr, uid = self.cr, self.uid
  
        
        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.clinical.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        api_pool = self.registry('t4.clinical.api')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        
        super(ADTTest, self).setUp()
    
    
    
    def test_adt(self):        
        
        env = self.create_environment()
        
        env = self.adt_patient_register()
        
        
        
        
    def adt_patient_register(self, activity_vals={}, data_vals={}, env={}):
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        fake.seed(next_seed()) 
        gender = data_vals.get('gender') or fake.random_element(array=('M','F'))
        other_identifier = data_vals.get('other_identifier') or str(fake.random_int(min=1000001, max=9999999))
        dob = data_vals.get('dob') or fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")
        data = {
                'family_name': data_vals.get('family_name') or fake.last_name(), 
                'given_name': data_vals.get('given_name') or fake.first_name(),
                'other_identifier': other_identifier, 
                'dob': dob, 
                'gender': gender, 
                'sex': gender         
                }
        # create
        ##############
        duplicate_ids = patient_pool.search(cr, uid, [['other_identifier','=',data['other_identifier']]])
        register_activity_id = self.create_activity(cr, adt_user_id, register_pool._name, {}, {})

        # submit
        ##############
        register_submit_res = self.submit(cr, adt_user_id, register_activity_id, data)
        register_activity = activity_pool.browse(cr, uid, register_activity_id)
        adt_user = user_pool.browse(cr, uid, adt_user_id)
        patient_ids = patient_pool.search(cr, uid, [['other_identifier','=',data['other_identifier']]])
        # submit tests
        self.assertTrue(register_activity.pos_id.id == adt_user.pos_id.id,
                        "activity.pos_id (%s) != adt_user.pos_id (%s)" 
                        % (register_activity.pos_id.id, adt_user.pos_id.id))        
        self.assertTrue(not register_activity.parent_id,
                        "activity.parent_id (%s) is not False" 
                        % (register_activity.parent_id.id))  
        self.assertTrue(not register_activity.location_id,
                        "activity.location_id (%s) is not False" 
                        % (register_activity.location_id.id)) 
        self.assertTrue(not register_activity.user_ids,
                        "activity.user_ids (%s) is not False" 
                        % (register_activity.user_ids))
        #duplicate_ids = [-1]
        self.assertTrue(not duplicate_ids and True or duplicate_ids == patient_ids,
                        "duplicate_ids and duplicate_ids == patient_ids is False\nduplicate_ids: %s\npatient_ids: %s" 
                        % (duplicate_ids, patient_ids))
        #patient_ids.append(-1) # patient_ids[0] = -1
        self.assertTrue(not duplicate_ids and len(patient_ids) == 1 and patient_ids[0] == register_activity.patient_id.id,
                        """not duplicate_ids and len(patient_ids) == 1 and patient_ids[0] == activity.patient_id is 
                        False\nactivity.patient_id: %s\npatient_ids: %s"""
                        % (register_activity.patient_id.id, patient_ids))
        # complete
        ##############
        register_complete_res = self.complete(cr, adt_user_id, register_activity_id)
        
        # return
        ##############
        
        
        env['patient_ids'].append(register_activity.patient_id.id)
        #import pdb; pdb.set_trace()
        return env
    
    def adt_patient_admit(self, activity_vals={}, data_vals={}, env={}):      
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        res = {}
        fake.seed(next_seed()) 
        data = {}
        if not data_vals.get('other_identifier'):
            
        data['other_identifier'] = data_vals.get('other_identifier') or other_identifier
        data['location'] = data_vals.get('suggested_location') or suggested_location
        data['code'] = str(fake.random_int(min=10001, max=99999))
        data['start_date'] = fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
        admit_activity_id = admit_pool.create_activity(cr, uid, {}, {})
        admit_submit_res = activity_pool.submit(cr, uid, admit_activity_id, data)
        admit_complete_res = activity_pool.complete(cr, uid, admit_activity_id)
        
        # create
        ##############
        duplicate_ids = patient_pool.search(cr, uid, [['other_identifier','=',data['other_identifier']]])
        register_activity_id = self.create_activity(cr, adt_user_id, register_pool._name, {}, {})

        # submit
        ##############
        register_submit_res = self.submit(cr, adt_user_id, register_activity_id, data)
        register_activity = activity_pool.browse(cr, uid, register_activity_id)
        adt_user = user_pool.browse(cr, uid, adt_user_id)
        patient_ids = patient_pool.search(cr, uid, [['other_identifier','=',data['other_identifier']]])
        # submit tests

        # complete
        ##############
        register_complete_res = self.complete(cr, adt_user_id, register_activity_id)
        
        # return
        ##############
        
        res.update({'register_activity_id': register_activity_id})
        res.update(register_submit_res)
        res.update(register_complete_res)

        #import pdb; pdb.set_trace()
        return res  
        
    def create_environment(self, WARD_QTY=5, BED_PER_WARD=3):
        """
        creates 1 pos environment
        """

        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
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
        
        res = {'pos_id': [pos_id],
               'adt_user_id': [adt_user_id],
               'bed_location_ids': bed_location_ids,
               'ward_location_ids': ward_location_ids,
               'nurse_user_ids': nurse_user_ids,
               'pateint_ids': [],
               }
        return res
