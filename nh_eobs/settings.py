from openerp.osv import osv, orm, fields
import re


class NHEobsWorkloadBucket(orm.Model):

    _name = 'nh.clinical.settings.workload'

    _columns = {
        'name': fields.text(string='Name of the workload bucket'),
        'settings_id': fields.many2one('nh.clinical.settings',
                                       'workload_bucket_period'),
        'sequence': fields.integer(string='Sequence for order',
                                   default=1)
    }

    _order = 'sequence asc'


class NHEobsSettings(orm.Model):
    _name = 'nh.clinical.settings'

    WORKLOAD_BUCKET_REGEX = r'^\d+[-|+]{1}(\d+)?.+$'

    _columns = {
        'discharge_transfer_period': fields.integer(
            string='Days to keep patients in '
                   'Discharge/Transfer lists'),
        'workload_bucket_period': fields.one2many(
            'nh.clinical.settings.workload',
            'settings_id',
            string='Time (in minutes) between buckets in Workload view'),
        'activity_period': fields.integer(
            string='Time (in minutes) to show user activities in')
    }
    _defaults = {
        'discharge_transfer_period': 3,
        'activity_period': 60
    }

    def get_settings(self, cr, uid, settings, context=None):
        if not isinstance(settings, list):
            settings = [settings]
        vals = self.browse(cr, uid, [])
        if not vals.ids:
            self.create(cr, uid, {})
        get_vals = self.read(cr, uid, 1, settings)
        return get_vals

    def get_setting(self, cr, uid, setting, context=None):
        if isinstance(setting, list):
            setting = setting[0]
        return self.get_settings(cr, uid, setting).get(setting)

    def validate_workload_buckets(self, buckets, context=None):
        errors = []
        pattern = re.compile(self.WORKLOAD_BUCKET_REGEX)
        for bucket in buckets:
            match = pattern.match(bucket)
            if not match:
                errors.append(str(buckets.index(bucket) + 1))
        if errors:
            plural = 's' if len(errors) > 1 else ''
            is_are = 'are' if len(errors) > 1 else 'is'
            positions = ' and '.join(errors)
            message = 'Time period{plural} in position{plural} {positions} ' \
                      '{is_are} invalid'
            return message.format(plural=plural, is_are=is_are,
                                  positions=positions)
        else:
            return True


class NHEobsConfigSettings(osv.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'nh.clinical.config.settings'
    _columns = {
        'discharge_transfer_period': fields.integer(),
        'workload_bucket_period': fields.one2many(
            'nh.clinical.settings.workload', 'settings_id'),
        'activity_period': fields.integer()
    }

    def refresh_discharge_transfer_views(self, cr, interval, context=None):
        nh_eobs_sql = self.pool.get('nh.clinical.sql')
        discharge = \
            nh_eobs_sql.get_last_discharge_users('{0}d'.format(interval))
        transfer = \
            nh_eobs_sql.get_last_transfer_users('{0}d'.format(interval))
        wardboard = \
            nh_eobs_sql.get_wardboard('{0}d'.format(interval))
        return cr.execute(
            """
            create or replace view
            last_discharge_users as({last_discharge_users});
            create or replace view
            last_transfer_users as({last_transfer_users});
            create or replace view
            nh_clinical_wardboard as({wardboard});
            """.format(last_discharge_users=discharge,
                       last_transfer_users=transfer,
                       wardboard=wardboard)
        )

    def refresh_workload_view(self, cr, buckets, context=None):
        sql_pool = self.pool.get('nh.clinical.sql')
        view = sql_pool.get_workload(buckets)
        return cr.execute(
            'create or replace view '
            'nh_activity_workload as ({workload})'.format(
                table=self._table, workload=view))

    def set_discharge_transfer_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        settings_pool.write(cr, uid, 1, {
            'discharge_transfer_period': wizard.discharge_transfer_period
        }, context=context)
        return self.refresh_discharge_transfer_views(
            cr, wizard.discharge_transfer_period, context=context)

    def execute(self, cr, uid, id, context=None):
        self.set_workload_bucket_period(cr, uid, id, context=context)
        self.set_activity_period(cr, uid, id, context=context)
        self.set_discharge_transfer_period(cr, uid, id, context=context)
        return {
            'name': 'LiveObs Settings',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': 0,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'inline',
        }

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
        settings_pool.write(cr, uid, 1, {'workload_bucket_period': [
            [6, 0, wizard.get('workload_bucket_period')]]}, context=context)
        return self.refresh_workload_view(cr, bucket_objs, context=context)

    def set_activity_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids, context=context)
        return settings_pool.write(cr, uid, 1, {
            'activity_period': wizard.activity_period
        }, context=context)

    def get_default_all(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        get_vals = settings_pool.read(cr, uid, 1, context=context)
        if not get_vals:
            settings_pool.create(cr, uid, {}, context=context)
            get_vals = settings_pool.read(cr, uid, 1, context=context)
        return {
            'discharge_transfer_period':
                get_vals.get('discharge_transfer_period'),
            'workload_bucket_period': get_vals.get('workload_bucket_period'),
            'activity_period': get_vals.get('activity_period')
        }
