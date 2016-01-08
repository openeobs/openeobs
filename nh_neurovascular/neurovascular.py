"""
`neurovascular.py` defines the neurovascular observation class and its
standard behaviour and policy triggers. There is currently no standard
being followed by clinicians so the logic is quite generic.
"""
from openerp.osv import orm, fields
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_neurovascular(orm.Model):
    """
    Represents a Neurovascular
    :class:`observation<observations.nh_clinical_patient_observation>`
    for acute limb compartment syndrome detection.
    """
    _name = 'nh.clinical.patient.observation.neurovascular'
    _inherit = ['nh.clinical.patient.observation']
    _required = []
    _description = "Neurovascular Observation"
    _columns = {
        'limb': fields.selection([['la', 'Left Arm'], ['ra', 'Right Arm'], ['ll', 'Left Leg'], ['rl', 'Right Leg']], 'Limb'),
        'colour': fields.char('Colour', size=20),
        'warmth': fields.char('Warmth', size=20),
        'movement': fields.char('Movement', size=50),
        'sensation': fields.char('Sensation', size=50),
        'pulse': fields.char('Pulse', size=50)
    }
    _form_description = [
        {
            'name': 'limb',
            'type': 'selection',
            'label': 'Limb',
            'selection': [['la', 'Left Arm'], ['ra', 'Right Arm'], ['ll', 'Left Leg'], ['rl', 'Right Leg']],
            'initially_hidden': False
        },
        {
            'name': 'colour',
            'type': 'text',
            'label': 'Colour',
            'initially_hidden': False
        },
        {
            'name': 'warmth',
            'type': 'text',
            'label': 'Warmth',
            'initially_hidden': False
        },
        {
            'name': 'movement',
            'type': 'text',
            'label': 'Movement',
            'initially_hidden': False
        },
        {
            'name': 'sensation',
            'type': 'text',
            'label': 'Sensation',
            'initially_hidden': False
        },
        {
            'name': 'pulse',
            'type': 'text',
            'label': 'Pulse',
            'initially_hidden': False
        }
    ]
