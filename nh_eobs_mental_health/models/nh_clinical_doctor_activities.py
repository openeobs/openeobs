from openerp.osv import orm


class NHClinicalDoctorActivities(orm.Model):
    """
    Extends nh_clinical_doctor_activities to include new models for Doctor
    Tasks
    """

    _name = "nh.clinical.doctor_activities"
    _inherit = 'nh.clinical.doctor_activities'

    def init(self, cr):
        # TODO EOBS-682: Refactor Doctor Tasks SQL to show tasks assigned to
        # doctors on ward
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        activity.id as id,
                        spell.id as activity_id,
                        activity.summary as summary,
                        location.name || ' (' || parent_location.name || ')'
                            as location
                    from nh_activity activity
                    inner join nh_clinical_patient patient
                        on activity.patient_id = patient.id
                    inner join nh_clinical_location location
                        on activity.location_id = location.id
                    inner join nh_clinical_location parent_location
                        on location.parent_id = parent_location.id
                    left join nh_activity spell
                        on spell.data_model = 'nh.clinical.spell'
                        and spell.patient_id = activity.patient_id
                    where activity.state not in ('completed','cancelled')
                    and activity.data_model in
                        (
                          'nh.clinical.notification.doctor_assessment',
                          'nh.clinical.notification.clinical_review',
                          'nh.clinical.notification.clinical_review_frequency'
                        )
                    and spell.state = 'started'
                )
        """ % (self._table, self._table))
