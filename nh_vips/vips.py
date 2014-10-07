# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
import logging
import bisect
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_vips(orm.Model):
    _name = 'nh.clinical.patient.observation.vips'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['pain', 'redness', 'swelling', 'cord', 'pyrexia']
    _description = "VIPS Observation"
    _selection = [('no', 'No'), ('yes', 'Yes')]

    """
    Default VIPS policy has 4 different scenarios:
        case 0: No phlebitis
        case 1: Early stage of plebitis --> Resite cannula
        case 2: Advanced stage of plebitis --> Consider plebitis treatment
        case 3: Advanced stage of thrombophlebitis --> Initiate phlebitis treatment
    """
    _POLICY = {'ranges': [1, 2, 4], 'case': '0123', 'frequencies': [1440, 1440, 1440, 1440],
               'notifications': [
                   [],
                   [{'model': 'nurse', 'summary': 'Resite Cannula', 'groups': ['nurse', 'hca']}],
                   [{'model': 'nurse', 'summary': 'Resite Cannula', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Consider plebitis treatment', 'groups': ['nurse', 'hca']}],
                   [{'model': 'nurse', 'summary': 'Resite Cannula', 'groups': ['nurse', 'hca']},
                    {'model': 'nurse', 'summary': 'Initiate plebitis treatment', 'groups': ['nurse', 'hca']}]
               ]}

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
                       'nh.clinical.patient.observation.vips': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
        }),
        'pain': fields.selection(_selection, 'Pain'),
        'redness': fields.selection(_selection, 'Redness'),
        'swelling': fields.selection(_selection, 'Swelling'),
        'cord': fields.selection(_selection, 'Palpable venous cord'),
        'pyrexia': fields.selection(_selection, 'Pyrexia'),
    }

    _defaults = {
        'frequency': 1440
    }

    _form_description = [
        {
            'name': 'pain',
            'type': 'selection',
            'label': 'Pain',
            'selection': _selection,
            'initially_hidden': False
        },
        {
            'name': 'redness',
            'type': 'selection',
            'label': 'Redness',
            'selection': _selection,
            'initially_hidden': False
        },
        {
            'name': 'swelling',
            'type': 'selection',
            'label': 'Swelling',
            'selection': _selection,
            'initially_hidden': False
        },
        {
            'name': 'cord',
            'type': 'selection',
            'label': 'Palpable venous cord',
            'selection': _selection,
            'initially_hidden': False
        },
        {
            'name': 'pyrexia',
            'type': 'selection',
            'label': 'Pyrexia',
            'selection': _selection,
            'initially_hidden': False
        }
    ]

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default VIPS policy
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

        res = super(nh_clinical_patient_observation_vips, self).complete(cr, SUPERUSER_ID, activity_id, context)

        # create next VIPS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID,
                             {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                             {'patient_id': activity.data_ref.patient_id.id})
        api_pool.change_activity_frequency(cr, SUPERUSER_ID,
                                           activity.data_ref.patient_id.id,
                                           self._name,
                                           self._POLICY['frequencies'][case], context=context)
        return res

    def create_activity(self, cr, uid, vals_activity={}, vals_data={}, context=None):
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id','=',vals_data['patient_id']],['data_model','=',self._name],['state','in',['new','started','scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain)
        except_if(len(ids),
                  msg="Having more than one activity of type '%s' is restricted. Terminate activities with ids=%s first"
                  % (self._name, str(ids)))
        res = super(nh_clinical_patient_observation_vips, self).create_activity(cr, uid, vals_activity, vals_data, context)
        return res