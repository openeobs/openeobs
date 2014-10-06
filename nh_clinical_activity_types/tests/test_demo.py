from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from pprint import pprint as pp

from openerp import tools
from openerp.osv import orm, fields, osv
from openerp.addons.nh_clinical_base.tests.test_base import BaseTest

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


class test_demo(common.SingleTransactionCase):

    def setUp(self):
        super(test_demo, self).setUp()
        
    def test_build_env(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('nh.clinical.demo.env')
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
        env_pool.browse(cr, uid, env_id)