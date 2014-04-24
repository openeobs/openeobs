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


class ActivityTypesScenarioTest(BaseTest):
 
    def setUp(self):
        global cr, uid, \
               register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool, user_pool, imd_pool, discharge_pool
        
        cr, uid = self.cr, self.uid

        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        activity_pool = self.registry('t4.clinical.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        api_pool = self.registry('t4.clinical.api')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        
        
        super(ActivityTypesScenarioTest, self).setUp()
    
    
    
    def test_scenario(self):        
        # environment
        pos1_env = self.create_pos_environment()
        # register
        [self.adt_patient_register(env=pos1_env) for i in range(3)]
        # admit
        [self.adt_patient_admit(data_vals={'patient_id':patient_id}, env=pos1_env) for patient_id in pos1_env['patient_ids']]
        # placement
        [self.patient_placement(data_vals={'patient_id': patient_id}, env=pos1_env) for patient_id in pos1_env['patient_ids']]
        # discharge
        [self.patient_discharge(data_vals={'patient_id':patient_id}, env=pos1_env) for patient_id in pos1_env['patient_ids']]
        
        
    def adt_patient_register(self, activity_vals={}, data_vals={}, env={}):
        #global pos_id, ward_location_ids, bed_location_ids, env['adt_user_id'], nurse_user_ids
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
        register_activity_id = self.create_activity(cr, env['adt_user_id'], register_pool._name, {}, {})

        # submit
        ##############
        self.submit(cr, env['adt_user_id'], register_activity_id, data)
        register_activity = activity_pool.browse(cr, uid, register_activity_id)
        adt_user = user_pool.browse(cr, uid, env['adt_user_id'])
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
        self.complete(cr, env['adt_user_id'], register_activity_id)
        
        # return
        ##############
        env['patient_ids'] = []
        env['patient_ids'].append(register_activity.patient_id.id)
        env['other_identifiers'] = []
        env['other_identifiers'].append(other_identifier)        
        #import pdb; pdb.set_trace()
        return env
    
    def patient_discharge(self, activity_vals={}, data_vals={}, env={}):      
        fake.seed(next_seed()) 
        data = {}
        #if not data_vals.get('other_identifier'):
        self.assertTrue(data_vals.get('patient_id') or env.get('patient_ids'),
                       "patient_id is not submitted!")                
        
        data['patient_id'] = data_vals.get('patient_id') or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        # create
        ##############
        discharge_activity_id = self.create_activity(cr, uid, discharge_pool._name, {}, {})
         
        # submit
        ##############
        discharge_submit_res = self.submit(cr, uid, discharge_activity_id, data)
        #import pdb; pdb.set_trace()
        pos_id = discharge_pool.get_activity_pos_id(cr, uid, discharge_activity_id)
        # submit tests
        discharge_activity = activity_pool.browse(cr, uid, discharge_activity_id)
        
        self.assertTrue(discharge_activity.patient_id,
                       "patient_id is not set after data submission!")
        self.assertTrue(discharge_activity.pos_id,
                       "pos_id is not set after data submission!")
        self.assertTrue(discharge_activity.location_id,
                       "location_id is not set after data submission!")
        #import pdb; pdb.set_trace()
        discharge_complete_res = activity_pool.complete(cr, uid, discharge_activity_id)

        return env
        
    def adt_patient_admit(self, activity_vals={}, data_vals={}, env={}):      
        fake.seed(next_seed()) 
        data = {}
        self.assertTrue(data_vals.get('other_identifier') or env['other_identifiers'],
                       "other_identifier is not submitted/available!")
        self.assertTrue(data_vals.get('suggested_location') or env['ward_location_ids'],
                       "suggested_location is not submitted/available!")                 
        data['other_identifier'] = data_vals.get('other_identifier') \
                                    or env['other_identifiers'][fake.random_int(min=0, max=len(env['other_identifiers'])-1)]
        data['location'] = data_vals.get('suggested_location') \
                                    or location_pool.browse(cr, uid, 
                                        env['ward_location_ids'][fake.random_int(min=0, max=len(env['ward_location_ids'])-1)]).name
        data['code'] = str(fake.random_int(min=10001, max=99999))
        data['start_date'] = fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
        admit_activity_id = self.create_activity(cr, env['adt_user_id'], admit_pool._name, {}, {})
        #import pdb; pdb.set_trace()
        # submit
        ##############
        self.submit(cr, env['adt_user_id'], admit_activity_id, data)
        admit_activity = activity_pool.browse(cr, uid, admit_activity_id)
        patient_ids = patient_pool.search(cr, env['adt_user_id'], [['other_identifier','=',data['other_identifier']]])
        location_id = location_pool.search(cr, env['adt_user_id'], [['name','=',data['location']]])[0]
        # submit tests
        self.assertTrue(admit_activity.patient_id.id in patient_ids,
                       "patient_id is either not set (correctly) after data submission!")
        self.assertTrue(admit_activity.pos_id,
                       "pos_id is not set after data submission!")
        self.assertTrue(not admit_activity.location_id,
                       "location_id is set after data submission, but must be False!")        
        # complete
        ##############
        self.complete(cr, env['adt_user_id'], admit_activity_id)
        # admission tests
        admission_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.admission'],
                                                               ['creator_id','=',admit_activity_id]])

        admission_activity_id = admission_activity_id and admission_activity_id[0]
        self.assertTrue(admission_activity_id,
                       "admission_activity not found after adt.admit completion!")
        admission_activity = activity_pool.browse(cr, uid, admission_activity_id)
        self.assertTrue(admission_activity.state == 'completed',
                       "admission_activity.state != 'completed' after adt.admit completion!")
        self.assertTrue(admission_activity.patient_id.id == admit_activity.patient_id.id,
                       "admission_activity.patient_id != admit_activity.patient_id after adt.admit completion!")        
        self.assertTrue(admission_activity.pos_id.id == admit_activity.pos_id.id,
                       "admission_activity.pos_id != admit_activity.pos_id after adt.admit completion!") 
        self.assertTrue(admission_activity.location_id.id == admit_activity.pos_id.lot_admission_id.id,
                       "admission_activity.location_id != admit_activity.pos_id.lot_admission_id after adt.admit completion!")
        # spell test
        spell_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.spell'],
                                                           ['creator_id','=',admission_activity_id]])   
        spell_activity_id = spell_activity_id and spell_activity_id[0]
        self.assertTrue(spell_activity_id,
                       "spell_activity not found after adt.admit completion!")  
        self.assertTrue(admission_activity.parent_id.id == spell_activity_id,
                       "admission_activity.parent_id != spell_activity_id after adt.admit completion!")
        spell_activity = activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(spell_activity.state == 'started',
                       "spell_activity.state != 'started' after adt.admit completion!")             
        self.assertTrue(spell_activity.patient_id.id == admit_activity.patient_id.id,
                       "spell_activity.patient_id != admit_activity.patient_id after adt.admit completion!")        
        self.assertTrue(spell_activity.pos_id.id == admit_activity.pos_id.id,
                       "spell_activity.pos_id != admit_activity.pos_id after adt.admit completion!") 
        self.assertTrue(spell_activity.location_id.id == admission_activity.pos_id.lot_admission_id.id,
                       "spell_activity.location_id != admission_activity.pos_id.lot_admission_id after adt.admit completion!")
        # move test
        move_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.move'],
                                                           ['creator_id','=',admission_activity_id]])   
        move_activity_id = move_activity_id and move_activity_id[0]
        self.assertTrue(move_activity_id,
                       "move_activity not found after adt.admit completion!")  
        move_activity = activity_pool.browse(cr, uid, move_activity_id)
        self.assertTrue(move_activity.parent_id.id == spell_activity_id,
                       "move_activity.parent_id != spell_activity_id after adt.admit completion!")
        self.assertTrue(move_activity.state == 'completed',
                       "move_activity.state != 'completed' after adt.admit completion!")             
        self.assertTrue(move_activity.patient_id.id == spell_activity.patient_id.id,
                       "move_activity.patient_id != spell_activity.patient_id after adt.admit completion!")        
        self.assertTrue(move_activity.pos_id.id == spell_activity.pos_id.id,
                       "move_activity.pos_id != spell_activity.pos_id after adt.admit completion!") 
        self.assertTrue(move_activity.location_id.id == api_pool.get_patient_current_location_id(cr, uid, move_activity.patient_id.id),
                       "move_activity.location_id != admission_activity.pos_id.lot_admission_id after adt.admit completion!")        

        # placement test
        placement_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.placement'],
                                                               ['creator_id','=',admission_activity_id]])   
        placement_activity_id = placement_activity_id and placement_activity_id[0]
        self.assertTrue(placement_activity_id,
                       "placement_activity not found after adt.admit completion!")  
        placement_activity = activity_pool.browse(cr, uid, placement_activity_id)
        self.assertTrue(placement_activity.parent_id.id == spell_activity_id,
                       "placement_activity.parent_id != spell_activity_id after adt.admit completion!")
        self.assertTrue(placement_activity.state == 'new',
                       "placement_activity.state != 'new' after adt.admit completion!")             
        self.assertTrue(placement_activity.patient_id.id == spell_activity.patient_id.id,
                       "placement_activity.patient_id != spell_activity.patient_id after adt.admit completion!")        
        self.assertTrue(placement_activity.pos_id.id == spell_activity.pos_id.id,
                       "placement_activity.pos_id != spell_activity.pos_id after adt.admit completion!") 
  
        
        return env

    def patient_placement(self, activity_vals={}, data_vals={}, env={}):
        data = {}
        data['patient_id'] = data_vals.get('patient_id') or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
        data['location_id'] = data_vals.get('location_id') or available_bed_location_ids[fake.random_int(min=0, max=len(available_bed_location_ids)-1)]
        placement_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.placement'],
                                                               ['patient_id','=',data['patient_id']],
                                                               ['state','in',['new','started','scheduled']]])
        placement_activity_id = placement_activity_id and placement_activity_id[0]
        self.assertTrue(placement_activity_id,
                       "placement_activity not found in patient_placement() for patient_id=%s" % (data['patient_id']))         
        placement_activity = activity_pool.browse(cr, uid, placement_activity_id)
        spell_activity = placement_activity.parent_id
        self.assertTrue(spell_activity.data_model == 't4.clinical.spell',
                       "parent_id is not spell")          
        self.assertTrue(spell_activity.patient_id.id == data['patient_id'],
                       "spell.patient_id != pateint_id")   
        # submit
        ##############
        activity_pool.submit(cr, uid, placement_activity_id, data)
        self.assertTrue(placement_activity.patient_id.id == spell_activity.patient_id.id,
                       "placement_activity.patient_id != spell_activity.patient_id after")        
        self.assertTrue(placement_activity.pos_id.id == spell_activity.pos_id.id,
                       "placement_activity.pos_id != spell_activity.pos_id") 
        self.assertTrue(placement_activity.location_id.id == placement_activity.data_ref.suggested_location_id.id,
                       "placement_activity.location_id != placement_activity.data_ref.suggested_location_id") 
        # complete
        ##############                
        activity_pool.complete(cr, uid, placement_activity_id)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        