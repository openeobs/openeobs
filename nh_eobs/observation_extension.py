# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.osv import orm
from openerp.addons.nh_eobs.helpers import refresh_materialized_views


class nh_clinical_patient_observation_ews(orm.Model):
    _inherit = 'nh.clinical.patient.observation.ews'

    @refresh_materialized_views('ews0', 'ews1', 'ews2')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_ews, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_o2target(orm.Model):
    _inherit = 'nh.clinical.patient.o2target'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_o2target, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_notification_frequency(orm.Model):
    _inherit = 'nh.clinical.notification.frequency'

    @refresh_materialized_views('ews0', 'ews1', 'ews2')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_notification_frequency, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_observation_height(orm.Model):
    _inherit = 'nh.clinical.patient.observation.height'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_height, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_observation_blood_product(orm.Model):
    _inherit = 'nh.clinical.patient.observation.blood_product'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_blood_product, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_observation_pain(orm.Model):
    _inherit = 'nh.clinical.patient.observation.pain'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_pain, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_observation_urine_output(orm.Model):
    _inherit = 'nh.clinical.patient.observation.urine_output'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_urine_output, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_observation_bowels_open(orm.Model):
    _inherit = 'nh.clinical.patient.observation.bowels_open'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_observation_bowels_open, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_mrsa(orm.Model):
    _inherit = 'nh.clinical.patient.mrsa'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_mrsa, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_diabetes(orm.Model):
    _inherit = 'nh.clinical.patient.diabetes'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_diabetes, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_palliative_care(orm.Model):
    _inherit = 'nh.clinical.patient.palliative_care'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_palliative_care, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_post_surgery(orm.Model):
    _inherit = 'nh.clinical.patient.post_surgery'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_post_surgery, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_critical_care(orm.Model):
    _inherit = 'nh.clinical.patient.critical_care'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_critical_care, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_urine_output_target(orm.Model):
    _inherit = 'nh.clinical.patient.uotarget'

    @refresh_materialized_views('param')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_urine_output_target, self).complete(
            cr, uid, activity_id, context)


class nh_clinical_patient_pbp_monitoring(orm.Model):
    _inherit = 'nh.clinical.patient.pbp_monitoring'

    @refresh_materialized_views('pbp')
    def complete(self, cr, uid, activity_id, context=None):
        return super(
            nh_clinical_patient_pbp_monitoring, self).complete(
            cr, uid, activity_id, context)
