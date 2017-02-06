from openerp.osv import orm, fields


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
            'Consider Special Dietary Need'),
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
