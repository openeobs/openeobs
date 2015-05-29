from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_urinary_analysis(orm.Model):
    _name = 'nh.clinical.patient.observation.urinary_analysis'
    _inherit = ['nh.clinical.patient.observation']
    _required = []
    _description = "Urinary Analysis Observation"
    _num_fields = ['ph', 'blood', 'protein', 'glucose', 'ketones', 'nitrates', 'leucocytes']
    _columns = {
        'ph': fields.float('pH', digits=(2, 1)),
        'blood': fields.integer('Blood (micrograms/L)'),
        'protein': fields.float('Protein (g/L)', digits=(1, 2)),
        'glucose': fields.integer('Glucose (mmol/L)'),
        'ketones': fields.float('Ketones (mmol/L)', digits=(2, 1)),
        'nitrates': fields.integer('Nitrates (micromol/L)'),
        'leucocytes': fields.integer('Leucocytes (cells/hpf)'),
    }
    _form_description = [
        {
            'name': 'ph',
            'type': 'float',
            'label': 'pH',
            'digits': [2, 1],
            'min': 1.0,
            'max': 14.0,
            'initially_hidden': False
        },
        {
            'name': 'blood',
            'type': 'integer',
            'label': 'Blood (micrograms/L)',
            'min': 0,
            'max': 1000,
            'initially_hidden': False
        },
        {
            'name': 'protein',
            'type': 'float',
            'label': 'Protein (g/L)',
            'digits': [1, 2],
            'min': 0.0,
            'max': 1.0,
            'initially_hidden': False
        },
        {
            'name': 'glucose',
            'type': 'integer',
            'label': 'Glucose (mmol/L)',
            'min': 0,
            'max': 100,
            'initially_hidden': False
        },
        {
            'name': 'ketones',
            'type': 'float',
            'label': 'Ketones (mmol/L)',
            'digits': [2, 1],
            'min': 0.0,
            'max': 10.0,
            'initially_hidden': False
        },
        {
            'name': 'nitrates',
            'type': 'integer',
            'label': 'Nitrates (micromol/L)',
            'min': 0,
            'max': 100,
            'initially_hidden': False
        },
        {
            'name': 'leucocytes',
            'type': 'integer',
            'label': 'Leucocytes (cells/hpf)',
            'min': 0,
            'max': 100,
            'initially_hidden': False
        }
    ]
