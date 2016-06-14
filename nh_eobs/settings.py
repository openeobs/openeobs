from openerp.osv import osv, orm, fields
from . import sql_statements as nh_eobs_sql


class NHEobsSettings(orm.Model):
    _name = 'nh.clinical.settings'
    _columns = {
        'discharge_transfer_period': fields.integer(
            string='Days to keep patients in '
                   'Discharge/Transfer lists'),
        'workload_bucket_period': fields.integer(
            string='Time (in minutes) between buckets in Workload view'),
        'activity_period': fields.integer(
            string='Time (in minutes) to show user activities in')
    }
    _defaults = {
        'discharge_transfer_period': 3,
        'workload_bucket_period': 15,
        'activity_period': 60
    }

    def get_settings(self, cr, uid, settings):
        if not isinstance(settings, list):
            settings = [settings]
        vals = self.browse(cr, uid, [])
        if not vals.ids:
            self.create(cr, uid, {})
        get_vals = self.read(cr, uid, 1, settings)
        return get_vals

    def get_setting(self, cr, uid, setting):
        if isinstance(setting, list):
            setting = setting[0]
        return self.get_settings(cr, uid, setting).get(setting)


class NHEobsConfigSettings(osv.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'nh.clinical.config.settings'
    _columns = {
        'discharge_transfer_period': fields.integer(),
        'workload_bucket_period': fields.integer(),
        'activity_period': fields.integer()
    }

    @staticmethod
    def refresh_discharge_transfer_views(cr, interval):
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

    def set_discharge_transfer_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids)
        settings_pool.write(cr, uid, 1, {
            'discharge_transfer_period': wizard.discharge_transfer_period
        })
        return self.refresh_discharge_transfer_views(
            cr, wizard.discharge_transfer_period)

    def set_workload_bucket_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids)
        return settings_pool.write(cr, uid, 1, {
            'workload_bucket_period': wizard.workload_bucket_period
        })

    def set_activity_period(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        wizard = self.browse(cr, uid, ids)
        return settings_pool.write(cr, uid, 1, {
            'activity_period': wizard.activity_period
        })

    def get_default_all(self, cr, uid, ids, context=None):
        settings_pool = self.pool.get('nh.clinical.settings')
        get_vals = settings_pool.read(cr, uid, 1)
        if not get_vals:
            settings_pool.create(cr, uid, {})
            get_vals = settings_pool.read(cr, uid, 1)
        return {
            'discharge_transfer_period':
                get_vals.get('discharge_transfer_period'),
            'workload_bucket_period': get_vals.get('workload_bucket_period'),
            'activity_period': get_vals.get('activity_period')
        }
