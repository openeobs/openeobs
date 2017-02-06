from openerp.osv import orm, fields
from openerp import api
import copy


class FoodAndFluid(orm.Model):

    _name = 'nh.clinical.patient.observation.food_fluid'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['passed_urine', 'bowels_open']
    _description = 'Food and Fluid Observation'

    _passed_urine_options = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unknown', 'Unknown')
    ]

    _bowels_open_options = [
        ('no', 'No'),
        ('unknown', 'Unknown'),
        ('type_1', 'Type 1'),
        ('type_2', 'Type 2'),
        ('type_3', 'Type 3'),
        ('type_4', 'Type 4'),
        ('type_5', 'Type 5'),
        ('type_6', 'Type 6'),
        ('type_7', 'Type 7')
    ]

    _columns = {
        'recorded_concerns': fields.many2one(
            'nh.clinical.recorded_concern',
            'Recorded Concern'),
        'dietary_needs': fields.many2one(
            'nh.clinical.dietary_need',
            'Consider Special Dietary Needs'),
        'food_fluid_period': fields.many2one(
            'nh.clinical.patient.observation.food_fluid.period',
            'Period for Food and Fluid Observations'
        ),
        'fluid_taken': fields.integer('Fluid Taken (ml) - Include IV / NG'),
        'fluid_description': fields.text('Fluid Description'),
        'food_taken': fields.text('Food Taken'),
        'food_fluid_rejected': fields.text(
            'Food and Fluid Offered but Rejected'),
        'passed_urine': fields.selection(
            _passed_urine_options, 'Passed Urine'),
        'bowels_open': fields.selection(_bowels_open_options, 'Bowels Open')
    }

    @api.model
    def get_form_description(self, patient_id):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui to submit this
        observation.

        Adds the lists of recorded concerns and dietary needs to the
        form description as these are stored in separate models to allow
        for multi select

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        form_desc = copy.deepcopy(self._form_description)
        recorded_concern_model = self.env['nh.clinical.recorded_concern']
        dietary_need_model = self.env['nh.clinical.dietary_need']
        recorded_concerns = recorded_concern_model.search([])
        dietary_needs = dietary_need_model.search([])
        form_desc[0]['selection'] = \
            [(rec.id, rec.name) for rec in recorded_concerns]
        form_desc[1]['selection'] = \
            [(rec.id, rec.name) for rec in dietary_needs]
        return form_desc

    _form_description = [
        {
            'name': 'recorded_concerns',
            'type': 'multiselect',
            'label': 'Recorded Concerns',
            'selection': [],
            'initially_hidden': False
        },
        {
            'name': 'dietary_needs',
            'type': 'multiselect',
            'label': 'Consider Special Dietary Needs',
            'selection': [],
            'initially_hidden': False
        },
        {
            'name': 'fluid_taken',
            'type': 'integer',
            'min': 0,
            'max': 5000,
            'label': 'Fluid Taken (ml) - Include IV / NG',
            'initially_hidden': False
        },
        {
            'name': 'fluid_description',
            'type': 'text',
            'label': 'Fluid Description',
            'initially_hidden': False
        },
        {
            'name': 'food_taken',
            'type': 'text',
            'label': 'Food Taken',
            'initially_hidden': False
        },
        {
            'name': 'food_fluid_rejected',
            'type': 'text',
            'label': 'Food and Fluid Offered but Rejected',
            'initially_hidden': False
        },
        {
            'name': 'passed_urine',
            'type': 'selection',
            'label': 'Passed Urine',
            'selection': _passed_urine_options,
            'initially_hidden': False
        },
        {
            'name': 'bowels_open',
            'type': 'selection',
            'label': 'Bowels Open',
            'selection': _bowels_open_options,
            'initially_hidden': False
        }
    ]
