# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd

import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_api(orm.Model):
    _name = 't4.clinical.api'
    


class t4_clinical_api_adt(orm.Model):
    _name = 't4.clinical.api.adt'
    
    
class t4_clinical_api_frontend(orm.Model):
    _name = 't4.clinical.api.frontend'