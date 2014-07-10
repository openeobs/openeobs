from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from pprint import pprint as pp

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

    def test_build_env(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        config = {
              'bed_qty': 7,
#              'ward_qty': 20,
#              'adt_user_qty': 1,
#              'nurse_user_qty': 10,
#              'ward_manager_user_qty': 3
#              'patient_qty': 2,
#              'admission_method': 'adt_admit' 
        }       
        env_id = env_pool.create(cr, uid, config)
        env_pool.build(cr, uid, env_id)
        
    def test_adt_register(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 0,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        register_data = env_pool.fake_data(cr, uid, env_id, 't4.clinical.adt.patient.register')
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        # test fake data
        assert register_data['family_name']
        assert register_data['given_name']
        assert register_data['other_identifier']
        assert register_data['dob']
        assert register_data['gender']
        assert register_data['sex']
        # Create
        register_activity = env_pool.create_activity(cr, adt_user_id, env_id,'t4.clinical.adt.patient.register', {}, register_data, no_fake=True)
        # activity test
        assert register_activity.data_ref.patient_id == register_activity.patient_id
        assert register_activity.state == 'new'
        assert not register_activity.creator_id
        assert not register_activity.parent_id
        assert register_activity.patient_id
        assert register_activity.pos_id
        
        # data test
        assert register_activity.data_ref.family_name == register_data['family_name']
        assert register_activity.data_ref.given_name == register_data['given_name']
        assert register_activity.data_ref.other_identifier == register_data['other_identifier']
        assert register_activity.data_ref.dob == register_data['dob']
        assert register_activity.data_ref.gender == register_data['gender']
        assert register_activity.data_ref.sex == register_data['sex']
        assert register_activity.data_ref.pos_id.id == env.pos_id.id
        # patient test
        assert register_activity.data_ref.patient_id.family_name == register_data['family_name']  
        assert register_activity.data_ref.patient_id.given_name == register_data['given_name']
        assert register_activity.data_ref.patient_id.other_identifier == register_data['other_identifier']
        assert register_activity.data_ref.patient_id.dob == register_data['dob']
        assert register_activity.data_ref.patient_id.gender == register_data['gender']
        assert register_activity.data_ref.patient_id.sex == register_data['sex']
        # Complete
        register_activity = env_pool.complete(cr, uid, env_id, register_activity.id)
        assert register_activity.state == 'completed'
        assert register_activity.date_terminated
        
        # Existing patient test
        try:
            register_activity = env_pool.create_activity(cr, adt_user_id, env_id,'t4.clinical.adt.patient.register', {}, register_data, no_fake=True)
        except Exception as e:
            assert e.args[1].startswith("Patient already exists!"), "Unexpected reaction to attempt to register existing patient!"
        else:
            assert False, "Unexpected reaction to registration attempt of existing patient!"

    def test_adt_admit(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 2,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        register_activity = env_pool.create_complete(cr, adt_user_id, env_id,'t4.clinical.adt.patient.register')
        admit_data = env_pool.fake_data(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        admit_data['other_identifier'] = register_activity.data_ref.other_identifier
        # test data
        assert admit_data['other_identifier']
        assert admit_data['location']
        assert admit_data['code']
        assert admit_data['start_date']
        assert admit_data['doctors']
        # Create
        admit_activity = env_pool.create_activity(cr, adt_user_id, env_id,'t4.clinical.adt.patient.admit', {}, admit_data, no_fake=True)
        # activity test
        assert admit_activity.data_ref.patient_id == register_activity.patient_id
        assert admit_activity.state == 'new'
        assert not admit_activity.parent_id         
        assert admit_activity.patient_id.id == register_activity.patient_id.id
        # data test
        assert admit_activity.data_ref.other_identifier == register_activity.data_ref.other_identifier
        assert admit_activity.data_ref.patient_id.id == register_activity.patient_id.id
        assert admit_activity.data_ref.location == admit_data['location']
        assert int(admit_activity.data_ref.code) == int(admit_data['code']), "code = %s, [code] = %s" % (admit_activity.data_ref.code, admit_data['code'])
        # test patient
        # test doctors
        # test policy
        # test suggested location
        
        # Complete
        admit_activity = env_pool.complete(cr, uid, env_id, admit_activity.id)
        # test admission
        admission_activity = [a for a in admit_activity.created_ids if a.data_model == 't4.clinical.patient.admission']
        assert len(admission_activity) == 1, "Created admission activity: %s" % admission_activity
        admission_activity = admission_activity[0]
        assert admission_activity.state == 'completed'
        # test spell
        spell_activity = [a for a in admission_activity.created_ids if a.data_model == 't4.clinical.spell']
        assert len(spell_activity) == 1, "Created spell activity: %s" % spell_activity    
        spell_activity = spell_activity[0]
        assert spell_activity.state == 'started'
        # test placement
        placement_activity = [a for a in admission_activity.created_ids if a.data_model == 't4.clinical.patient.placement']
        assert len(placement_activity) == 1, "Created patient.placement activity: %s" % placement_activity    
        placement_activity = placement_activity[0]
        assert placement_activity.state == 'new'        
        
    def test_adt_discharge(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 1,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        spell_activities = api_pool.get_activities(cr, uid, data_models=['t4.clinical.spell'], pos_ids=[env.pos_id.id], states=['started'])
        patient = spell_activities[0].patient_id
        discharge_activity = env_pool.create_activity(cr, uid, env_id, 't4.clinical.adt.patient.discharge', {}, {'other_identifier': patient.other_identifier}, True)
        env_pool.complete(cr, uid, env_id, discharge_activity.id)
    
    def test_placement(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 0,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        register_activity = env_pool.create_complete(cr, adt_user_id, env_id,'t4.clinical.adt.patient.register')
        admit_data = env_pool.fake_data(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        admit_data['other_identifier'] = register_activity.data_ref.other_identifier
        admit_activity = env_pool.create_complete(cr, adt_user_id, env_id,'t4.clinical.adt.patient.admit', {}, admit_data)
        # test admission
        admission_activity = [a for a in admit_activity.created_ids if a.data_model == 't4.clinical.patient.admission']
        assert len(admission_activity) == 1, "Created admission activity: %s" % admission_activity
        admission_activity = admission_activity[0]
        assert admission_activity.state == 'completed'
        #test placement        
        placement_activity = [a for a in admission_activity.created_ids if a.data_model == 't4.clinical.patient.placement']
        assert len(placement_activity) == 1, "Created patient.placement activity: %s" % placement_activity    
        placement_activity = placement_activity[0]
        assert placement_activity.state == 'new'   
        assert placement_activity.pos_id.id == register_activity.pos_id.id
        assert placement_activity.patient_id.id == register_activity.patient_id.id
        assert placement_activity.data_ref.patient_id.id == placement_activity.patient_id.id
        assert placement_activity.data_ref.suggested_location_id
        assert placement_activity.location_id.id == placement_activity.data_ref.suggested_location_id.id

    def test_api_user_map(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'bed_qty': 3,
            'user_qty': 3
        }
        nurse_count = len(api.user_map(cr, uid, group_xmlids=['group_t4clinical_nurse']))
        adt_count = len(api.user_map(cr, uid, group_xmlids=['group_t4clinical_adt']))
        ward_manager_count = len(api.user_map(cr, uid, group_xmlids=['group_t4clinical_ward_manager']))
            
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        
        # test group_xmlids
        umap = api.user_map(cr, uid, group_xmlids=['group_t4clinical_ward_manager'])    
        assert len(umap) - ward_manager_count == env.ward_manager_user_qty, \
            "Unexpected ward manager users count. before: %s, after: %s, env: %s" % (ward_manager_count, len(umap), env.ward_manager_user_qty)
        umap = api.user_map(cr, uid, group_xmlids=['group_t4clinical_adt'])
        assert len(umap) - adt_count == env.adt_user_qty, \
            "Unexpected adt users count. before: %s, after: %s, env: %s" % (adt_count, len(umap), env.adt_user_qty)
        umap = api.user_map(cr, uid, group_xmlids=['group_t4clinical_nurse'])
        assert len(umap) - nurse_count == env.nurse_user_qty, \
            "Unexpected nurse users count. before: %s, after: %s, env: %s" % (nurse_count, len(umap), env.nurse_user_qty)        
        
        # test assigned_activity_ids
        ews_activities = api.get_activities(cr, uid, pos_ids=[env.pos_id.id], data_models=['t4.clinical.patient.observation.ews'])
        user_id = umap.keys()[0]
        activity_ids = [a.id for a in ews_activities]
        [api.assign(cr, uid, activity_id, user_id) for activity_id in activity_ids]
        umap = api.user_map(cr, uid, assigned_activity_ids=activity_ids)
        pp(umap)
        assert set(activity_ids) == set(umap[user_id]['assigned_activity_ids']), \
            "Wrong assigned_activity_ids returned. activity_ids = %s, assigned_activity_ids = %s" \
            % (activity_ids, umap[user_id]['assigned_activity_ids'])
                
    def test_api_patient_map(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'bed_qty': 3,
            'patient_qty': 2
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        pmap = api.patient_map(cr, uid, pos_ids=[env.pos_id.id])
        pp(pmap)
        
    def test_api_location_map(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'bed_qty': 6,
            'patient_qty': 2
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        # get patients
        spell_activities = api_pool.get_activities(cr, uid, data_models=['t4.clinical.spell'], states=['started'], pos_ids=[env.pos_id.id])
        assert len(spell_activities) == env.patient_qty
        patients = [a.patient_id for a in spell_activities]
        bed_locations = api_pool.get_locations(cr, uid, pos_ids=[env.pos_id.id], usages=['bed'])
        assert len(bed_locations) == env.bed_qty
        amap = api_pool.location_map(cr, uid, usages=['bed'], available_range=[0,1], pos_ids=[env.pos_id.id])
        available_ids = [k for k, v in amap.items() if amap[k]['available']>0]
        unavailable_ids = list(set(amap.keys()) - set(available_ids))
        assert len(unavailable_ids) == env.patient_qty, "unavailable_ids = %s" % unavailable_ids
        assert available_ids, "This test needs more beds than patients!"
        # test moves 0->1->2->3 ....
        for i in range(len(available_ids)):
            patient_id = patients[0].id
            location_id = available_ids[i]
            move = api_pool.create_complete(cr, uid, 't4.clinical.patient.move', {},
                                            {'patient_id': patient_id, 'location_id': location_id})
            # availability
            amap = api_pool.location_map(cr, uid, usages=['bed'], available_range=[0,1], pos_ids=[env.pos_id.id])
            assert not amap[available_ids[i]]['available']
            if i > 0: assert amap[available_ids[i-1]]['available']
            # patient
            amap = api_pool.location_map(cr, uid, usages=['bed'], patient_ids=[patient_id], available_range=[0,1], pos_ids=[env.pos_id.id])
            #import pdb; pdb.set_trace()
            assert len(amap) == 1, "Patient must be in one location only!"
            assert len(amap[location_id]['patient_ids']) == 1, "More patients returned than expected!"
            assert amap[location_id]['patient_ids'][0] == patient_id, "Wrong patient returned!"
            amap = api_pool.location_map(cr, uid, usages=['bed'], patient_ids=[patient_id], available_range=[0,1], pos_ids=[env.pos_id.id])
            
            
    def test_no_policy_obs_and_adt_cancel(self):
        #return
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        activity_pool = self.registry('t4.activity')
        config = {
              'bed_qty': 7,
#              'ward_qty': 20,
#              'adt_user_qty': 1,
#              'nurse_user_qty': 10,
#              'ward_manager_user_qty': 3
#              'patient_qty': 2,
#              'admission_method': 'adt_admit'         
        }
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        pos = env.pos_id
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        nurse_user_id = api_pool.user_map(cr,uid, group_xmlids=['group_t4clinical_nurse']).keys()[0]
        
        #Complete observation.ews
        ews_activities = api_pool.get_activities(cr, uid, pos_ids=[pos.id], data_models=['t4.clinical.patient.observation.ews'])
        assert len(ews_activities) == env.patient_qty, "len(ews_activities) = %s, env.patient_qty = %s, pos.id = %s" % (len(ews_activities), env.patient_qty, pos.id)
        for activity in ews_activities:
            api_pool.assign(cr, uid, activity.id, nurse_user_id)
            env_pool.submit_complete(cr, nurse_user_id, env_id, activity.id)

                
        # Complete observation.gcs  
#         gcs_activities = api_pool.get_activities(cr, uid, pos_ids=[pos.id], data_models=['t4.clinical.patient.observation.gcs'])
#         print gcs_activities
        #import pdb; pdb.set_trace()
        #patients = [a.patient for a in api_pool.get_activities(cr, uid, pos_ids=[pos.id], data_models=['t4.clinical.patient.observation.gcs'])]
        #gcs = [env_pool.create_activity(cr, uid, env_id, 't4.clinical.patient.observation.gcs',{}, {'patient_id':p.id}) for p in patients]
        gcs = [env_pool.create_activity(cr, uid, env_id, 't4.clinical.patient.observation.gcs') for i in range(env.patient_qty)]
        for gcs_activity in gcs: 
            api_pool.assign(cr, uid, gcs_activity.id, nurse_user_id)
            env_pool.submit_complete(cr, nurse_user_id, env_id, gcs_activity.id)
        # Complete observation.height
        height = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.height') for i in range(env.patient_qty)]
        # Complete observation.weight
        weight = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.weight') for i in range(env.patient_qty)]
        # Complete observation.blood_sugar
        blood_sugar = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.blood_sugar') for i in range(env.patient_qty)]
        # Complete observation.blood_product
        blood_product = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.blood_product') for i in range(env.patient_qty)]
        # Complete observation.stools
        stools = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.stools') for i in range(env.patient_qty)]
        # calcel adt.cancel_admit
        cancel = [env_pool.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.cancel_admit') for i in range(1)]
        
        for a in gcs + height + weight + blood_sugar + blood_product + stools:
            if a.patient_id.id == cancel[0].patient_id.id:
                assert a.state == 'cancelled'

    def test_gcs_observations_policy_static(self):
        #return
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
        api_pool = self.registry('t4.clinical.api')
        activity_pool = self.registry('t4.activity')
        env_id = env_pool.create(cr, uid)
        env = env_pool.build(cr, uid, env_id)

        # gcs
        gcs_activity = env_pool.create_complete(cr, uid, env_id,'t4.clinical.patient.observation.gcs')
        for i in range(13):
            data = {
                'eyes': gcs_test_data['EYES'][i],
                'verbal': gcs_test_data['VERBAL'][i],
                'motor': gcs_test_data['MOTOR'][i],
            }
            gcs_activity = env_pool.submit_complete(cr, uid, env_id, gcs_activity.created_ids[0].id, data)
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
                ('creator_id', '=', gcs_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', gcs_pool._name)]
            gcs_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(gcs_activity_ids, msg='Next GCS activity was not triggered')
            next_gcs_activity = activity_pool.browse(cr, uid, gcs_activity_ids[0])
            self.assertEqual(next_gcs_activity.data_ref.frequency, frequency, msg='Frequency not matching')
        

    def test_ews_observations_policy_static(self):
        #return
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
        api_pool = self.registry('t4.clinical.api')
        activity_pool = self.registry('t4.activity')
        env_id = env_pool.create(cr, uid)
        env = env_pool.build(cr, uid, env_id)
        # ews
        ews_activity = api_pool.get_activities(cr, uid, 
                                               pos_ids=[env.pos_id.id], 
                                               data_models=['t4.clinical.patient.observation.ews'],
                                               states=['new','scheduled','started'])[0]
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
            nurse_user_id = api_pool.user_map(cr,uid, group_xmlids=['group_t4clinical_nurse']).keys()[0]

            # completion must be made as nurse user, otherwise notifications are not created
            api_pool.assign(cr, uid, ews_activity.id, nurse_user_id)
            ews_activity = api_pool.submit_complete(cr, nurse_user_id, ews_activity.id, data)
            
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
                ('creator_id', '=', ews_activity.id),
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
                ('creator_id', '=', ews_activity.id),
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
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            ews_activity = api_pool.get_activities(cr, uid, pos_ids=[env.pos_id.id], 
                                                   data_models=['t4.clinical.patient.observation.ews'],
                                                   states=['new','scheduled','started'])[0]