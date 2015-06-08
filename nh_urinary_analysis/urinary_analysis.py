from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_urinary_analysis(orm.Model):
    _name = 'nh.clinical.patient.observation.urinary_analysis'
    _inherit = ['nh.clinical.patient.observation']
    _required = []
    _description = "Urinary Analysis Observation"
    _num_fields = ['ph']
    _values = [['neg', 'NEG'], ['trace', 'TRACE'], ['1', '+'], ['2', '++'], ['3', '+++']]
    _columns = {
        'ph': fields.float('pH', digits=(2, 1)),
        'blood': fields.selection(_values, 'Blood'),
        'protein': fields.selection(_values, 'Protein'),
        'glucose': fields.selection(_values, 'Glucose'),
        'ketones': fields.selection(_values, 'Ketones'),
        'nitrates': fields.selection(_values, 'Nitrates'),
        'leucocytes': fields.selection(_values, 'Leucocytes'),
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
            'label': 'Blood',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        },
        {
            'name': 'protein',
            'label': 'Protein',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        },
        {
            'name': 'glucose',
            'label': 'Glucose',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        },
        {
            'name': 'ketones',
            'label': 'Ketones',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        },
        {
            'name': 'nitrates',
            'label': 'Nitrates',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        },
        {
            'name': 'leucocytes',
            'label': 'Leucocytes',
            'type': 'selection',
            'selection': _values,
            'initially_hidden': False
        }
    ]
