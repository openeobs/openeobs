from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}

class test_activity(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global activity_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool, api_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_activity_id, discharge_activity_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow