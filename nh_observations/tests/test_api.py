from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from pprint import pprint as pp

from openerp import tools
from openerp.osv import orm, fields, osv
from openerp.addons.nh_clinical.tests.test_base import BaseTest

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

class test_api(common.SingleTransactionCase):

    def setUp(self):
        super(test_api, self).setUp()
        
        
    def test_api_location_map(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        config = {
            'bed_qty': 6,
            'patient_qty': 2
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        # get patients
        spell_activities = api.get_activities(cr, uid, data_models=['nh.clinical.spell'], states=['started'], pos_ids=[env.pos_id.id])
        assert len(spell_activities) == env.patient_qty
        patients = [a.patient_id for a in spell_activities]
        bed_locations = api.get_locations(cr, uid, pos_ids=[env.pos_id.id], usages=['bed'])
        assert len(bed_locations) == env.bed_qty
        amap = api.location_map(cr, uid, usages=['bed'], available_range=[0,1], pos_ids=[env.pos_id.id])
        available_ids = [k for k, v in amap.items() if amap[k]['available']>0]
        unavailable_ids = list(set(amap.keys()) - set(available_ids))
        assert len(unavailable_ids) == env.patient_qty, "unavailable_ids = %s" % unavailable_ids
        assert available_ids, "This test needs more beds than patients!"
        # test moves 0->1->2->3 ....
        for i in range(len(available_ids)):
            patient_id = patients[0].id
            location_id = available_ids[i]
            move = api.create_complete(cr, uid, 'nh.clinical.patient.move', {},
                                            {'patient_id': patient_id, 'location_id': location_id})
            # availability
            amap = api.location_map(cr, uid, usages=['bed'], available_range=[0,1], pos_ids=[env.pos_id.id])
            assert not amap[available_ids[i]]['available']
            if i > 0: assert amap[available_ids[i-1]]['available']
            # patient
            amap = api.location_map(cr, uid, usages=['bed'], patient_ids=[patient_id], available_range=[0,1], pos_ids=[env.pos_id.id])
            #import pdb; pdb.set_trace()
            assert len(amap) == 1, "Patient must be in one location only!"
            assert len(amap[location_id]['patient_ids']) == 1, "More patients returned than expected!"
            assert amap[location_id]['patient_ids'][0] == patient_id, "Wrong patient returned!"
            amap = api.location_map(cr, uid, usages=['bed'], patient_ids=[patient_id], available_range=[0,1], pos_ids=[env.pos_id.id])
            
    def test_api_patient_map(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        config = {
            'bed_qty': 3,
            'patient_qty': 3
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        patients = api.patient_map(cr, uid, parent_location_ids=[env.pos_id.location_id.id])
        assert len(patients) == config['patient_qty'], "parent_location_ids patient_qty: %s is wrong!" % len(patients)
        patients = api.patient_map(cr, uid, pos_ids=[env.pos_id.id])
        assert len(patients) == config['patient_qty'], "pos_ids patient_qty: %s is wrong!" % len(patients)
        patient_ids = patients.keys()
        patients = api.patient_map(cr, uid, patient_ids=patient_ids)
        assert len(patients) == config['patient_qty'], "patient_ids patient_qty: %s is wrong!" % len(patients)  
        patient_ids = patients.keys()
        patients = api.patient_map(cr, uid, patient_ids=patient_ids, 
                                            parent_location_ids=[env.pos_id.location_id.id], 
                                            pos_ids=[env.pos_id.id])
        assert len(patients) == config['patient_qty'], "patient/parent_location/pos ids patient_qty: %s is wrong!" % len(patients)      
        #pp(patients)
        
        
    def test_api_user_map(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        config = {
            'bed_qty': 3,
            'user_qty': 3
        }
        nurse_count = len(api.user_map(cr, uid, group_xmlids=['group_nhc_nurse']))
        adt_count = len(api.user_map(cr, uid, group_xmlids=['group_nhc_adt']))
        ward_manager_count = len(api.user_map(cr, uid, group_xmlids=['group_nhc_ward_manager']))
            
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        
        # test group_xmlids
        umap = api.user_map(cr, uid, group_xmlids=['group_nhc_ward_manager'])    
        assert len(umap) - ward_manager_count == env.ward_manager_user_qty, \
            "Unexpected ward manager users count. before: %s, after: %s, env: %s" % (ward_manager_count, len(umap), env.ward_manager_user_qty)
        umap = api.user_map(cr, uid, group_xmlids=['group_nhc_adt'])
        assert len(umap) - adt_count == env.adt_user_qty, \
            "Unexpected adt users count. before: %s, after: %s, env: %s" % (adt_count, len(umap), env.adt_user_qty)
        umap = api.user_map(cr, uid, group_xmlids=['group_nhc_nurse'])
        assert len(umap) - nurse_count == env.nurse_user_qty, \
            "Unexpected nurse users count. before: %s, after: %s, env: %s" % (nurse_count, len(umap), env.nurse_user_qty)        
        
        # test assigned_activity_ids
        ews_activities = api.get_activities(cr, uid, pos_ids=[env.pos_id.id], data_models=['nh.clinical.patient.observation.ews'])
        user_id = umap.keys()[0]
        activity_ids = [a.id for a in ews_activities]
        [api.assign(cr, uid, activity_id, user_id) for activity_id in activity_ids]
        umap = api.user_map(cr, uid, assigned_activity_ids=activity_ids)
        pp(umap)
        assert set(activity_ids) == set(umap[user_id]['assigned_activity_ids']), \
            "Wrong assigned_activity_ids returned. activity_ids = %s, assigned_activity_ids = %s" \
            % (activity_ids, umap[user_id]['assigned_activity_ids'])
                

    def test_api_activity_map(self):
        #return
        cr, uid = self.cr, self.uid
        env_model = self.registry('nh.clinical.demo.env')
        activity_model = self.registry('nh.activity')
        location_model = self.registry('nh.clinical.location')
        patient_model = self.registry('nh.clinical.patient')
        api = self.registry('nh.clinical.api')
        config = {
            'bed_qty': 3,
            'patient_qty': 2
        }       
        env_id = env_model.create(cr, uid, config)
        env = env_model.browse(cr, uid, env_id)
        
        args = {
                'pos_ids': [env.pos_id.id],
                'data_models': ['nh.clinical.patient.register'],
                'patient_ids': api.patient_map(cr, uid, pos_ids=[env.pos_id.id]).keys(),
                'location_ids': api.location_map(cr, uid, pos_ids=[env.pos_id.id]).keys(),
                'states': ['started', 'completed', 'scheduled'],
                #'device_ids': api.device_map(cr, uid, pos_ids=[env.pos_id.id]).keys(),
                }
        #print "==================== ACTIVITY MAP args ==========================="
        for i in range (len(args)*10):
            keys = [fake.random_element(args.keys()) for j in range(fake.random_int(1, len(args)-1))]
            kwargs = {k: args[k] for k in keys}
            domain = [[k[:-1],'in',args[k]] for k in keys] # :-1 to remove 's'
            #print "testing kwargs: %s" % (kwargs.keys())
            activity_map = api.activity_map(cr, uid, **kwargs)
            activity_ids = activity_model.search(cr, uid, domain)
            assert len(activity_map) == len(activity_ids)
            assert set(activity_map.keys()) == set(activity_ids) 
      