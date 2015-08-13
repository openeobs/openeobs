from openerp.osv import orm, osv
import logging
import threading
from datetime import datetime as dt
from openerp.api import Environment
from openerp import registry
_logger = logging.getLogger(__name__)


def refresh_materialized_views(f):
    def wrapper(*args, **kwargs):
        self, cr, uid, views = args[:4]
        if not isinstance(views, list):
            raise osv.except_osv('Type Error!', "views must be a list, found to be %s" % type(views))
        for v in views:
            if not isinstance(v, str):
                raise osv.except_osv('Type Error!', "view name must be a string, found to be %s" % type(v))
        _logger.debug('Refreshing materialized views...')
        start = dt.now()
        sql = ''
        for v in views:
            sql += 'refresh materialized view '+v+';\n'
        with Environment.manage():
            with registry(cr.dbname).cursor() as new_cr:
                new_cr.execute(sql)
                new_cr.commit()
        end = dt.now()
        delta = end-start
        milliseconds = int(delta.total_seconds() * 1000)
        _logger.debug('Materialized views refreshed in %s milliseconds' % milliseconds)
        return f(*args, **kwargs)
    return wrapper



class nh_clinical_patient_observation_ews(orm.Model):

    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_observation_ews, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['ews0', 'ews1', 'ews2'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_placement(orm.Model):

    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_placement, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['placement'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_mrsa(orm.Model):

    _name = 'nh.clinical.patient.mrsa'
    _inherit = 'nh.clinical.patient.mrsa'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_mrsa, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_diabetes(orm.Model):

    _name = 'nh.clinical.patient.diabetes'
    _inherit = 'nh.clinical.patient.diabetes'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_diabetes, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_palliative_care(orm.Model):

    _name = 'nh.clinical.patient.palliative_care'
    _inherit = 'nh.clinical.patient.palliative_care'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_palliative_care, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_post_surgery(orm.Model):

    _name = 'nh.clinical.patient.post_surgery'
    _inherit = 'nh.clinical.patient.post_surgery'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_post_surgery, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_critical_care(orm.Model):

    _name = 'nh.clinical.patient.critical_care'
    _inherit = 'nh.clinical.patient.critical_care'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_critical_care, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_weight_monitoring(orm.Model):

    _name = 'nh.clinical.patient.weight_monitoring'
    _inherit = 'nh.clinical.patient.weight_monitoring'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_weight_monitoring, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_urine_output_target(orm.Model):

    _name = 'nh.clinical.patient.uotarget'
    _inherit = 'nh.clinical.patient.uotarget'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_urine_output_target, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_observation_height(orm.Model):

    _name = 'nh.clinical.patient.observation.height'
    _inherit = 'nh.clinical.patient.observation.height'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_observation_height, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_pbp_monitoring(orm.Model):

    _name = 'nh.clinical.patient.pbp_monitoring'
    _inherit = 'nh.clinical.patient.pbp_monitoring'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_pbp_monitoring, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_patient_o2target(orm.Model):

    _name = 'nh.clinical.patient.o2target'
    _inherit = 'nh.clinical.patient.o2target'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_o2target, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res


class nh_clinical_o2level(orm.Model):

    _name = 'nh.clinical.o2level'
    _inherit = 'nh.clinical.o2level'

    @refresh_materialized_views
    def refresh_views(self, cr, uid, views, context=None):
        return True

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_o2level, self).complete(cr, uid, activity_id, context=context)
        thr = threading.Thread(target=self.refresh_views, args=[cr, uid, ['param'], context], kwargs=None)
        thr.start()
        return res
