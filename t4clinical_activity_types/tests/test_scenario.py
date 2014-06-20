from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


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


class ActivityTypesTest(BaseTest):    
    def setUp(self):
        global cr, uid, \
               register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool, user_pool, imd_pool, discharge_pool, \
               device_connect_pool, device_disconnect_pool, partner_pool, height_pool, blood_sugar_pool, \
               blood_product_pool, weight_pool, stools_pool, gcs_pool, vips_pool, o2target_pool, o2target_activity_pool
        
        cr, uid = self.cr, self.uid

        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        activity_pool = self.registry('t4.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        height_pool = self.registry('t4.clinical.patient.observation.height')
        weight_pool = self.registry('t4.clinical.patient.observation.weight')
        blood_sugar_pool = self.registry('t4.clinical.patient.observation.blood_sugar')
        blood_product_pool = self.registry('t4.clinical.patient.observation.blood_product')
        stools_pool = self.registry('t4.clinical.patient.observation.stools')
        gcs_pool = self.registry('t4.clinical.patient.observation.gcs')
        vips_pool = self.registry('t4.clinical.patient.observation.vips')
        api_pool = self.registry('t4.clinical.api')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        user_pool = self.registry('res.users')
        partner_pool = self.registry('res.partner')
        imd_pool = self.registry('ir.model.data')
        device_connect_pool = self.registry('t4.clinical.device.connect')
        device_disconnect_pool = self.registry('t4.clinical.device.disconnect')
        o2target_pool = self.registry('t4.clinical.o2level')
        o2target_activity_pool = self.registry('t4.clinical.patient.o2target')

        super(ActivityTypesTest, self).setUp()
        
    def create_pos_environment(self):
        env = super(ActivityTypesTest, self).create_pos_environment()
        env.update({'patient_ids': [], 'other_identifiers': []})
        return env        
    
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
        
        # env
        ##############
        env['patient_ids'].append(register_activity.patient_id.id)
        env['other_identifiers'].append(other_identifier)        
        #import pdb; pdb.set_trace()
        return register_activity_id
    
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
        self.assertTrue(data_vals.get('other_identifier') or env.get('other_identifiers'),
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
        
        if not data.get('doctors'):
            d = [{
                    'code': str(fake.random_int(min=10001, max=99999)),
                    'type': fake.random_element(array=('r','c')),
                    'title': fake.random_element(array=('Mr','Mrs','Ms','Dr')),
                    'family_name': fake.last_name(),
                    'given_name': fake.first_name()
                    },
                   ]
            data['doctors'] = d
            
        
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
        for doctor in data['doctors']:
            partner_ids = partner_pool.search(cr, uid, [['code','=',doctor['code']]])
            self.assertTrue(len(partner_ids) == 1, "0 or more than 1 doctor with code. partner_ids = %s" % partner_ids)
            if doctor['type'] == 'c':
                self.assertTrue(admit_activity.data_ref.con_doctor_ids, "admit consultant ids")                 
            else:
                self.assertTrue(admit_activity.data_ref.ref_doctor_ids, "admit referrer ids")              
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
        #api_pool.activity_info(cr, uid, spell_activity_id)
        self.assertTrue(spell_activity_id,
                       "spell_activity not found after adt.admit completion!")  
        self.assertTrue(admission_activity.parent_id.id == spell_activity_id,
                       "admission_activity.parent_id != spell_activity_id after adt.admit completion!")
        spell_activity = activity_pool.browse(cr, uid, spell_activity_id)
        for doctor in data['doctors']:
            if doctor['type']== 'c':
                self.assertTrue(spell_activity.data_ref.con_doctor_ids,
                                "consultant ids")                 
            else:
                self.assertTrue(spell_activity.data_ref.ref_doctor_ids,
                                "referrer ids") 
        self.assertTrue(spell_activity.state == 'started',
                       "spell_activity.state != 'started' after adt.admit completion!")             
        self.assertTrue(spell_activity.patient_id.id == admit_activity.patient_id.id,
                       "spell_activity.patient_id != admit_activity.patient_id after adt.admit completion!")        
        self.assertTrue(spell_activity.pos_id.id == admit_activity.pos_id.id,
                       "spell_activity.pos_id != admit_activity.pos_id after adt.admit completion!") 
        self.assertTrue(spell_activity.location_id.id == admission_activity.pos_id.lot_admission_id.id,
                       "spell_activity.location_id != admission_activity.pos_id.lot_admission_id after adt.admit completion!")
        
        self.assertTrue(api_pool.get_patient_spell_activity_id(cr, uid, 
                                                               admit_activity.patient_id.id, 
                                                               pos_id=admit_activity.pos_id.id) == spell_activity_id,
                       "api.get_pateint_spell_activity_id != spell_activity_id after adt.admit completion!")        
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
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'])
        data['location_id'] = data_vals.get('location_id') \
                              or available_bed_location_ids[fake.random_int(min=0, max=len(available_bed_location_ids)-1)]
        placement_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.placement'],
                                                               ['patient_id','=',patient_id],
                                                               ['state','in',['new','started','scheduled']]])
        placement_activity_id = placement_activity_id and placement_activity_id[0]
        self.assertTrue(placement_activity_id,
                       "placement_activity not found in patient_placement() for patient_id=%s" % (patient_id))         
        placement_activity = activity_pool.browse(cr, uid, placement_activity_id)
        spell_activity = placement_activity.parent_id
        self.assertTrue(spell_activity.data_model == 't4.clinical.spell',
                       "parent_id is not spell")          
        self.assertTrue(spell_activity.patient_id.id == patient_id,
                       "spell.patient_id != pateint_id")   
        # submit
        ##############
        activity_pool.submit(cr, uid, placement_activity_id, data)
        self.assertTrue(placement_activity.patient_id.id == spell_activity.patient_id.id,
                       "placement_activity.patient_id != spell_activity.patient_id after submission")        
        self.assertTrue(placement_activity.pos_id.id == spell_activity.pos_id.id,
                       "placement_activity.pos_id != spell_activity.pos_id after submission") 
        self.assertTrue(placement_activity.location_id.id == placement_activity.data_ref.suggested_location_id.id,
                       "placement_activity.location_id != placement_activity.data_ref.suggested_location_id after submission") 
        # complete
        ##############                
        activity_pool.complete(cr, uid, placement_activity_id)
        
        move_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.move'],
                                                          ['creator_id','=',placement_activity_id]])
        move_activity_id = move_activity_id and move_activity_id[0]
        self.assertTrue(move_activity_id,
                       "move_activity not found after placement.complete()")          
        move_activity = activity_pool.browse(cr, uid, move_activity_id)

        self.assertTrue(move_activity.parent_id.id == spell_activity.id,
                       "move_activity.parent_id != spell_activity.id after placement.complete()")         
        self.assertTrue(move_activity.state == 'completed',
                       "move_activity.state != 'completed' after placement.complete()")  
        self.assertTrue(move_activity.patient_id.id == spell_activity.patient_id.id,
                       "move_activity.patient_id != spell_activity.patient_id after placement.complete()")        
        self.assertTrue(move_activity.pos_id.id == spell_activity.pos_id.id,
                       "move_activity.pos_id != spell_activity.pos_id after placement.complete()") 
        self.assertTrue(move_activity.location_id.id == data['location_id'],
                       "move_activity.location_id != data['location_id'] after placement.complete()")         
        
        
        
        # complete api calls test
        self.assertTrue(api_pool.get_patient_current_location_id(cr, uid, move_activity.patient_id.id) == data['location_id'],
                       "current_location_id != data['location_id'] after placement.complete()"
                       + "\n current_location_id: %s" % api_pool.get_patient_current_location_id(cr, uid, move_activity.patient_id.id)
                       + "\n move_location_id: %s" % data['location_id']) 
        
        
         # ews test
        ews_activity_id = activity_pool.search(cr, uid, [['data_model','=','t4.clinical.patient.observation.ews'],
                                                         ['creator_id','=',placement_activity_id]])   
        ews_activity_id = ews_activity_id and ews_activity_id[0]
        #api_pool.activity_info(cr, uid, ews_activity_id)
        self.assertTrue(ews_activity_id,
                       "ews_activity not found after placement completion!")  
        ews_activity = activity_pool.browse(cr, uid, ews_activity_id)
        self.assertTrue(ews_activity.parent_id.id == spell_activity.id,
                       "ews_activity.parent_id != spell_activity after placement completion!")
        self.assertTrue(ews_activity.state == 'scheduled',
                       "ews_activity.state != 'scheduled' after placement completion!")  
        date_scheduled_diff=(dt.now()+rd(minutes=spell_activity.data_ref.ews_frequency) 
                             - dt.strptime(ews_activity.date_scheduled, DTF)).total_seconds()
        self.assertTrue(date_scheduled_diff < 5,
                       "ews_activity.date_scheduled_diff > 5 sec after placement completion!")   
