from openerp.osv import orm


class nh_clinical_overdue(orm.Model):
    """
    Extends :class:`activity<activity.nh_activity>` to create
    overdue activities used by view overdue_view.xml
    Includes fields ``delay_string`` to record time
    overdue and ``user_name`` to record user the activity is assigned
    to.
    """

    _name = "nh.clinical.overdue"
    _inherit = "nh.clinical.overdue"

    def init(self, cr):
        # TODO: EOBS-695: Refactor Overdue Tasks to use groups that can access
        # activity instead of looking at activity data model
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                with activity as (
                    select
                        activity.id as id,
                        case
                            when activity.data_model !=
                                'nh.clinical.patient.placement'
                            then spell.id
                            else activity.id
                        end as activity_id,
                        activity.summary as name,
                        location.name as location,
                        parent_location.name as parent_location,
                        coalesce(patient.family_name, '') || ',
                            ' || coalesce(patient.given_name, '')
                            || ' ' || coalesce(patient.middle_names,'')
                            as patient_name,
                        patient.patient_identifier as nhs_number,
                        partner.name as user_name,
                        activity.state as state,
                        now() at time zone 'UTC' - coalesce(
                            activity.date_scheduled,activity.date_deadline)
                            as delay_interval,
                        case
                            when strpos(activity.data_model, 'hca') != 0
                                then 'HCA'
                            when strpos(activity.data_model, 'doctor') != 0
                                then 'Doctor'
                            when activity.data_model =
                                'nh.clinical.notification.clinical_review'
                                then 'Doctor'
                            when activity.data_model =
                                'nh.clinical.notification'
                                '.clinical_review_frequency'
                                then 'Nurse, Doctor'
                            when strpos(activity.data_model, 'notification')
                                != 0 then 'Nurse'
                            when strpos(activity.data_model, 'observation')
                                != 0 then 'HCA, Nurse'
                            else 'Shift Coordinator'
                        end as groups
                    from nh_activity activity
                    inner join nh_clinical_patient patient
                        on activity.patient_id = patient.id
                    inner join nh_clinical_location location
                        on activity.location_id = location.id
                    inner join nh_clinical_location parent_location
                        on location.parent_id = parent_location.id
                    left join res_users u on activity.user_id = u.id
                    left join res_partner partner on u.partner_id = partner.id
                    left join nh_activity spell
                        on spell.data_model = 'nh.clinical.spell'
                        and spell.patient_id = activity.patient_id
                    where activity.state not in ('completed','cancelled')
                    and activity.data_model != 'nh.clinical.spell'
                    and spell.state = 'started'
                    )
                    select
                        id,
                        activity_id,
                        name,
                        location,
                        parent_location,
                        patient_name,
                        nhs_number,
                        user_name,
                        state,
                        case when extract(epoch from delay_interval) > 0 then
                            case when extract(days from delay_interval) > 0
                                then  extract(days from delay_interval)
                                || ' day(s) ' else ''
                            end || to_char(delay_interval, 'HH24:MI')
                        else '' end as delay_string,
                        case when extract(epoch from delay_interval) > 0
                            then(extract(epoch from delay_interval)/60)::int
                        else 0 end as delay,
                        groups
                    from activity
                    order by delay
                )
        """ % (self._table, self._table))
