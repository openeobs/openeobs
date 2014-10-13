from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_user_activity_responsibility(SingleTransactionCase):
    @classmethod
    def tearDownClass(cls):
        if config['test_commit']:
            cls.cr.commit()
            print "COMMIT"
        else:
            cls.cr.rollback()
            print "ROLLBACK"
        cls.cr.close()
        

    def setUp(self):
        global cr, uid
        cr, uid = self.cr, self.uid
        
        super(test_user_activity_responsibility, self).setUp()
    
    def user_activity_resp(self, user_id, activity_id):
        global cr, uid
        api = self.registry('nh.clinical.api')
        activity = api.browse(cr, uid, 'nh.activity', activity_id)
        return any([user_id == u.id for u in activity.user_ids])

    def user_location_resp(self, user_id, location_id):
        global cr, uid
        api = self.registry('nh.clinical.api')
        user = api.browse(cr, uid, 'res.users', user_id)
        return any([location_id == l.id for l in user.location_ids])
    
    def user_add_location(self, user_id, location_id):
        global cr, uid
        api = self.registry('nh.clinical.api')        
        api.write(cr, uid, 'res.users', user_id, {'location_ids': [[4, location_id]]})    
        return api.browse(cr, uid, 'res.users', user_id)

    def user_remove_location(self, user_id, location_id):
        global cr, uid
        api = self.registry('nh.clinical.api')        
        api.write(cr, uid, 'res.users', user_id, {'location_ids': [[3, location_id]]})    
        return api.browse(cr, uid, 'res.users', user_id)

    def user_add_group(self, user_id, group_xmlid):
        global cr, uid
        api = self.registry('nh.clinical.api') 
        imd_pool = self.registry('ir.model.data')
        group = imd_pool.get_object(cr, uid, "nh_clinical", group_xmlid)
        assert group
        api.write(cr, uid, 'res.users', user_id, {'groups_id': [[4, group.id]]})    
        return api.browse(cr, uid, 'res.users', user_id)

    def user_remove_group(self, user_id, group_xmlid):
        global cr, uid
        api = self.registry('nh.clinical.api') 
        imd_pool = self.registry('ir.model.data')
        group = imd_pool.get_object(cr, uid, "nh_clinical", group_xmlid)
        assert group
        api.write(cr, uid, 'res.users', user_id, {'groups_id': [[3, group.id]]})      
        return api.browse(cr, uid, 'res.users', user_id)

    def group_add_user(self, group_xmlid, user_id):
        global cr, uid
        api = self.registry('nh.clinical.api') 
        imd_pool = self.registry('ir.model.data')
        group = imd_pool.get_object(cr, uid, "nh_clinical", group_xmlid)
        assert group
        api.write(cr, uid, 'res.groups', group.id, {'users': [[4, user_id]]})    
        return api.browse(cr, uid, 'res.groups', group.id)

    def group_remove_user(self, user_id, group_xmlid):
        global cr, uid
        api = self.registry('nh.clinical.api') 
        imd_pool = self.registry('ir.model.data')
        group = imd_pool.get_object(cr, uid, "nh_clinical", group_xmlid)
        assert group
        api.write(cr, uid, 'res.groups', group.id, {'users': [[3, user_id]]})      
        return api.browse(cr, uid, 'res.groups', group.id)
        
    def test_spell_responsible_users(self):
        global cr, uid, seed
        api = self.registry('nh.clinical.api')
        api_demo = self.registry('nh.clinical.api.demo')
#         placement_model = self.registry('nh.clinical.patient.placement')
#         placement_model._POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring'}]}
        pos_id = api_demo.create(cr, uid, 'nh.clinical.pos') 
        
        ward_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_ward', {'pos_id': pos_id})
        bed_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_bed', {'parent_id': ward_id}) 
        bed_nurse_id = api_demo.create(cr, uid, 'res.users', 'user_nurse')
        ward_nurse_id = api_demo.create(cr, uid, 'res.users', 'user_nurse')
        ward = api.browse(cr, uid, 'nh.clinical.location', ward_id)
        
        # activity.data (SPELL) UPDATE
        self.user_add_location(bed_nurse_id, bed_id)
        self.user_add_location(ward_nurse_id, ward_id)
        assert self.user_location_resp(bed_nurse_id, bed_id)
        assert self.user_location_resp(ward_nurse_id, ward_id)
        placement_activity = api_demo.register_admit_place(cr, uid, bed_id, {}, admit_values={'location': ward.code})    
