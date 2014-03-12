# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_patient_observation(orm.AbstractModel):
    _name = 't4.clinical.patient.observation'
    _inherit = ['t4.clinical.task.data']    
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
    
    def create_task(self, cr, uid, task_vals={}, data_vals={}, context=None):
        task_pool = self.pool['t4.clinical.task']
        patient_id = data_vals['patient_id']
        spell_task_id = task_pool.get_patient_spell_task_id(cr, uid, patient_id, context)
        except_if(not spell_task_id, msg="Current spell is not found for patient_id: %s" % patient_id)
        task_vals.update({'parent_id': spell_task_id})
        return super(t4_clinical_patient_observation, self).create_task(cr, uid, task_vals, data_vals, context)      
                
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

    def get_task_location_id(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        patient_id = task.data_ref.patient_id.id
        placement_pool = self.pool['t4.clinical.patient.placement']
        # FIXME + placement.id child_of current_spell_task
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


class score(object):
    _ranges = []
    _limit_per_one = 3
    _limit_in_one = False
    _score = 0

    def add_range(self, key=None, value=None, min=None, max=None, selection=None, score=None):
        assert isinstance(key, basestring), "Key must be a string"
        assert value is not None, "Value can't be None"
        assert score is not None, "Score can't be None"
        assert (isinstance(min, (int, long)) or isinstance(max, (int, long))) or isinstance(selection, (list,tuple)), "min-max or selection must be set"

        self._ranges.append({'key': key, 'value': value, 'min': min, 'max': max, 'selection': selection, 'score': score})

    def get_score(self):
        for r in self._ranges:
            min_max_test = r['min'] and r['value'] >= r['min'] or not r['min'] \
                            and r['max'] and r['value'] <= r['max'] or not r['max']
            if min_max_test:
                r.update({'match': True, 'reason': 'min-max'})
            elif r['selection'] and r['value'] in r['selection']:
                r.update({'match': True, 'reason': 'selection'})
            else:
                r.update({'match': False, 'reason': ''})
        for r in self._ranges:
            if r['match']:
                self._score += r['score']
                self._limit_in_one = r['score'] >= self._limit_per_one
                
        return self._score, self._limit_in_one


class t4_clinical_patient_observation_ews(orm.Model):
    _name = 't4.clinical.patient.observation.ews'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['respiration_rate', 'indirect_oxymetry_spo2', 'body_temperature', 'blood_pressure_systolic', 'pulse_rate']
    
    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context):
            score = 0
            three_in_one = False
    
            if ews.respiration_rate <= 8:
                score += 3
                three_in_one = True
            elif ews.respiration_rate <= 11:
                score += 1
            elif ews.respiration_rate <= 20:
                score += 0
            elif ews.respiration_rate <= 24:
                score += 2
            else:
                score += 3
                three_in_one = True
    
            if ews.indirect_oxymetry_spo2 <= 91:
                score += 3
                three_in_one = True
            elif ews.indirect_oxymetry_spo2 < 94:
                score += 2
            elif ews.indirect_oxymetry_spo2 < 96:
                score += 1
            else:
                score += 0
    
            if ews.oxygen_administration_flag:
                score += 2
    
            if ews.body_temperature <= 35.0:
                score += 3
                three_in_one = True
            elif ews.body_temperature < 36.1:
                score += 1
            elif ews.body_temperature < 38.1:
                score += 0
            elif ews.body_temperature < 39.1:
                score += 1
            else:
                score += 2
    
            if ews.blood_pressure_systolic <= 90:
                score += 3
                three_in_one = True
            elif ews.blood_pressure_systolic <= 100:
                score += 2
            elif ews.blood_pressure_systolic <= 110:
                score += 1
            elif ews.blood_pressure_systolic <= 219:
                score += 0
            else:
                score += 3
                three_in_one = True
    
            if ews.pulse_rate <= 40:
                score += 3
                three_in_one = True
            elif ews.pulse_rate < 51:
                score += 1
            elif ews.pulse_rate < 91:
                score += 0
            elif ews.pulse_rate < 111:
                score += 1
            elif ews.pulse_rate < 131:
                score += 2
            else:
                score += 3
                three_in_one = True
    
            if ews.avpu_text in ['V', 'P', 'U']:
                score += 3
                three_in_one = True
            res[ews.id] = {'score': score, 'three_in_one': three_in_one}
            _logger.info("Observation EWS task_id=%s ews_id=%s score: %s" % (ews.task_id.id, ews.id, res[ews.id]))
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
        #'o2_device_reading_id': fields.many2one('t4skr.device.reading', 'Supplemental O2 Paramenters'),
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

    def submit(self, cr, uid, task_id, data_vals={}, context=None):
        vals = data_vals.copy()
        if vals.get('oxygen_administration'):
            vals.update({'oxygen_administration_flag': vals['oxygen_administration'].get('oxygen_administration_flag')})
            del vals['oxygen_administration']

        return super(t4_clinical_patient_observation_ews, self).submit(cr, uid, task_id, data_vals, context)   