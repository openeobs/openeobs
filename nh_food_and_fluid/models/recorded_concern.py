from openerp.osv import orm, fields


class FoodAndFluidRecordedConcern(orm.Model):

    _name = 'nh.clinical.recorded_concern'
    _required = ['name']
    _description = 'Recorded Concern'

    _columns = {
        'name': fields.text('Name')
    }
