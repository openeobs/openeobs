# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
import logging
import bisect
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class t4_clinical_patient_observation(orm.AbstractModel):
    _name = 't4.clinical.patient.observation'
    _inherit = ['t4.activity.data']    
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
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, data_vals['patient_id'], context=context)
        except_if(not spell_activity_id, msg="Current spell is not found for patient_id: %s" %  data_vals['patient_id'])
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
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        placement_pool = self.pool['t4.clinical.patient.placement']
        # FIXME + placement.id child_of current_spell_activity
        placement = placement_pool.browse_domain(cr, uid, [('patient_id','=',patient_id),('state','=','completed')], limit=1, order="date_terminated desc")
        #import pdb; pdb.set_trace()
        location_id = placement and placement[0].location_id.id or False
        return location_id     

# deprecated
class t4_clinical_patient_observation_height_weight(orm.Model):
    _name = 't4.clinical.patient.observation.height_weight'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['height', 'weight']
    _columns = {
                       
        'height': fields.float('Height'),
        'weight': fields.float('Weight'),
    }

class t4_clinical_patient_observation_height(orm.Model):
    _name = 't4.clinical.patient.observation.height'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['height']
    _columns = {
        'height': fields.float('Height'),
    }

class t4_clinical_patient_observation_weight(orm.Model):
    _name = 't4.clinical.patient.observation.weight'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['weight']
    _columns = {
        'weight': fields.float('Weight'),
    }


class t4_clinical_patient_observation_blood_product(orm.Model):
    _name = 't4.clinical.patient.observation.blood_product'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['vol', 'product']
    _columns = {
        'vol': fields.float('Blood Product Vol'),
        'product': fields.selection((('rbc', 'RBC'),
                                    ('ffp', 'FFP'),
                                    ('platelets', 'Platelets'),
                                    ('has', 'Human Albumin Sol'),
                                    ('dli', 'DLI'),
                                    ('stem', 'Stem Cells')), 'Blood Product'),
    }


class t4_clinical_patient_observation_blood_sugar(orm.Model):
    _name = 't4.clinical.patient.observation.blood_sugar'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['blood_sugar']
    _columns = {
        'blood_sugar': fields.float('Blood Sugar'),
    }


