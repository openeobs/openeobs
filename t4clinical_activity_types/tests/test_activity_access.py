from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_activity_access(SingleTransactionCase):
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
        
        super(test_activity_access, self).setUp()
        
    def test_spell_access(self):
        global cr, uid, seed
        api = self.registry('t4.clinical.api')
        api_demo = self.registry('t4.clinical.api.demo')
        
        pos_id = api_demo.create(cr, uid, 't4.clinical.pos') 
        
        ward_id = api_demo.create(cr, uid, 't4.clinical.location', 'location_ward', {'pos_id': pos_id})
        bed_id = api_demo.create(cr, uid, 't4.clinical.location', 'location_bed', {'parent_id': ward_id}) 
        nurse_id = api_demo.create(cr, uid, 'res.users', 'user_nurse')
        bed_id = bed_id
        ward = api.browse(cr, uid, 't4.clinical.location', ward_id)
        
        # before SPELL creation: TEST of t4.clinical.spell update() 
        print "ADD LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[4, bed_id]]}) 
        nurse_user = api.browse(cr, uid, 'res.users', nurse_id)
        assert bed_id in [l.id for l in nurse_user.location_ids] 
        placement_activity_id = api_demo.register_admit_place(cr, uid, bed_id, {}, admit_values={'location': ward.code})    
        placement_activity = api.browse(cr, uid, 't4.activity', placement_activity_id)
        assert placement_activity.parent_id.data_model == 't4.clinical.spell'
        spell_activity_id = placement_activity.parent_id.id
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert spell_activity.location_id.id == bed_id
#         import pdb; pdb.set_trace()
        assert nurse_id in [u.id for u in spell_activity.user_ids], "spell.user_ids: %s" % [u.id for u in spell_activity.user_ids]
        print "DELETE LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[3, bed_id]]})
        assert bed_id not in [l.id for l in nurse_user.location_ids]
        nurse_user = api.browse(cr, uid, 'res.users', nurse_id)
        assert not nurse_user.location_ids
        
        # WRITE location_ids ON RES.USER
        print "ADD LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[4, bed_id]]}) 
        nurse_user = api.browse(cr, uid, 'res.users', nurse_id)
        assert bed_id in [l.id for l in nurse_user.location_ids]
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert nurse_id in [u.id for u in spell_activity.user_ids]
        print "DELETE LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[3, bed_id]]})
        assert bed_id not in [l.id for l in nurse_user.location_ids]
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert nurse_id not in [u.id for u in spell_activity.user_ids], "Spell activity must be accessible anyway!"
        
        # WRITE groups_id ON RES.USER
        print "NEW USER without 't4clinical' groups"
        user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        api.write(cr, uid, 'res.users', user_id, {'location_ids': [[4, bed_id]]}) 
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert user_id not in [u.id for u in spell_activity.user_ids], "User must not appear in activity.user_ids"
        print "NEW USER: adding group"
        imd_pool = self.registry('ir.model.data')
        group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")
        api.write(cr, uid, 'res.users', user_id, {'groups_id': [[4, group.id]]}) 
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert user_id in [u.id for u in spell_activity.user_ids], "User must appear in activity.user_ids after nurse group added!"

        # WRITE users ON RES.GROUPS
        print "NEW USER without 't4clinical' groups"
        user_id = api_demo.create(cr, uid, 'res.users', '_user_base')
        api.write(cr, uid, 'res.users', user_id, {'location_ids': [[4, bed_id]]}) 
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert user_id not in [u.id for u in spell_activity.user_ids], "User must not appear in activity.user_ids"        

        api.write(cr, uid, 'res.groups', group.id, {'users': [[4, user_id]]})
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert user_id in [u.id for u in spell_activity.user_ids], "User must appear in activity.user_ids after user added to nurse group!"       




