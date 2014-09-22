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
        placement_activity_id = api_demo.register_admit_place(cr, uid, bed_id)
        placement_activity = api.browse(cr, uid, 't4.activity', placement_activity_id)
        spell_activity_id = placement_activity.parent_id.id
        assert spell_activity_id
        location_id = placement_activity.parent_id.location_id.id
        assert location_id
        nurse_user = api.browse(cr, uid, 'res.users', nurse_id)
        assert not nurse_user.location_ids
        # ORM ACL
        # user.location_ids is False
        domain = [('id', '=', spell_activity_id)]
        spell_ids = api.search(cr, nurse_id, 't4.clinical.spell', domain)
        assert not spell_ids
        
        # add location
        print "ADD LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[4, location_id]]}) 
        nurse_user = api.browse(cr, uid, 'res.users', nurse_id)
        assert location_id in [l.id for l in nurse_user.location_ids]
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert nurse_id in [u.id for u in spell_activity.user_ids]
        # remove location
        print "DELETE LOCATION"
        api.write(cr, uid, 'res.users', nurse_id, {'location_ids': [[3, location_id]]})
        assert location_id not in [l.id for l in nurse_user.location_ids]
        spell_activity = api.browse(cr, uid, 't4.activity', spell_activity_id)
        assert nurse_id in [u.id for u in spell_activity.user_ids], "Spell activity must be accessible anyway!"
        
        # add/remove group