#         placement_activity = api.browse(cr, uid, 'nh.activity', placement_activity_id)
        assert placement_activity.parent_id.data_model == 'nh.clinical.spell'
        spell_activity_id = placement_activity.parent_id.id
        
        assert self.user_activity_resp(bed_nurse_id, spell_activity_id)
        assert self.user_activity_resp(ward_nurse_id, spell_activity_id)
        self.user_remove_location(bed_nurse_id, bed_id)
        self.user_remove_location(ward_nurse_id, ward_id)  
        assert not self.user_location_resp(bed_nurse_id, bed_id)
        assert not self.user_location_resp(ward_nurse_id, ward_id)             
        assert not self.user_activity_resp(bed_nurse_id, spell_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, spell_activity_id)       
        
        # WRITE location_ids ON RES.USER
        self.user_add_location(bed_nurse_id, bed_id)
        self.user_add_location(ward_nurse_id, ward_id)        
        assert self.user_location_resp(bed_nurse_id, bed_id)
        assert self.user_location_resp(ward_nurse_id, ward_id)        
        assert self.user_activity_resp(bed_nurse_id, spell_activity_id)
        assert self.user_activity_resp(ward_nurse_id, spell_activity_id)
        self.user_remove_location(bed_nurse_id, bed_id)
        self.user_remove_location(ward_nurse_id, ward_id)
        assert not self.user_location_resp(bed_nurse_id, bed_id)
        assert not self.user_location_resp(ward_nurse_id, ward_id) 
        assert not self.user_activity_resp(bed_nurse_id, spell_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, spell_activity_id)            
            
        # WRITE groups_id ON RES.USER
        bed_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        ward_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        self.user_add_location(bed_user_id, bed_id)
        self.user_add_location(ward_user_id, ward_id)        
        assert self.user_location_resp(bed_user_id, bed_id)
        assert self.user_location_resp(ward_user_id, ward_id)    
        assert not self.user_activity_resp(bed_user_id, spell_activity_id)
        assert not self.user_activity_resp(ward_user_id, spell_activity_id)
        self.user_add_group(bed_user_id, 'group_nhc_nurse')
        self.user_add_group(ward_user_id, 'group_nhc_nurse')
        assert self.user_activity_resp(bed_user_id, spell_activity_id)
        assert self.user_activity_resp(ward_user_id, spell_activity_id)        

        # WRITE users ON RES.GROUPS
        bed_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        ward_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        self.user_add_location(bed_user_id, bed_id)
        self.user_add_location(ward_user_id, ward_id)         
        assert self.user_location_resp(bed_user_id, bed_id)
        assert self.user_location_resp(ward_user_id, ward_id)         
        assert not self.user_activity_resp(bed_user_id, spell_activity_id)
        assert not self.user_activity_resp(ward_user_id, spell_activity_id)
        self.group_add_user('group_nhc_nurse', bed_user_id)
        self.group_add_user('group_nhc_nurse', ward_user_id)
        assert self.user_activity_resp(bed_user_id, spell_activity_id)
        assert self.user_activity_resp(ward_user_id, spell_activity_id)

    def test_ews_responsible_users(self):
        global cr, uid, seed
        api = self.registry('nh.clinical.api')
        api_demo = self.registry('nh.clinical.api.demo')
        placement_model = self.registry('nh.clinical.patient.placement')
        placement_model._POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring'}]}
        pos_id = api_demo.create(cr, uid, 'nh.clinical.pos') 
        
        ward_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_ward', {'pos_id': pos_id})
        bed_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_bed', {'parent_id': ward_id}) 
        bed_nurse_id = api_demo.create(cr, uid, 'res.users', 'user_nurse')
        ward_nurse_id = api_demo.create(cr, uid, 'res.users', 'user_nurse')
        ward = api.browse(cr, uid, 'nh.clinical.location', ward_id)
        
        # activity.data (GENERAL) UPDATE
        self.user_add_location(bed_nurse_id, bed_id)
        self.user_add_location(ward_nurse_id, ward_id)
        assert self.user_location_resp(bed_nurse_id, bed_id)
        assert self.user_location_resp(ward_nurse_id, ward_id)
        placement_activity = api_demo.register_admit_place(cr, uid, bed_id, {}, admit_values={'location': ward.code})    
