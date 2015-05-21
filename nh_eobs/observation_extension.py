from openerp.osv import orm

class nh_clinical_patient_observation_ews_refresh(orm.Model):

    _name = 'nh.clinical.patient.observation.ews'
    _inherit = 'nh.clinical.patient.observation.ews'

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_patient_observation_ews_refresh, self).complete(cr, uid, activity_id, context=context)
        sql = """
                refresh materialized view ews0;
                refresh materialized view ews1;
                refresh materialized view ews2;
        """
        cr.execute(sql)
        return res



