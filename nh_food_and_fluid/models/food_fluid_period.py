from openerp.osv import orm, fields


class FoodAndFluidPeriod(orm.Model):

    _name = 'nh.clinical.patient.observation.food_fluid.period'
    _description = 'Period of Food & Fluid Observations'

    def _is_period_currently_active(self):
        return False

    _columns = {
        'start_date': fields.datetime(
            'Start of Food and Fluid Period', required=True),
        'end_date': fields.datetime(
            'End of Food and Fluid Period', required=True),
        'currently_active': fields.function(
            _is_period_currently_active)
    }
