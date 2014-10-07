# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
_logger = logging.getLogger(__name__)


class nh_clinical_o2level(orm.Model):
    _name = 'nh.clinical.o2level'

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['max', 'min'], context=context):
            result[r['id']] = str(r['min']) + '-' + str(r['max'])
        return result

    _columns = {
        'name': fields.function(_get_name, 'O2 Target', type='char', size=10),
        'min': fields.integer("Min"),
        'max': fields.integer("Max"),
        'active': fields.boolean('Active', help="If the active field is set to false, it will allow you to hide the"
                                                " O2 target without removing it."),
    }
    _defaults = {
        'active': True
    }

    def unlink(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'active': False}, context=context)


class nh_clinical_patient_o2target(orm.Model):
    _name = 'nh.clinical.patient.o2target'
    _inherit = ['nh.activity.data']
    _rec_name = 'level_id'
    _columns = {
        'level_id': fields.many2one('nh.clinical.o2level', 'O2 Level', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }