from openerp.osv import orm


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    def toggle_obs_stop(self, cr, uid, ids, context=None):
        pass