class t4_clinical_patient_observation_stools(orm.Model):
    _name = 't4.clinical.patient.observation.stools'
    _inherit = ['t4.clinical.patient.observation']
    _required = []
    _columns = {
        'bowel_open': fields.boolean('Bowel Open'),
        'nausea': fields.boolean('Nausea'),
        'vomiting': fields.boolean('Vomiting'),
        'quantity': fields.selection((('large', 'Large'),
                                    ('medium', 'Medium'),
                                    ('small', 'Small')), 'Quantity'),
        'colour': fields.selection((('brown', 'Brown'),
                                    ('yellow', 'Yellow'),
                                    ('green', 'Green'),
                                    ('black', 'Black/Tarry'),
                                    ('red', 'Red (fresh blood)'),
                                    ('clay', 'Clay')), 'Colour'),
        'bristol_type': fields.selection((('1', 'Type 1'), ('2', 'Type 2'), ('3', 'Type 3'), ('4', 'Type 4'),
                                        ('5', 'Type 5'), ('6', 'Type 6'), ('7', 'Type 7')), 'Bristol Type'),
        'offensive': fields.boolean('Offensive'),
        'strain': fields.boolean('Strain'),
        'laxatives': fields.boolean('Laxatives'),
        'samples': fields.selection((('none', 'None'),
                                    ('micro', 'Micro'),
                                    ('virol', 'Virol'),
                                    ('m+v', 'M+V')), 'Lab Samples'),
        'rectal_exam': fields.boolean('Rectal Exam'),
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
               'notifications': [[], ['Assess patient'], ['Urgently inform medical team'], ['Immediately inform medical team']],
               'risk': ['None', 'Low', 'Medium', 'High']}
    
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

            case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], score)])
            case = 2 if three_in_one and case < 3 else case
            clinical_risk = self._POLICY['risk'][case]

            res[ews.id] = {'score': score, 'three_in_one': three_in_one, 'clinical_risk': clinical_risk}
            _logger.debug("Observation EWS activity_id=%s ews_id=%s score: %s" % (ews.activity_id.id, ews.id, res[ews.id]))
        return res

    def _data2ews_ids(self, cr, uid, ids, context=None):
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        ews_ids = ews_pool.search(cr, uid, [('activity_id', 'in', ids)], context=context)
        return ews_ids
    
    _columns = {
        #'duration': fields.integer('Duration'),
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store= {
                       't4.clinical.patient.observation.ews': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
                         }),
        'three_in_one': fields.function(_get_score, type='boolean', multi='score', string='3 in 1 flag', store= {
                       't4.clinical.patient.observation.ews': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
                         }),
        'clinical_risk': fields.function(_get_score, type='char', multi='score', string='Clinical Risk', store={
            't4.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, [], 10)
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
        'order_by': fields.related('activity_id', 'date_terminated', type='datetime', string='Date Terminated', store={
            't4.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, ['activity_id'], 10),
            't4.activity.data': (_data2ews_ids, ['date_terminated'], 20)
        })
    }

    _order = "order_by desc, id desc"

    def submit(self, cr, uid, activity_id, data_vals={}, context=None):
        vals = data_vals.copy()
        if vals.get('oxygen_administration'):
            vals.update({'oxygen_administration_flag': vals['oxygen_administration'].get('oxygen_administration_flag')})
            del vals['oxygen_administration']


        return super(t4_clinical_patient_observation_ews, self).submit(cr, SUPERUSER_ID, activity_id, data_vals, context)      
    
    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default EWS policy
        """
        activity_pool = self.pool['t4.activity']
        hca_pool = self.pool['t4.clinical.notification.hca']
        nurse_pool = self.pool['t4.clinical.notification.nurse']
        groups_pool = self.pool['res.groups']
        api_pool = self.pool['t4.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        case = 2 if activity.data_ref.three_in_one and case < 3 else case
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'T4 Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'T4 Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False
        if group == 'hca':
            hca_pool.create_activity(cr,  SUPERUSER_ID, {'summary': 'Inform registered nurse', 'creator_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
            nurse_pool.create_activity(cr, SUPERUSER_ID, {'summary': 'Informed about patient status', 'creator_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
        if case:
            for n in self._POLICY['notifications'][case]:
                nurse_pool.create_activity(cr, SUPERUSER_ID, {'summary': n, 'creator_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
        # create next EWS
        spell_activity_id = activity.parent_id.id
        next_activity_id = self.create_activity(cr, SUPERUSER_ID, 
                             {'creator_id': activity_id, 'parent_id': spell_activity_id},
                             {'patient_id': activity.data_ref.patient_id.id})
        activity_pool.schedule(cr, SUPERUSER_ID, next_activity_id, dt.today()+rd(minutes=self._POLICY['frequencies'][case]))
        activity_pool.submit(cr, SUPERUSER_ID, spell_activity_id, 
                             {'ews_frequency':self._POLICY['frequencies'][case]},
                             context)
        return super(t4_clinical_patient_observation_ews, self).complete(cr, SUPERUSER_ID, activity_id, context)

class t4_clinical_patient_observation_gcs(orm.Model):
    _name = 't4.clinical.patient.observation.gcs'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['eyes', 'verbal', 'motor']
    _eyes = [('1', '1: Does not open eyes'),
             ('2', '2: Opens eyes in response to painful stimuli'),
             ('3', '3: Opens eyes in response to voice'),
             ('4', '4: Opens eyes spontaneously'),
             ('C', 'C: Closed by swelling')]
    _verbal = [('1', '1: Makes no sounds'),
               ('2', '2: Incomprehensible sounds'),
               ('3', '3: Utters inappropiate words'),
               ('4', '4: Confused, disoriented'),
               ('5', '5: Oriented, converses normally'),
               ('T', 'T: Intubated')]
    _motor = [('1', '1: Makes no movements'),
              ('2', '2: Extension to painful stimuli (decerebrate response)'),
              ('3', '3: Abnormal flexion to painful stimuli (decorticate response)'),
              ('4', '4: Flexion / Withdrawal to painful stimuli'),
              ('5', '5: Localizes painful stimuli'),
              ('6', '6: Obeys commands')]

    """
    Default GCS policy has 5 different scenarios:
        case 0: 30 min frequency
        case 1: 1 hour frequency
        case 2: 2 hour frequency
        case 3: 4 hour frequency
        case 4: 12 hour frequency (no clinical risk)
    """
    _POLICY = {'ranges': [5, 9, 13, 14], 'case': '01234', 'frequencies': [30, 60, 120, 240, 720],
               'notifications': [[], [], [], [], []]}

    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for gcs in self.browse(cr, uid, ids, context):
            eyes = 1 if gcs.eyes == 'C' else int(gcs.eyes)
            verbal = 1 if gcs.verbal == 'T' else int(gcs.verbal)
            motor = int(gcs.motor)

            res[gcs.id] = {'score': eyes+verbal+motor}
            _logger.debug("Observation GCS activity_id=%s gcs_id=%s score: %s" % (gcs.activity_id.id, gcs.id, res[gcs.id]))
        return res

    _columns = {
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store={
                       't4.clinical.patient.observation.gcs': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
        }),
        'eyes': fields.selection(_eyes, 'Eyes'),
        'verbal': fields.selection(_verbal, 'Verbal'),
        'motor': fields.selection(_motor, 'Motor')
    }

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default GCS policy
        """
        activity_pool = self.pool['t4.activity']
        nurse_pool = self.pool['t4.clinical.notification.nurse']
        api_pool = self.pool['t4.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        for n in self._POLICY['notifications'][case]:
            nurse_pool.create_activity(cr, SUPERUSER_ID, {'summary': n, 'creator_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})
        # create next GCS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID, 
                             {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                             {'patient_id': activity.data_ref.patient_id.id})
        self.schedule(cr, SUPERUSER_ID, next_activity_id, dt.today()+rd(minutes=self._POLICY['frequencies'][case]))
        return super(t4_clinical_patient_observation_gcs, self).complete(cr, SUPERUSER_ID, activity_id, context)


class t4_clinical_patient_observation_vips(orm.Model):
    _name = 't4.clinical.patient.observation.vips'
    _inherit = ['t4.clinical.patient.observation']
    _required = ['pain', 'redness', 'swelling', 'cord', 'pyrexia']
    _selection = [('no', 'No'), ('yes', 'Yes')]

    """
    Default VIPS policy has 4 different scenarios:
        case 0: No plebitis
        case 1: Early stage of plebitis --> Resite cannula
        case 2: Advanced stage of plebitis --> Consider plebitis treatment
        case 3: Advanced stage of thrombophlebitis --> Initiate phlebitis treatment
    """
    _POLICY = {'ranges': [1, 2, 4], 'case': '0123', 'frequencies': [1440, 1440, 1440, 1440],
               'notifications': [[], ['Resite Cannula'], ['Resite Cannula', 'Consider plebitis treatment'], ['Resite Cannula', 'Initiate phlebitis treatment']]}

    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for vips in self.browse(cr, uid, ids, context):
            score = 0
            pain = vips.pain == 'yes'
            redness = vips.redness == 'yes'
            swelling = vips.swelling == 'yes'
            cord = vips.cord == 'yes'
            pyrexia = vips.pyrexia == 'yes'

            if all([pain, redness, swelling, cord, pyrexia]):
                score = 5
            elif all([pain, redness, swelling, cord]):
                score = 4
            elif all([pain, redness, swelling]):
                score = 3
            elif all([pain, redness]) or all([pain, swelling]) or all([redness, swelling]):
                score = 2
            elif any([pain, redness]):
                score = 1

            res[vips.id] = {'score': score}
            _logger.debug("Observation VIPS activity_id=%s vips_id=%s score: %s" % (vips.activity_id.id, vips.id, res[vips.id]))
        return res

    _columns = {
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store={
                       't4.clinical.patient.observation.vips': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
        }),
        'pain': fields.selection(_selection, 'Pain'),
        'redness': fields.selection(_selection, 'Redness'),
        'swelling': fields.selection(_selection, 'Swelling'),
        'cord': fields.selection(_selection, 'Palpable venous cord'),
        'pyrexia': fields.selection(_selection, 'Pyrexia'),
    }

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default VIPS policy
        """
        activity_pool = self.pool['t4.activity']
        nurse_pool = self.pool['t4.clinical.notification.nurse']
        api_pool = self.pool['t4.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        for n in self._POLICY['notifications'][case]:
            nurse_pool.create_activity(cr, SUPERUSER_ID, {'summary': n, 'creator_id': activity_id}, {'patient_id': activity.data_ref.patient_id.id})

        # create next VIPS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID, 
                             {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                             {'patient_id': activity.data_ref.patient_id.id})
        activity_pool.schedule(cr, SUPERUSER_ID, next_activity_id, dt.today()+rd(minutes=self._POLICY['frequencies'][case]))        
        return super(t4_clinical_patient_observation_vips, self).complete(cr, SUPERUSER_ID, activity_id, context)
