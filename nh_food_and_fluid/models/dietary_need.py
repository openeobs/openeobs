from openerp.osv import orm, fields


class FoodAndFluidDietaryNeed(orm.Model):

    _name = 'nh.clinical.dietary_need'
    _required = ['name']
    _description = 'Consider Special Dietary Needs'

    _columns = {
        'name': fields.text('Name')
    }