#         ews_trigger = api_pool.get_activity_trigger_browse(cr, uid, ews_activity.patient_id.id, ews_activity.data_model)
#         self.assertTrue(ews_trigger.unit == 'minute' and ews_trigger.unit_qty == placement_activity.pos_id.ews_init_frequency,
#                        "ews_trigger is not set correctly after placement completion!") 
                        
        self.assertTrue(ews_activity.patient_id.id == placement_activity.patient_id.id,
                       "ews_activity.patient_id != placement_activity.patient_id after placement completion!")        
        self.assertTrue(ews_activity.pos_id.id == placement_activity.pos_id.id,
                       "ews_activity.pos_id != placement_activity.pos_id after placement completion!") 
        self.assertTrue(ews_activity.location_id.id == placement_activity.data_ref.location_id.id, # placement_activity.location_id == suggested_location
                       "ews_activity.location_id != placement_activity.data_ref.location_id.id after placement completion!")

    def device_connect(self, activity_vals={}, data_vals={}, env={}):
        data = {}
        device_id = data_vals.get('device_id') \
                     or env['device_ids'][fake.random_int(min=0, max=len(env['device_ids'])-1)]
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)] 
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        connect_activity_id = device_connect_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
                                                                  {
                                                                   'patient_id': patient_id,
                                                                   'device_id': device_id
                                                                   })
        # Complete
        activity_pool.complete(cr, uid, connect_activity_id)   

        connect_activity = activity_pool.browse(cr, uid, connect_activity_id)
        self.assertTrue(connect_activity.state == 'completed',
                       "connect_activity.state != 'completed' after completion!")
        session_activity_id = activity_pool.search(cr, uid, [('creator_id','=',connect_activity.id),
                                                             ('data_model','=','t4.clinical.device.session')])
        session_activity_id = session_activity_id and session_activity_id[0]
        self.assertTrue(session_activity_id,
                       "session activity not found after device.connect completion!")        
        session_activity = activity_pool.browse(cr, uid, session_activity_id)
        self.assertTrue(session_activity.patient_id.id == session_activity.patient_id.id,
                       "session.patient_id != connect.patient_id!")         
        self.assertTrue(session_activity.device_id.id == session_activity.device_id.id,
                       "session.device_id != connect.device_id!")  

        return connect_activity_id          
               
    def device_disconnect(self, activity_vals={}, data_vals={}, env={}):
        data = {}
        device_id = data_vals.get('device_id') \
                     or env['device_ids'][fake.random_int(min=0, max=len(env['device_ids'])-1)]
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)] 
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        disconnect_activity_id = device_disconnect_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
                                                                  {
                                                                   'patient_id': patient_id,
                                                                   'device_id': device_id
                                                                   })
        # Complete
        session_activity_id = api_pool.get_device_session_activity_id(cr, uid, device_id)
        activity_pool.complete(cr, uid, disconnect_activity_id)   
        session_activity = activity_pool.browse(cr, uid, session_activity_id)
        self.assertTrue(session_activity.state == 'completed',
                       "session_activity.state != 'completed' after device.disconnect completion!")  
        return disconnect_activity_id

    def observation_height(self, activity_vals={}, data_vals={}, env={}):        
        height = data_vals.get('height') or float(fake.random_int(min=160, max=200))/100.0
        print "TEST - observation Height - %s" % height
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        height_activity_id = height_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
                                                         {'patient_id': patient_id, 'height': height})
        # Complete
        activity_pool.complete(cr, uid, height_activity_id)
        height_activity = activity_pool.browse(cr, uid, height_activity_id)
        self.assertTrue(height_activity.data_ref.height == height)
        return height_activity_id

    def observation_weight(self, activity_vals={}, data_vals={}, env={}):
        weight = data_vals.get('weight') or float(fake.random_int(min=40, max=200))
        print "TEST - observation Weight - %s" % weight
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        weight_activity_id = weight_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
                                                         {'patient_id': patient_id, 'weight': weight})
        # Complete
        activity_pool.complete(cr, uid, weight_activity_id)
        weight_activity = activity_pool.browse(cr, uid, weight_activity_id)
        self.assertTrue(weight_activity.data_ref.weight == weight)
        return weight_activity_id

    def observation_blood_sugar(self, activity_vals={}, data_vals={}, env={}):
        blood_sugar = data_vals.get('blood_sugar') or float(fake.random_int(min=1, max=100))
        print "TEST - observation Blood Sugar - %s" % blood_sugar
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        bs_activity_id = blood_sugar_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, 
                                                          {'patient_id': patient_id, 'blood_sugar': blood_sugar})
        # Complete
        activity_pool.complete(cr, uid, bs_activity_id)
        bs_activity = activity_pool.browse(cr, uid, bs_activity_id)
        self.assertTrue(bs_activity.data_ref.blood_sugar == blood_sugar)
        return bs_activity_id
    
    def observation_blood_product(self, activity_vals={}, data_vals={}, env={}):
        vol = data_vals.get('vol') or float(fake.random_int(min=1, max=10))
        product = data_vals.get('product') or fake.random_element(array=('rbc', 'ffp', 'platelets', 'has', 'dli', 'stem'))
        print "TEST - observation Blood Product - %s %s" % (vol, product)
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        bp_activity_id = blood_product_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
                                                            {
                                                                'patient_id': patient_id,
                                                                'product': product,
                                                                'vol': vol
                                                            })
        # Complete
        activity_pool.complete(cr, uid, bp_activity_id)
        bp_activity = activity_pool.browse(cr, uid, bp_activity_id)
        self.assertTrue(bp_activity.data_ref.product == product)
        self.assertTrue(bp_activity.data_ref.vol == vol)
        return bp_activity_id
    
    def observation_stools(self, activity_vals={}, data_vals={}, env={}):
        data = {
            'bowel_open': data_vals.get('bowel_open') or fake.random_int(min=0, max=1),
            'nausea': data_vals.get('nausea') or fake.random_int(min=0, max=1),
            'vomiting': data_vals.get('vomiting') or fake.random_int(min=0, max=1),
            'quantity': data_vals.get('quantity') or fake.random_element(array=('large', 'medium', 'small')),
            'colour': data_vals.get('colour') or fake.random_element(array=('brown', 'yellow', 'green', 'black', 'red', 'clay')),
            'bristol_type': data_vals.get('bristol_type') or str(fake.random_int(min=1, max=7)),
            'offensive': data_vals.get('offensive') or fake.random_int(min=0, max=1),
            'strain': data_vals.get('strain') or fake.random_int(min=0, max=1),
            'laxatives': data_vals.get('laxatives') or fake.random_int(min=0, max=1),
            'samples': data_vals.get('samples') or fake.random_element(array=('none', 'micro', 'virol', 'm+v')),
            'rectal_exam': data_vals.get('rectal_exam') or fake.random_int(min=0, max=1),
        }
        print "TEST - observation Stools - %s" % data
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        data['patient_id'] = patient_id
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        stools_activity_id = stools_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, data)
        # Complete
        activity_pool.complete(cr, uid, stools_activity_id)
        stools_activity = activity_pool.browse(cr, uid, stools_activity_id)
        [self.assertTrue(eval('stools_activity.data_ref.'+k) == data[k]) for k in data.keys() if k != 'patient_id']
        return stools_activity_id

    def observation_ews(self, activity_vals={}, data_vals={}, env={}):
        data = {
            'respiration_rate': data_vals.get('respiration_rate') or fake.random_int(min=5, max=34),
            'indirect_oxymetry_spo2': data_vals.get('indirect_oxymetry_spo2') or fake.random_int(min=85, max=100),
            'body_temperature': data_vals.get('body_temperature') or float(fake.random_int(min=350, max=391))/10.0,
            'blood_pressure_systolic': data_vals.get('blood_pressure_systolic') or fake.random_int(min=65, max=206),
            'pulse_rate': data_vals.get('pulse_rate') or fake.random_int(min=35, max=136),
            'avpu_text': data_vals.get('avpu_text') or fake.random_element(array=('A', 'V', 'P', 'U')),
        }
        if isinstance(data_vals.get('oxygen_administration_flag'), bool):
            data['oxygen_administration_flag'] = fake.random_element(array=(True, False))
        else:
            data['oxygen_administration_flag'] = data_vals.get('oxygen_administration_flag')
        data['blood_pressure_diastolic'] = data_vals.get('blood_pressure_diastolic') or data['blood_pressure_systolic']-30
        if data['oxygen_administration_flag']:
            data.update({
                'flow_rate': data_vals.get('flow_rate') or fake.random_int(min=40, max=60),
                'concentration': data_vals.get('concentration') or fake.random_int(min=50, max=100),
                'cpap_peep': data_vals.get('cpap_peep') or fake.random_int(min=1, max=100),
                'niv_backup': data_vals.get('niv_backup') or fake.random_int(min=1, max=100),
                'niv_ipap': data_vals.get('niv_ipap') or fake.random_int(min=1, max=100),
                'niv_epap': data_vals.get('niv_epap') or fake.random_int(min=1, max=100),
            })
        print "TEST - observation EWS - %s" % data
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        data['patient_id'] = patient_id
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        ews_activity_id = ews_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, data)
        # Complete
        activity_pool.complete(cr, uid, ews_activity_id)
        ews_activity = activity_pool.browse(cr, uid, ews_activity_id)
        [self.assertTrue(eval('ews_activity.data_ref.'+k) == data[k]) for k in data.keys() if k != 'patient_id']
        return ews_activity_id
    
    def observation_gcs(self, activity_vals={}, data_vals={}, env={}):
        data = {
            'eyes': data_vals.get('eyes') or fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': data_vals.get('verbal') or fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': data_vals.get('motor') or fake.random_element(array=('1', '2', '3', '4', '5', '6')),
        }
        print "TEST - observation GCS - %s" % data
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        data['patient_id'] = patient_id
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        # Create
        gcs_activity_id = gcs_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, data)
        # Complete
        activity_pool.complete(cr, uid, gcs_activity_id)
        gcs_activity = activity_pool.browse(cr, uid, gcs_activity_id)
        [self.assertTrue(eval('gcs_activity.data_ref.'+k) == data[k]) for k in data.keys() if k != 'patient_id']
        return gcs_activity_id

    def o2target(self, activity_vals={}, data_vals={}, env={}):
        patient_id = data_vals.get('patient_id') \
                     or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
        o2target_ids = o2target_pool.search(cr, uid, [])
        o2level_id = data_vals.get('level_id') or fake.random_element(array=o2target_ids) if o2target_ids else False
        if not o2level_id:
            return False
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id)
        o2target_activity_id = o2target_activity_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, {'level_id': o2level_id, 'patient_id': patient_id})
        activity_pool.complete(cr, uid, o2target_activity_id)
        return o2target_activity_id

