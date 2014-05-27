# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)

class t4_clinical_device_session(orm.Model):
    _name = 't4.clinical.device.session'
    _description = 'Device Session'
    _inherit = ['t4.activity.data']
    _rec_name = 'device_id'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }
    
    def name_get(self, cr, uid, ids, context):
        res = []
        for session in self.browse(cr, uid, ids, context):
            res.append((session.id, session.device_id.type_id.name))
        return res
    
    def start(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        device_pool = self.pool['t4.clinical.device']
        device_pool.write(cr, uid, activity.data_ref.device_id.id, {'is_available': False})
        super(t4_clinical_device_session, self).start(cr, uid, activity_id, context)
        
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        device_pool = self.pool['t4.clinical.device']
        device_pool.write(cr, uid, activity.data_ref.device_id.id, {'is_available': True})
        super(t4_clinical_device_session, self).complete(cr, uid, activity_id, context)        
        
    
class t4_clinical_device_connect(orm.Model):
    _name = 't4.clinical.device.connect'
    _inherit = ['t4.activity.data']
    _description = 'Connect Device'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        device_session_pool = self.pool['t4.clinical.device.session']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, activity.patient_id.id)
        except_if(not spell_activity_id, msg="No started spell found for patient_id=%s" % activity.patient_id.id)
        session_activity_id = device_session_pool.create_activity(cr, uid, 
                                            {'creator_id': activity_id, 'parent_id': spell_activity_id},
                                            {'patient_id': activity.patient_id.id, 'device_id': activity.device_id.id})
        activity_pool.start(cr, uid, session_activity_id)
        return super(t4_clinical_device_connect, self).complete(cr, SUPERUSER_ID, activity_id, context)

class t4_clinical_device_disconnect(orm.Model):
    _name = 't4.clinical.device.disconnect'
    _inherit = ['t4.activity.data']
    _description = 'Disconnect Device'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        device_session_pool = self.pool['t4.clinical.device.session']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, activity.patient_id.id)
        except_if(not spell_activity_id, msg="No started spell found for patient_id=%s" % activity.patient_id.id)
        session_activity_id = api_pool.get_device_session_activity_id(cr, uid, activity.device_id.id)
        except_if(not session_activity_id, msg="No started session found for device_id=%s" % activity.device_id.id)
        activity_pool.complete(cr, uid, session_activity_id)
        return super(t4_clinical_device_disconnect, self).complete(cr, SUPERUSER_ID, activity_id, context)

    
class t4_clinical_device_observation(orm.Model):
    _name = 't4.clinical.device.observation'
    _inherit = ['t4.activity.data']
    _description = 'Device Observation'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }
    
