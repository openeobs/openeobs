# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging
import bisect

_logger = logging.getLogger(__name__)


class t4_clinical_patient_observation(orm.AbstractModel):
    _name = 't4.clinical.patient.observation'
    _inherit = ['t4.clinical.activity.data']    
    _required = [] # fields required for complete observation
    
    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {obs['id']: bool(set(self._required) & set(eval(obs['none_values']))) for obs in self.read(cr, uid, ids, ['none_values'], context)}
        print 'is_partial: %s' % res
        #import pdb; pdb.set_trace()
        return res    
    
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'is_partial': fields.function(_is_partial, type='boolean', string='Is Partial?'),
        'none_values': fields.text('Non-updated fields'),
        
        
    }
    _defaults = {

     }
    
    def create(self, cr, uid, vals, context=None):
        none_values = list(set(self._required) - set(vals.keys()))
        vals.update({'none_values': none_values})
        #print "create none_values: %s" % none_values
        return super(t4_clinical_patient_observation, self).create(cr, uid, vals, context)        
    
    def create_activity(self, cr, uid, activity_vals={}, data_vals={}, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        patient_id = data_vals['patient_id']
        spell_activity_id = activity_pool.get_patient_spell_activity_id(cr, uid, patient_id, context)
        except_if(not spell_activity_id, msg="Current spell is not found for patient_id: %s" % patient_id)
        activity_vals.update({'parent_id': spell_activity_id})
        return super(t4_clinical_patient_observation, self).create_activity(cr, uid, activity_vals, data_vals, context)      
                
    def write(self, cr, uid, ids, vals, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required:
            return super(t4_clinical_patient_observation, self).write(cr, uid, ids, vals, context)
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            none_values = list(set(eval(obs['none_values'])) - set(vals.keys()))
            vals.update({'none_values': none_values})
            print "write none_values: %s" % none_values
            super(t4_clinical_patient_observation, self).write(cr, uid, obs['id'], vals, context)
        return True

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        placement_pool = self.pool['t4.clinical.patient.placement']
        # FIXME + placement.id child_of current_spell_activity
        placement = placement_pool.browse_domain(cr, uid, [('patient_id','=',patient_id),('state','=','completed')], limit=1, order="date_terminated desc")
        #import pdb; pdb.set_trace()
        location_id = placement and placement[0].location_id.id or False
        return location_id     


class t4_clinical_patient_observation_height_weight(orm.Model):
    _name = 't4.clinical.patient.observation.height_weight'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['height', 'weight']
    _columns = {
                       
        'height': fields.float('Height'),
        'weight': fields.float('Weight'),
    }


class t4_clinical_patient_observation_ews(orm.Model):
    _name = 't4.clinical.patient.observation.ews'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['respiration_rate', 'indirect_oxymetry_spo2', 'body_temperature', 'blood_pressure_systolic', 'pulse_rate']

    _RR_RANGES = {'ranges': [8, 11, 20, 24], 'scores': '31023'}
    _O2_RANGES = {'ranges': [91, 93, 95], 'scores': '3210'}
    _BT_RANGES = {'ranges': [35.0, 36.0, 38.0, 39.0], 'scores': '31012'}
    _BP_RANGES = {'ranges': [90, 100, 110, 219], 'scores': '32103'}
    _PR_RANGES = {'ranges': [40, 50, 90, 110, 130], 'scores': '310123'}
    """
    Default EWS policy has 4 different scenarios:
        case 0: no clinical risk
        case 1: low clinical risk
        case 2: medium clinical risk
        case 3: high clinical risk
    """
    _POLICY = {'ranges': [0, 4, 6], 'case': '0123', 'frequencies': [720, 240, 60, 30],
               'notifications': [[], ['Assess patient'], ['Urgently inform medical team'], ['Immediately inform medical team']]}
    
    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context):
            score = 0
            three_in_one = False

            aux = int(self._RR_RANGES['scores'][bisect.bisect_left(self._RR_RANGES['ranges'], ews.respiration_rate)])
            three_in_one = three_in_one or aux == 3
            score += aux

            aux = int(self._O2_RANGES['scores'][bisect.bisect_left(self._O2_RANGES['ranges'], ews.indirect_oxymetry_spo2)])
            three_in_one = three_in_one or aux == 3
            score += aux

            aux = int(self._BT_RANGES['scores'][bisect.bisect_left(self._BT_RANGES['ranges'], ews.body_temperature)])
            three_in_one = three_in_one or aux == 3
            score += aux

            aux = int(self._BP_RANGES['scores'][bisect.bisect_left(self._BP_RANGES['ranges'], ews.blood_pressure_systolic)])
            three_in_one = three_in_one or aux == 3
            score += aux

            aux = int(self._PR_RANGES['scores'][bisect.bisect_left(self._PR_RANGES['ranges'], ews.pulse_rate)])
            three_in_one = three_in_one or aux == 3
            score += aux

            score += 2 if ews.oxygen_administration_flag else 0

            score += 3 if ews.avpu_text in ['V', 'P', 'U'] else 0
            three_in_one = True if ews.avpu_text in ['V', 'P', 'U'] else three_in_one

            res[ews.id] = {'score': score, 'three_in_one': three_in_one}
            _logger.info("Observation EWS activity_id=%s ews_id=%s score: %s" % (ews.activity_id.id, ews.id, res[ews.id]))
        return res    
    
    _columns = {
        #'duration': fields.integer('Duration'),
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store= {
                       't4.clinical.patient.observation.ews': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
                         }),
        'three_in_one': fields.function(_get_score, type='boolean', multi='score', string='3 in 1 flag', store= {
                       't4.clinical.patient.observation.ews': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
                         }),
        'respiration_rate': fields.integer('Respiration Rate'),
        'indirect_oxymetry_spo2': fields.integer('O2 Saturation'),
        'oxygen_administration_flag': fields.boolean('Oxygen Administration Flag'),
        'body_temperature': fields.float('Body Temperature', digits=(3, 1)),
        'blood_pressure_systolic': fields.integer('Blood Pressure Systolic'),
        'blood_pressure_diastolic': fields.integer('Blood Pressure Diastolic'),
        'pulse_rate': fields.integer('Pulse Rate'),
        'avpu_text': fields.selection((('A', 'Alert'),
                                       ('V', 'Voice'),
                                       ('P', 'Pain'),
                                       ('U', 'Unresponsive')), 'AVPU'),
        'mews_score': fields.integer('Mews Score'),
        # O2 stuff former 'o2_device_reading_id'
        'flow_rate': fields.integer('Flow rate (l/min)'),
        'concentration': fields.integer('Concentration (%)'),
        'cpap_peep': fields.integer('CPAP: PEEP (cmH2O)'),
        'niv_backup': fields.integer('NIV: Back-up rate (br/min)'),
        'niv_ipap': fields.integer('NIV: IPAP (cmH2O)'),
        'niv_epap': fields.integer('NIV: EPAP (cmH2O)'),
        #'device_instance_id': fields.many2one('t4clinical.device.instance', 'Device', required=True),        
    }

    def submit(self, cr, uid, activity_id, data_vals={}, context=None):
        vals = data_vals.copy()
        if vals.get('oxygen_administration'):
            vals.update({'oxygen_administration_flag': vals['oxygen_administration'].get('oxygen_administration_flag')})
            del vals['oxygen_administration']


        return super(t4_clinical_patient_observation_ews, self).submit(cr, self.admin_uid(cr), activity_id, data_vals, context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default EWS policy
        """
        activity_pool = self.pool['t4.clinical.activity']
        hca_pool = self.pool['t4.clinical.notification.hca']
        nurse_pool = self.pool['t4.clinical.notification.nurse']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        case = 2 if activity.data_ref.three_in_one and case < 3 else case
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'T4 Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'T4 Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False
        if group == 'hca':
            hca_pool.create_activity(cr,  self.admin_uid(cr), {'summary': 'Inform registered nurse', 'creator_activity_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
            nurse_pool.create_activity(cr, self.admin_uid(cr), {'summary': 'Informed about patient status', 'creator_activity_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
        if case:
            for n in self._POLICY['notifications'][case]:
                nurse_pool.create_activity(cr, self.admin_uid(cr), {'summary': n, 'creator_activity_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
        activity_pool.set_activity_trigger(cr, self.admin_uid(cr), activity.data_ref.patient_id.id,
                                           't4.clinical.patient.observation.ews', 'minute',
                                           self._POLICY['frequencies'][case], context)
        return super(t4_clinical_patient_observation_ews, self).complete(cr, self.admin_uid(cr), activity_id, context)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    