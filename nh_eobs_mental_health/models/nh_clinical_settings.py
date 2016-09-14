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
        'activity_period': 360,
        'manually_set': False
    }

    def init(self, cr, context=None):
        """ Change the existing settings to the new defaults """
        workload_pool = self.pool.get('nh.clinical.settings.workload')
        config_pool = self.pool.get('nh.clinical.config.settings')
        existing_rec = self.read(cr, 1, 1, context=context)
        mental_health_buckets = workload_pool.search(cr, 1, [
            ['name', 'in', [
                '361+ minutes remain',
                '241-360 minutes remain',
                '121-240 minutes remain',
                '0-120 minutes remain',
                '1-120 minutes late',
                '121+ minutes late'
            ]]])
        defaults = self._defaults
        bucket_objs = workload_pool.read(cr, 1, mental_health_buckets)
        defaults['workload_bucket_period'] = [[6, 0, mental_health_buckets]]
        if existing_rec:
            if not existing_rec.get('manually_set'):
                self.write(cr, 1, 1, defaults, context=context)
                config_pool.refresh_workload_view(
                    cr, bucket_objs, context=context)
        else:
            self.create(cr, 1, defaults, context=context)
            config_pool.refresh_workload_view(
                cr, bucket_objs, context=context)


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
        workload_pool = self.pool.get('nh.clinical.settings.workload')
        wizard = self.read(cr, uid, ids, context=context)[0]
        bucket_objs = workload_pool.read(cr, uid,
                                         wizard.get('workload_bucket_period'),
                                         context=context)
        buckets = [bucket.get('name') for bucket in bucket_objs]
        validation = settings_pool.validate_workload_buckets(buckets,
                                                             context=context)
        if isinstance(validation, str):
            raise ValueError(validation)
        settings_pool.write(cr, uid, 1, {
            'manually_set': True,
            'workload_bucket_period': [
                [6, 0, wizard.get('workload_bucket_period')]
            ]}, context=context)
        return self.refresh_workload_view(cr, bucket_objs, context=context)

    def set_activity_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        return settings_pool.write(cr, uid, 1, {
            'activity_period': wizard.activity_period,
            'manually_set': True
        }, context=context)