class ActivityTypesScenarioTest(BaseTest):

    def setUp(self):
        global cr, uid, \
               register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool, user_pool, imd_pool, discharge_pool, \
               device_connect_pool, device_disconnect_pool, partner_pool, height_pool, blood_sugar_pool, \
               blood_product_pool, weight_pool, stools_pool, gcs_pool, vips_pool, o2target_pool, o2target_activity_pool
        
        cr, uid = self.cr, self.uid

        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        activity_pool = self.registry('t4.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        height_pool = self.registry('t4.clinical.patient.observation.height')
        weight_pool = self.registry('t4.clinical.patient.observation.weight')
        blood_sugar_pool = self.registry('t4.clinical.patient.observation.blood_sugar')
        blood_product_pool = self.registry('t4.clinical.patient.observation.blood_product')
        stools_pool = self.registry('t4.clinical.patient.observation.stools')
        gcs_pool = self.registry('t4.clinical.patient.observation.gcs')
        vips_pool = self.registry('t4.clinical.patient.observation.vips')
        api_pool = self.registry('t4.clinical.api')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        user_pool = self.registry('res.users')
        partner_pool = self.registry('res.partner')
        imd_pool = self.registry('ir.model.data')
        device_connect_pool = self.registry('t4.clinical.device.connect')
        device_disconnect_pool = self.registry('t4.clinical.device.disconnect')
        o2target_pool = self.registry('t4.clinical.o2level')
        o2target_activity_pool = self.registry('t4.clinical.patient.o2target')

        super(BaseTest, self).setUp()

    def test_no_policy_obs(self):
        env_pool = self.registry('t4.clinical.demo.env')
        config = {
              'bed_qty': 7,
#              'ward_qty': 20,
#              'adt_user_qty': 1,
#              'nurse_user_qty': 10,
#              'ward_manager_user_qty': 3
        }
        env_id = env_pool.create(cr, uid, config)
        
        env_pool.build(cr, uid, env_id)
        
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        
        # Register
        [env_pool.adt_patient_register(cr, adt_user_id, env_id) for i in range(2)]

        # Admit
        [env_pool.adt_patient_admit(cr, adt_user_id, env_id) for i in range(2)]

        placement_activities = env_pool.get_activities(cr, uid, env_id, domain=[['data_model','=','t4.clinical.patient.placement']])
        for pa in placement_activities:
            print "pa.location_id: %s, pa.data_ref.location_id: %s" %(pa.location_id, pa.data_ref.location_id)

        # Admit
        [env_pool.complete_placement(cr, adt_user_id, env_id) for i in range(2)]
        
#         # Register-Admit-Placement shortcut # breaks on 'more than 1 ews at a time' 
#         env_pool.force_patient_placement(cr, adt_user_id, env_id)

        # Complete observation.ews
        
        [env_pool.complete_observation_ews(cr, uid, env_id) for i in range(3)]
               
        # Complete observation.gcs
        env_pool.create_observation_gcs(cr, uid, env_id)
        env_pool.complete_observation_gcs(cr, uid, env_id)


        # Complete observation.height
        env_pool.create_observation_height(cr, uid, env_id)
        env_pool.complete_observation_height(cr, uid, env_id)


        # Complete observation.weight
        env_pool.create_observation_weight(cr, uid, env_id)
        env_pool.complete_observation_weight(cr, uid, env_id)

        # Complete observation.blood_sugar
        env_pool.create_observation_blood_sugar(cr, uid, env_id)
        env_pool.complete_observation_blood_sugar(cr, uid, env_id)

        # Complete observation.blood_product
        env_pool.create_observation_blood_product(cr, uid, env_id)
        env_pool.complete_observation_blood_product(cr, uid, env_id)

        # Complete observation.stools
        env_pool.create_observation_stools(cr, uid, env_id)
        env_pool.complete_observation_stools(cr, uid, env_id)

        # calcel adt.admit.cancel

        env_pool.create_adt_patient_cancel_admit(cr, adt_user_id, env_id)
        env_pool.complete_adt_patient_cancel_admit(cr, adt_user_id, env_id)

    def test_gcs_observations_policy_static(self):
        return
        gcs_test_data = {
            'SCORE':    [   3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15],
            'CASE':     [   0,    0,    0,    1,    1,    1,    1,    2,    2,    2,    2,    3,    4],
            'EYES':     [ '1',  'C',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '4',  '4',  '4',  '4'],
            'VERBAL':   [ '1',  'T',  '1',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '5',  '5'],
            'MOTOR':    [ '1',  '2',  '2',  '2',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '6'],
        }
        
        gcs_policy = {
            'frequencies': [30, 60, 120, 240, 720],
            'notifications': [
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False}
            ]
        }

        env_pool = self.registry('t4.clinical.demo.env')
        env_id = env_pool.create(cr, uid)
        env_pool.build(cr, uid, env_id)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        # Register
        env_pool.adt_patient_register(cr, adt_user_id, env_id)
        # Admit
        env_pool.adt_patient_admit(cr, adt_user_id, env_id)
        # Complete Placement shortcut
        env_pool.complete_placement(cr, uid, env_id)
        
        # gcs
        env_pool.create_observation_gcs(cr, uid, env_id)
        for i in range(13):
            data = {
                'eyes': gcs_test_data['EYES'][i],
                'verbal': gcs_test_data['VERBAL'][i],
                'motor': gcs_test_data['MOTOR'][i],
            }
            gcs_id = env_pool.complete_observation_gcs(cr, uid, env_id, data)
            gcs_activity = activity_pool.browse(cr, uid, gcs_id)
            
            frequency = gcs_policy['frequencies'][gcs_test_data['CASE'][i]]
            nurse_notifications = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['nurse']
            assessment = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['assessment']
            review_frequency = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['frequency']

            print "TEST - observation GCS: expecting score %s, frequency %s" % (gcs_test_data['SCORE'][i], frequency)

            
            # # # # # # # # # # # # # # # # #
            # Check the score and frequency #
            # # # # # # # # # # # # # # # # #
            self.assertEqual(gcs_activity.data_ref.score, gcs_test_data['SCORE'][i], msg='Score not matching')
            domain = [
                ('creator_id', '=', gcs_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', gcs_pool._name)]
            gcs_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(gcs_activity_ids, msg='Next GCS activity was not triggered')
            next_gcs_activity = activity_pool.browse(cr, uid, gcs_activity_ids[0])
            self.assertEqual(next_gcs_activity.data_ref.frequency, frequency, msg='Frequency not matching')
        

    def test_ews_observations_policy_static(self):
        return
        ews_test_data = {
            'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,    3,    4,   20],
            'CASE':     [   0,    1,    1,    1,    1,    2,    2,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    2,    2,    3],
            'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
            'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   91,   91,   91,   91,   91,   91,   91,   99,   99,   91],
            'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
            'BT':       [37.5, 36.5, 36.5, 36.0, 36.0, 36.0, 38.5, 38.5, 38.5, 38.5, 38.5, 35.5, 39.5, 35.0, 35.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
            'BPS':      [ 120,  115,  115,  115,  110,  110,  110,  110,  100,  100,  100,  100,  100,  100,   90,  220,  220,  220,  120,  120,  220],
            'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
            'PR':       [  65,   55,   55,   55,   55,   50,  110,   50,   50,  130,  130,  130,  130,  130,  130,  135,  135,  135,   65,   65,  135],
            'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
        }
        ews_policy = {
            'frequencies': [720, 240, 60, 30],
            'risk': ['None', 'Low', 'Medium', 'High'],
            'notifications': [
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': True, 'frequency': False},
                {'nurse': ['Urgently inform medical team'], 'assessment': False, 'frequency': False},
                {'nurse': ['Immediately inform medical team'], 'assessment': False, 'frequency': False}
            ]
        }

        env_pool = self.registry('t4.clinical.demo.env')
        env_id = env_pool.create(cr, uid)
        env_pool.build(cr, uid, env_id)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        # Register
        env_pool.adt_patient_register(cr, adt_user_id, env_id)
        # Admit
        env_pool.adt_patient_admit(cr, adt_user_id, env_id)
        # Complete Placement shortcut
        env_pool.complete_placement(cr, uid, env_id)
        # ews
        for i in range(21):
            
            data={
                'respiration_rate': ews_test_data['RR'][i],
                'indirect_oxymetry_spo2': ews_test_data['O2'][i],
                'oxygen_administration_flag': ews_test_data['O2_flag'][i],
                'body_temperature': ews_test_data['BT'][i],
                'blood_pressure_systolic': ews_test_data['BPS'][i],
                'blood_pressure_diastolic': ews_test_data['BPD'][i],
                'pulse_rate': ews_test_data['PR'][i],
                'avpu_text': ews_test_data['AVPU'][i]
            }
            ews_id = env_pool.complete_observation_ews(cr, uid, env_id, data)
            ews_activity = activity_pool.browse(cr, uid, ews_id)
            
            frequency = ews_policy['frequencies'][ews_test_data['CASE'][i]]
            clinical_risk = ews_policy['risk'][ews_test_data['CASE'][i]]
            nurse_notifications = ews_policy['notifications'][ews_test_data['CASE'][i]]['nurse']
            assessment = ews_policy['notifications'][ews_test_data['CASE'][i]]['assessment']
            review_frequency = ews_policy['notifications'][ews_test_data['CASE'][i]]['frequency']

            print "TEST - observation EWS: expecting score %s, frequency %s, risk %s" % (ews_test_data['SCORE'][i], frequency, clinical_risk)


            # # # # # # # # # # # # # # # # # # # # # # # # #
            # Check the score, frequency and clinical risk  #
            # # # # # # # # # # # # # # # # # # # # # # # # #
            #import pdb; pdb.set_trace()
            self.assertEqual(ews_activity.data_ref.score, ews_test_data['SCORE'][i], msg='Score not matching')
            self.assertEqual(ews_activity.data_ref.clinical_risk, clinical_risk, msg='Risk not matching')
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', ews_pool._name)]
            ews_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(ews_activity_ids, msg='Next EWS activity was not triggered')
            next_ews_activity = activity_pool.browse(cr, uid, ews_activity_ids[0])
            self.assertEqual(next_ews_activity.data_ref.frequency, frequency, msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.assessment')]
            assessment_ids = activity_pool.search(cr, uid, domain)
            if assessment:
                self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
                activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 't4.clinical.notification.frequency')]
                frequency_ids = activity_pool.search(cr, uid, domain)
                self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            domain = [
                ('creator_id', '=', ews_id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.nurse')]
            notification_ids = activity_pool.search(cr, uid, domain)
            self.assertEqual(len(notification_ids), len(nurse_notifications), msg='Wrong notifications triggered')
