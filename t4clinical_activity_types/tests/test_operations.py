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


class test_operations(common.SingleTransactionCase):

    def setUp(self):
        super(test_operations, self).setUp()
        

    def test_placement(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 0,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
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