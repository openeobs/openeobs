# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`stools.py` defines the bristol stool scale observation class and its
standard behaviour and policy triggers. There are currently no standard
scalation policies defined.
"""
from openerp.osv import orm, fields
import logging

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_stools(orm.Model):
    """
    Represents a Bristol Stool Scale
    :class:`observation<observations.nh_clinical_patient_observation>`,
    which is used as a useful research tool to evaluate the
    effectiveness of treatments for various diseases of the bowel.
    """
    _name = 'nh.clinical.patient.observation.stools'
    _inherit = ['nh.clinical.patient.observation']
    _required = []
    _description = "Bristol Stool Scale Observation"
    _boolean_selection = [[True, 'Yes'], [False, 'No']]
    _quantity_selection = [['large', 'Large'], ['medium', 'Medium'], ['small', 'Small']]
    _colour_selection = [['brown', 'Brown'], ['yellow', 'Yellow'], ['green', 'Green'], ['black', 'Black/Tarry'],
                         ['red', 'Red (fresh blood)'], ['clay', 'Clay']]
    _bristol_selection = [['1', 'Type 1'], ['2', 'Type 2'], ['3', 'Type 3'], ['4', 'Type 4'], ['5', 'Type 5'],
                          ['6', 'Type 6'], ['7', 'Type 7']]
    _samples_selection = [['none', 'None'], ['micro', 'Micro'], ['virol', 'Virol'], ['m+v', 'M+V']]
    _columns = {
        'bowel_open': fields.boolean('Bowel Open'),
        'nausea': fields.boolean('Nausea'),
        'vomiting': fields.boolean('Vomiting'),
        'quantity': fields.selection(_quantity_selection, 'Quantity'),
        'colour': fields.selection(_colour_selection, 'Colour'),
        'bristol_type': fields.selection(_bristol_selection, 'Bristol Type'),
        'offensive': fields.boolean('Offensive'),
        'strain': fields.boolean('Strain'),
        'laxatives': fields.boolean('Laxatives'),
        'samples': fields.selection(_samples_selection, 'Lab Samples'),
        'rectal_exam': fields.boolean('Rectal Exam'),
    }
    _form_description = [
        {
            'name': 'bowel_open',
            'type': 'selection',
            'label': 'Bowel Open',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'nausea',
            'type': 'selection',
            'label': 'Nausea',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'vomiting',
            'type': 'selection',
            'label': 'Vomiting',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'quantity',
            'type': 'selection',
            'label': 'Quantity',
            'selection': _quantity_selection,
            'initially_hidden': False
        },
        {
            'name': 'colour',
            'type': 'selection',
            'label': 'Colour',
            'selection': _colour_selection,
            'initially_hidden': False
        },
        {
            'name': 'bristol_type',
            'type': 'selection',
            'label': 'Bristol Type',
            'selection': _bristol_selection,
            'initially_hidden': False
        },
        {
            'name': 'offensive',
            'type': 'selection',
            'label': 'Offensive',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'strain',
            'type': 'selection',
            'label': 'Strain',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'laxatives',
            'type': 'selection',
            'label': 'Laxatives',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'samples',
            'type': 'selection',
            'label': 'Lab Samples',
            'selection': _samples_selection,
            'initially_hidden': False
        },
        {
            'name': 'rectal_exam',
            'type': 'selection',
            'label': 'Rectal Exam',
            'selection': _boolean_selection,
            'initially_hidden': False
        }
    ]
