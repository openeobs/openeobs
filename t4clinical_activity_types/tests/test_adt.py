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


class test_adt(common.SingleTransactionCase):

    def setUp(self):
        super(test_adt, self).setUp()
        
    def test_adt_admit(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 2,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
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
        cr, uid = self.cr, self.uid
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 1,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        spell_activities = api.get_activities(cr, uid, data_models=['t4.clinical.spell'], pos_ids=[env.pos_id.id], states=['started'])
        patient = spell_activities[0].patient_id
        discharge_activity = env_pool.create_activity(cr, uid, env_id, 't4.clinical.adt.patient.discharge', {}, {'other_identifier': patient.other_identifier}, True)
        env_pool.complete(cr, uid, env_id, discharge_activity.id)


    def test_adt_register(self):
        return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 0,
        }       
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
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

