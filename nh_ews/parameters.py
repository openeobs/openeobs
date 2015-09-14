# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_observations.helpers import refresh_materialized_views
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
        'level_id': fields.many2one('nh.clinical.o2level', 'O2 Level'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def get_last(self, cr, uid, patient_id, datetime=False, context=None):
        """
        Checks if there is an O2 Target assigned for the provided Patient
        :return: False if there is no assigned O2 Target.
                nh.clinical.o2level id of the last assigned O2 Target
        """
        if not datetime:
            datetime = dt.now().strftime(dtf)
        domain = [['patient_id', '=', patient_id], ['data_model', '=', 'nh.clinical.patient.o2target'],
                  ['state', '=', 'completed'], ['parent_id.state', '=', 'started'], ['date_terminated', '<=', datetime]]
        activity_pool = self.pool['nh.activity']
        o2target_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc, sequence desc',
                                            context=context)
        if not o2target_ids:
            return False
        activity = activity_pool.browse(cr, uid, o2target_ids[0], context=context)
        return activity.data_ref.level_id.id if activity.data_ref.level_id else False

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_o2target, self).complete(cr, uid, activity_id, context)
        return res
