from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)


class t4_clinical_overdue(orm.Model):
    _name = "t4.clinical.overdue"
    _inherits = {'t4.activity': 'activity_id'}
    _description = "Overdue Activities View"
    _auto = False
    _table = "t4_clinical_overdue"
    _states = [('new', 'new'), ('planned', 'Planned'), ('scheduled', 'Scheduled'),
               ('started', 'Started'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
               ('suspended', 'Suspended'), ('aborted', 'Aborted'), ('expired', 'Expired')]
    _columns = {
        'activity_id': fields.many2one('t4.activity', 'Activity', required=1, ondelete='restrict'),
        'name': fields.char('Activity Name', size=100),
        'delay': fields.integer('Delay'),
        'location': fields.char('Location', size=100),
        'parent_location': fields.char('Parent Location', size=100),
        'patient_name': fields.char('Patient Name', size=100),
        'nhs_number': fields.char('NHS Number', size=100),
        'user_name': fields.char('User Name', size=100),
        'state': fields.selection(_states, 'State')
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        activity.id as id,
                        case
                            when activity.data_model != 't4.clinical.patient.placement'
                            then spell.id
                            else activity.id
                        end as activity_id,
                        activity.summary as name,
                        location.name as location,
                        parent_location.name as parent_location,
                        coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as patient_name,
                        patient.patient_identifier as nhs_number,
                        partner.name as user_name,
                        activity.state as state,
                        now() at time zone 'UTC',
                        now() at time zone 'UTC' > activity.date_scheduled,
                        case
                            when activity.date_scheduled is not null and now() at time zone 'UTC' > activity.date_scheduled
                            then (extract(epoch from (now() at time zone 'UTC' - activity.date_scheduled))/60)::int
                            when activity.date_deadline is not null and now() at time zone 'UTC' > activity.date_deadline
                            then (extract(epoch from (now() at time zone 'UTC' - activity.date_deadline))/60)::int
                            else 0
                        end  as delay
                    from t4_activity activity
                    inner join t4_clinical_patient patient on activity.patient_id = patient.id
                    inner join t4_clinical_location location on activity.location_id = location.id
                    inner join t4_clinical_location parent_location on location.parent_id = parent_location.id
                    left join res_users u on activity.user_id = u.id
                    left join res_partner partner on u.partner_id = partner.id
                    left join t4_activity spell on spell.data_model = 't4.clinical.spell' and spell.patient_id = activity.patient_id
                    where activity.state not in ('completed','cancelled') and activity.data_model != 't4.clinical.spell'
                    order by delay
                )
        """ % (self._table, self._table))