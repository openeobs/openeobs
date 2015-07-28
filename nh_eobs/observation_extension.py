from openerp.osv import orm
from openerp.sql_db import TestCursor


class nh_clinical_patient_observation_ews(orm.Model):

    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_observation_ews, self).complete(cr, uid, activity_id, context=context)
        if not isinstance(cr, TestCursor):
            sql = """
                    refresh materialized view ews0;
                    refresh materialized view ews1;
                    refresh materialized view ews2;
            """
            cr.execute(sql)
        return res


class nh_clinical_patient_placement(orm.Model):

    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_placement, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view placement""")
        return res


class nh_clinical_patient_mrsa(orm.Model):

    _name = 'nh.clinical.patient.mrsa'
    _inherit = 'nh.clinical.patient.mrsa'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_mrsa, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_diabetes(orm.Model):

    _name = 'nh.clinical.patient.diabetes'
    _inherit = 'nh.clinical.patient.diabetes'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_diabetes, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_palliative_care(orm.Model):

    _name = 'nh.clinical.patient.palliative_care'
    _inherit = 'nh.clinical.patient.palliative_care'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_palliative_care, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_post_surgery(orm.Model):

    _name = 'nh.clinical.patient.post_surgery'
    _inherit = 'nh.clinical.patient.post_surgery'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_post_surgery, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_critical_care(orm.Model):

    _name = 'nh.clinical.patient.critical_care'
    _inherit = 'nh.clinical.patient.critical_care'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_critical_care, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_weight_monitoring(orm.Model):

    _name = 'nh.clinical.patient.weight_monitoring'
    _inherit = 'nh.clinical.patient.weight_monitoring'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_weight_monitoring, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_urine_output_target(orm.Model):

    _name = 'nh.clinical.patient.uotarget'
    _inherit = 'nh.clinical.patient.uotarget'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_urine_output_target, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_observation_height(orm.Model):

    _name = 'nh.clinical.patient.observation.height'
    _inherit = 'nh.clinical.patient.observation.height'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_observation_height, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_pbp_monitoring(orm.Model):

    _name = 'nh.clinical.patient.pbp_monitoring'
    _inherit = 'nh.clinical.patient.pbp_monitoring'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_pbp_monitoring, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_patient_o2target(orm.Model):

    _name = 'nh.clinical.patient.o2target'
    _inherit = 'nh.clinical.patient.o2target'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_o2target, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res


class nh_clinical_o2level(orm.Model):

    _name = 'nh.clinical.o2level'
    _inherit = 'nh.clinical.o2level'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_o2level, self).complete(cr, uid, activity_id, context=context)
        cr.execute("""refresh materialized view param""")
        return res
