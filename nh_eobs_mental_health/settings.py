from openerp.osv import orm, fields, osv


class NHEobsMentalHealthSettings(orm.Model):
    _name = 'nh.clinical.settings'
    _inherit = 'nh.clinical.settings'

    _columns = {
        'manually_set':
            fields.boolean(string='Have the settings been manually set')
    }
    _defaults = {
        'discharge_transfer_period': 10,
        'workload_bucket_period': 120,
        'activity_period': 360,
        'manually_set': False
    }

    def init(self, cr, context=None):
        """ Change the existing settings to the new defaults """
        existing_rec = self.read(cr, 1, 1, context=context)
        if existing_rec:
            if not existing_rec.get('manually_set'):
                self.write(cr, 1, 1, self._defaults, context=context)
        else:
            self.create(cr, 1, {}, context=context)


class NHEobsMentalHealthConfig(osv.TransientModel):
    _name = 'nh.clinical.config.settings'
    _inherit = 'nh.clinical.config.settings'

    def set_discharge_transfer_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        settings_pool.write(cr, uid, 1, {
            'discharge_transfer_period': wizard.discharge_transfer_period,
            'manually_set': True
        }, context=context)
        return self.refresh_discharge_transfer_views(
            cr, wizard.discharge_transfer_period)

    def set_workload_bucket_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        return settings_pool.write(cr, uid, 1, {
            'workload_bucket_period': wizard.workload_bucket_period,
            'manually_set': True
        }, context=context)

    def set_activity_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        return settings_pool.write(cr, uid, 1, {
            'activity_period': wizard.activity_period,
            'manually_set': True
        }, context=context)
