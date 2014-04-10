# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)
class observation_test(orm.Model):
    _name = 'observation.test'
    _inherit = ['t4.clinical.activity.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2'),
        'datetime': fields.datetime('datetime'),
        'source': fields.text('source'),
}



class test_activity_data(orm.Model):
    _name = 'test.activity.data'
    _inherit = ['t4.clinical.activity.data']    
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', readonly=True),
        'location_id': fields.many2one('t4.clinical.location', 'Location', readonly=True),        
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', readonly=True),
}      