#         placement_activity = api.browse(cr, uid, 'nh.activity', placement_activity_id)
        
        ews_activities = api.activity_map(cr, uid, pos_ids=[placement_activity.pos_id.id], patient_ids=[placement_activity.patient_id.id],
                                          data_models=['nh.clinical.patient.observation.ews'])
        assert ews_activities, "EWS activity not found"
        ews_activity_id = ews_activities.keys()[0]
        
        assert self.user_activity_resp(bed_nurse_id, ews_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, ews_activity_id)
        self.user_remove_location(bed_nurse_id, bed_id)
        self.user_remove_location(ward_nurse_id, ward_id)  
        assert not self.user_location_resp(bed_nurse_id, bed_id)
        assert not self.user_location_resp(ward_nurse_id, ward_id)             
        assert not self.user_activity_resp(bed_nurse_id, ews_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, ews_activity_id)       
        
        # WRITE location_ids ON RES.USER
        self.user_add_location(bed_nurse_id, bed_id)
        self.user_add_location(ward_nurse_id, ward_id)        
        assert self.user_location_resp(bed_nurse_id, bed_id)
        assert self.user_location_resp(ward_nurse_id, ward_id)        
        assert self.user_activity_resp(bed_nurse_id, ews_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, ews_activity_id)
        self.user_remove_location(bed_nurse_id, bed_id)
        self.user_remove_location(ward_nurse_id, ward_id)
        assert not self.user_location_resp(bed_nurse_id, bed_id)
        assert not self.user_location_resp(ward_nurse_id, ward_id) 
        assert not self.user_activity_resp(bed_nurse_id, ews_activity_id)
        assert not self.user_activity_resp(ward_nurse_id, ews_activity_id)            
             
        # WRITE groups_id ON RES.USER
        bed_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        ward_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        self.user_add_location(bed_user_id, bed_id)
        self.user_add_location(ward_user_id, ward_id)        
        assert self.user_location_resp(bed_user_id, bed_id)
        assert self.user_location_resp(ward_user_id, ward_id)    
        assert not self.user_activity_resp(bed_user_id, ews_activity_id)
        assert not self.user_activity_resp(ward_user_id, ews_activity_id)
        self.user_add_group(bed_user_id, 'group_nhc_nurse')
        self.user_add_group(ward_user_id, 'group_nhc_nurse')
        assert self.user_activity_resp(bed_user_id, ews_activity_id)
        assert not self.user_activity_resp(ward_user_id, ews_activity_id)        
 
        # WRITE users ON RES.GROUPS
        bed_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        ward_user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        self.user_add_location(bed_user_id, bed_id)
        self.user_add_location(ward_user_id, ward_id)         
        assert self.user_location_resp(bed_user_id, bed_id)
        assert self.user_location_resp(ward_user_id, ward_id)         
        assert not self.user_activity_resp(bed_user_id, ews_activity_id)
        assert not self.user_activity_resp(ward_user_id, ews_activity_id)
        self.group_add_user('group_nhc_nurse', bed_user_id)
        self.group_add_user('group_nhc_nurse', ward_user_id)
        assert self.user_activity_resp(bed_user_id, ews_activity_id)
        assert not self.user_activity_resp(ward_user_id, ews_activity_id)        
        
