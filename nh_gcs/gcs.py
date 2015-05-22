# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
from openerp.addons.nh_observations.parameters import frequencies
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from dateutil.relativedelta import relativedelta as rd
import logging
import bisect
from openerp import SUPERUSER_ID
from math import fabs

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_gcs(orm.Model):
    _name = 'nh.clinical.patient.observation.gcs'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['eyes', 'verbal', 'motor']
    _description = "GCS Observation"
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

    def calculate_score(self, gcs_data):
        eyes = 1 if gcs_data['eyes'] == 'C' else int(gcs_data['eyes'])
        verbal = 1 if gcs_data['verbal'] == 'T' else int(gcs_data['verbal'])
        motor = int(gcs_data['motor'])

        return {'score': eyes+verbal+motor}

    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for gcs in self.browse(cr, uid, ids, context):
            res[gcs.id] = self.calculate_score({'eyes': gcs.eyes, 'verbal': gcs.verbal, 'motor': gcs.motor})
            _logger.debug("Observation GCS activity_id=%s gcs_id=%s score: %s" % (gcs.activity_id.id, gcs.id, res[gcs.id]))
        return res

    _columns = {
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store={
                       'nh.clinical.patient.observation.gcs': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
        }),
        'eyes': fields.selection(_eyes, 'Eyes'),
        'verbal': fields.selection(_verbal, 'Verbal'),
        'motor': fields.selection(_motor, 'Motor')
    }

    _defaults = {
        'frequency': 60
    }

    _form_description = [
        {
            'name': 'meta',
            'type': 'meta',
            'score': True
        },
        {
            'name': 'eyes',
            'type': 'selection',
            'label': 'Eyes',
            'selection': _eyes,
            'initially_hidden': False
        },
        {
            'name': 'verbal',
            'type': 'selection',
            'label': 'Verbal',
            'selection': _verbal,
            'initially_hidden': False
        },
        {
            'name': 'motor',
            'type': 'selection',
            'label': 'Motor',
            'selection': _motor,
            'initially_hidden': False
        }
    ]

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default GCS policy
        """
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False

        # TRIGGER NOTIFICATIONS
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._POLICY['notifications'][case],
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)

        return super(nh_clinical_patient_observation_gcs, self).complete(cr, SUPERUSER_ID, activity_id, context)

    def create_activity(self, cr, uid, vals_activity={}, vals_data={}, context=None):
        assert vals_data.get('patient_id'), "patient_id is a required field!"
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id','=',vals_data['patient_id']],['data_model','=',self._name],['state','in',['new','started','scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain)
        except_if(len(ids),
                  msg="Having more than one activity of type '%s' is restricted. Terminate activities with ids=%s first"
                  % (self._name, str(ids)))
        res = super(nh_clinical_patient_observation_gcs, self).create_activity(cr, uid, vals_activity, vals_data, context)
        return res