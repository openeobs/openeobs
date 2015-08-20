from openerp.osv import orm, fields, osv
import logging
_logger = logging.getLogger(__name__)


class nh_eobs_ward_dashboard(orm.Model):
    _name = "nh.eobs.ward.dashboard"
    _inherits = {'nh.clinical.location': 'location_id'}
    _description = "Ward Dashboard"
    _auto = False
    _table = "nh_eobs_ward_dashboard"

    _clinical_risk_selection = [['NoScore', 'No Score Yet'],
                                ['High', 'High Risk'],
                                ['Medium', 'Medium Risk'],
                                ['Low', 'Low Risk'],
                                ['None', 'No Risk']]

    def _get_wm_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from loc_users
                 where group_name = 'NH Clinical Ward Manager Group'
                        and location_id in (%s)""" % ", ".join([str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update({r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    def _get_dr_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from child_loc_users
                 where group_name = 'NH Clinical Doctor Group'
                        and location_id in (%s)""" % ", ".join([str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update({r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Location', required=1, ondelete='restrict'),
        'waiting_patients': fields.integer('Waiting Patients'),
        'patients_in_bed': fields.integer('Patients in Bed'),
        'related_hcas': fields.integer('HCAs'),
        'related_nurses': fields.integer('Nurses'),
        'highest_risk': fields.selection(_clinical_risk_selection, "Highest Risk"),
        'assigned_wm_ids': fields.function(_get_wm_ids, type='many2many', relation='res.users', string='Ward Managers'),
        'assigned_doctor_ids': fields.function(_get_dr_ids, type='many2many', relation='res.users', string='Doctors')
    }

    def init(self, cr):
        cr.execute("""
        drop view if exists %s;
        drop view if exists loc_waiting_patients;
        drop view if exists loc_patients_in_bed;
        drop view if exists loc_users;
        drop view if exists child_loc_users;
        drop view if exists loc_patients_by_risk;

        create or replace view loc_patients_by_risk as (
            select
                wl.ward_id as location_id,
                e1.clinical_risk,
                count(spell.id) as patients
            from nh_clinical_spell spell
            inner join nh_activity activity on activity.id = spell.activity_id and activity.state = 'started'
            inner join nh_clinical_location location on location.id = spell.location_id and location.usage = 'bed'
            inner join ward_locations wl on wl.id = location.id
            inner join ews1 e1 on e1.spell_activity_id = activity.id
            group by wl.ward_id, e1.clinical_risk
        );

        create or replace view loc_patients_in_bed as (
            select
                wl.ward_id as location_id,
                count(spell.id) as patients_in_bed
            from nh_clinical_spell spell
            inner join nh_activity activity on activity.id = spell.activity_id and activity.state = 'started'
            inner join nh_clinical_location location on location.id = spell.location_id and location.usage = 'bed'
            inner join ward_locations wl on wl.id = location.id
            group by wl.ward_id
        );

        create or replace view loc_waiting_patients as (
            select
                location.id as location_id,
                count(placement.id) as waiting_patients
            from nh_clinical_patient_placement placement
            inner join nh_activity activity on activity.id = placement.activity_id and activity.state = 'scheduled'
            inner join nh_clinical_location location on location.id = placement.suggested_location_id
            group by location.id
        );

        create or replace view loc_users as (
            select
                location.id as location_id,
                groups.name as group_name,
                array_agg(distinct users.id) as user_ids
            from res_groups groups
            left join res_groups_users_rel gurel on gurel.gid = groups.id
            left join res_users users on users.id = gurel.uid
            left join user_location_rel ulrel on ulrel.user_id = users.id
            left join nh_clinical_location location on location.id = ulrel.location_id
            group by location.id, groups.name
        );

        create or replace view child_loc_users as (
            select
                wl.ward_id as location_id,
                groups.name as group_name,
                array_agg(distinct users.id) as user_ids,
                count(distinct users.id) as related_users
            from res_groups groups
            left join res_groups_users_rel gurel on gurel.gid = groups.id
            left join res_users users on users.id = gurel.uid
            left join user_location_rel ulrel on ulrel.user_id = users.id
            left join nh_clinical_location location on location.id = ulrel.location_id
            left join ward_locations wl on wl.id = location.id
            group by wl.ward_id, groups.name
        );

        create or replace view %s as (
            select
                location.id as id,
                location.id as location_id,
                lwp.waiting_patients,
                lpbed.patients_in_bed,
                clu1.related_users as related_hcas,
                clu2.related_users as related_nurses
            from nh_clinical_location location
            left join loc_waiting_patients lwp on lwp.location_id = location.id
            left join loc_patients_in_bed lpbed on lpbed.location_id = location.id
            left join child_loc_users clu1 on clu1.location_id = location.id and clu1.group_name = 'NH Clinical HCA Group'
            left join child_loc_users clu2 on clu2.location_id = location.id and clu2.group_name = 'NH Clinical Nurse Group'
            where location.usage = 'ward'
        )
        """ % (self._table, self._table))
