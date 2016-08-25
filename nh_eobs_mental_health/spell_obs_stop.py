from openerp.osv import orm, fields


class NHClinicalSpellObsStop(orm.Model):

    _name = 'nh.clinical.spell'
    _inherit = 'nh.clinical.spell'

    _columns = {
        'obs_stop': fields.boolean('Stop Observations for patient?')
    }

    _defaults = {
        'obs_stop': False
    }
