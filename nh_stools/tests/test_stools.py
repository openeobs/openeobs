# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests import common

import logging        
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class TestBristolStools(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestBristolStools, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')

        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.stools_pool = cls.registry('nh.clinical.patient.observation.stools')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4, patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_bristol_stools(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.patient_pool.search(cr, uid, [['current_location_id.usage', '=', 'bed'], ['current_location_id.parent_id', 'in', [self.wu_id, self.wt_id]]])
        self.assertTrue(patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', patient_id]])
        self.assertTrue(spell_ids, msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.nu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.nu_id
        else:
            user_id = self.nt_id

        for i in range(25):
            stools_activity_id = self.stools_pool.create_activity(cr, uid, {'parent_id': spell_activity.id}, {'patient_id': spell_activity.patient_id.id})
            data = {
                'bowel_open': fake.random_element([True, False]),
                'nausea': fake.random_element([True, False]),
                'vomiting': fake.random_element([True, False]),
                'quantity': fake.random_element(['large', 'medium', 'small']),
                'colour': fake.random_element(['brown', 'yellow', 'green', 'black', 'red', 'clay']),
                'bristol_type': fake.random_element(['1', '2', '3', '4', '5', '6', '7']),
                'offensive': fake.random_element([True, False]),
                'strain': fake.random_element([True, False]),
                'laxatives': fake.random_element([True, False]),
                'samples': fake.random_element(['none', 'micro', 'virol', 'm+v']),
                'rectal_exam': fake.random_element([True, False])
            }
            self.activity_pool.assign(cr, uid, stools_activity_id, user_id)
            self.activity_pool.submit(cr, user_id, stools_activity_id, data)
            self.activity_pool.complete(cr, user_id, stools_activity_id)
            stools_activity = self.activity_pool.browse(cr, uid, stools_activity_id)
            self.assertTrue(stools_activity.state == 'completed', msg="Bristol Stools not completed")
            self.assertTrue(stools_activity.date_terminated, msg="Bristol Stools date terminated not registered")
            for key in data.keys():
                self.assertTrue(eval('stools_activity.data_ref.'+key) == data[key], msg="Bristol Stools Completed: %s not submitted correctly" % key)
