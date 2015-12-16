# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Gives an overview of the current state of ward and bed
:class:`locations<base.nh_clinical_location>`.
"""
from openerp.osv import orm, fields
import logging
_logger = logging.getLogger(__name__)


class nh_eobs_ward_dashboard(orm.Model):
    """
    Extends :class:`location<base.nh_clinical_location>`, providing
    an overall state of a ward location.

    It shows number of related :class:`users<base.res_users>` by type,
    number of free beds, number of
    :class:`patients<base.nh_clinical_patient>` by risk, number of
    waiting patients, etc.
    """

    _name = "nh.eobs.ward.dashboard"
    _inherits = {'nh.clinical.location': 'location_id'}
    _description = "Ward Dashboard"
    _auto = False
    _table = "nh_eobs_ward_dashboard"

    def _get_wm_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from loc_users
                 where group_name = 'NH Clinical Ward Manager Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    def _get_dr_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from child_loc_users
                 where group_name = 'NH Clinical Doctor Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    def _get_bed_ids(self, cr, uid, ids, fiel_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, bed_ids
                 from ward_beds
                 where location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update({r['location_id']: r['bed_ids'] for r in cr.dictfetchall()})
        return res

    def _get_waiting_patient_ids(self, cr, uid, ids, fiel_name, arg,
                                 context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, patients_waiting_ids
                 from loc_waiting_patients
                 where location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['patients_waiting_ids']
             for r in cr.dictfetchall()})
        return res

    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Location',
                                       required=1, ondelete='restrict'),
        'waiting_patients': fields.integer('Waiting Patients'),
        'patients_in_bed': fields.integer('Patients in Bed'),
        'free_beds': fields.integer('Free Beds'),
        'related_hcas': fields.integer('HCAs'),
        'related_nurses': fields.integer('Nurses'),
        'related_doctors': fields.integer('Doctors'),
        'kanban_color': fields.integer('Kanban Color'),
        'assigned_wm_ids': fields.function(
            _get_wm_ids, type='many2many', relation='res.users',
            string='Ward Managers'),
        'assigned_doctor_ids': fields.function(
            _get_dr_ids, type='many2many', relation='res.users',
            string='Doctors'),
        'bed_ids': fields.function(
            _get_bed_ids, type='many2many', relation='nh.eobs.bed.dashboard',
            string='Beds'),
        'waiting_patient_ids': fields.function(
            _get_waiting_patient_ids, type='many2many',
            relation='nh.clinical.patient', string='Waiting Patients'),
        'high_risk_patients': fields.integer('High Risk Patients'),
        'med_risk_patients': fields.integer('Medium Risk Patients'),
        'low_risk_patients': fields.integer('Low Risk Patients'),
        'no_risk_patients': fields.integer('No Risk Patients'),
        'noscore_patients': fields.integer('No Score Patients')
    }

    def patient_board(self, cr, uid, ids, context=None):
        """
        Returns an Odoo `action` which defines a `form` view for a
        :class:`wardboard<wardboard.nh_clinical_wardboard>` for all
        :class:`patients<base.nh_clinical_patient>` in an `open`
        :class:`spell<spell.nh_clinical_spell>` and
        :class:`placed<operations.nh_clinical_patient_placement>` in a
        bed :class:`location<base.nh_clinical_location>`.

        :param ids: ward dashboard ids
        :type ids: list
        :returns: Odoo `action` definition
        :rtype: dict
        """

        wdb = self.browse(cr, uid, ids[0], context=context)
        context.update({'search_default_clinical_risk': 1,
                        'search_default_high_risk': 0,
                        'search_default_ward_id': wdb.id})
        kanban_view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_kanban')[1]
        tree_view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_tree')[1]
        form_view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_form')[1]
        return {
            'name': 'Acuity Board',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'views': [(kanban_view_id, 'kanban'),
                      (tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('spell_state', '=', 'started'),
                       ('location_id.usage', '=', 'bed')],
            'target': 'current',
            'context': context
        }

    def init(self, cr):
        cr.execute("""
        drop view if exists %s cascade;
        drop view if exists loc_waiting_patients cascade;
        drop view if exists loc_availability cascade;
        drop view if exists loc_users cascade;
        drop view if exists child_loc_users cascade;
        drop view if exists loc_patients_by_risk cascade;
        drop view if exists loc_risk_patients_count cascade;
        drop view if exists ward_beds cascade;

        create or replace view loc_patients_by_risk as (
            select
                wl.ward_id as location_id,
                case
                    when e1.clinical_risk is null then 'NoScore'
                    else e1.clinical_risk
                end as clinical_risk,
                count(spell.id) as patients
            from nh_clinical_spell spell
            inner join nh_activity activity
            on activity.id = spell.activity_id and activity.state = 'started'
            inner join nh_clinical_location location
            on location.id = spell.location_id and location.usage = 'bed'
            inner join ward_locations wl on wl.id = location.id
            left join ews1 e1 on e1.spell_activity_id = activity.id
            group by wl.ward_id, e1.clinical_risk
        );

        create or replace view loc_risk_patients_count as (
            select
                location.id as location_id,
                high.patients as high_risk_patients,
                med.patients as med_risk_patients,
                low.patients as low_risk_patients,
                no.patients as no_risk_patients,
                nos.patients as noscore_patients
            from nh_clinical_location location
            left join loc_patients_by_risk high
            on high.location_id = location.id and high.clinical_risk = 'High'
            left join loc_patients_by_risk med
            on med.location_id = location.id and med.clinical_risk = 'Medium'
            left join loc_patients_by_risk low
            on low.location_id = location.id and low.clinical_risk = 'Low'
            left join loc_patients_by_risk no
            on no.location_id = location.id and no.clinical_risk = 'None'
            left join loc_patients_by_risk nos
            on nos.location_id = location.id and nos.clinical_risk = 'NoScore'
        );

        create or replace view loc_availability as (
            select
                wl.ward_id as location_id,
                count(spell.id) as patients_in_bed,
                count(location.id) - count(spell.id) as free_beds
            from nh_clinical_location location
            inner join ward_locations wl on wl.id = location.id
            left join nh_clinical_spell spell
            on spell.location_id = location.id
            left join nh_activity activity
            on activity.id = spell.activity_id and activity.state = 'started'
            where location.usage = 'bed' and location.active = true
            group by wl.ward_id
        );

        create or replace view loc_waiting_patients as (
            select
                placement.location_id as location_id,
                count(distinct placement.patient_id) as waiting_patients,
                array_agg(distinct placement.patient_id)
                as patients_waiting_ids
            from nh_clinical_placement placement
            inner join nh_activity activity on activity.id = placement.id
            inner join nh_activity spell_activity
            on spell_activity.id = activity.parent_id
            where spell_activity.state = 'started'
            group by placement.location_id
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
            left join nh_clinical_location location
            on location.id = ulrel.location_id
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
            left join nh_clinical_location location
            on location.id = ulrel.location_id
            left join ward_locations wl on wl.id = location.id
            group by wl.ward_id, groups.name
        );

        create or replace view ward_beds as (
            select
                wl.ward_id as location_id,
                array_agg(distinct location.id) as bed_ids
            from nh_clinical_location location
            inner join ward_locations wl on wl.id = location.id
            where location.usage = 'bed'
            group by wl.ward_id
        );

        create or replace view %s as (
            select
                location.id as id,
                location.id as location_id,
                lwp.waiting_patients,
                avail.patients_in_bed,
                avail.free_beds,
                clu1.related_users as related_hcas,
                clu2.related_users as related_nurses,
                clu3.related_users as related_doctors,
                rpc.high_risk_patients,
                rpc.med_risk_patients,
                rpc.low_risk_patients,
                rpc.no_risk_patients,
                rpc.noscore_patients,
                case
                    when rpc.high_risk_patients > 0 then 2
                    when rpc.med_risk_patients >0 then 3
                    when rpc.low_risk_patients >0 then 4
                    else 7
                end as kanban_color
            from nh_clinical_location location
            left join loc_waiting_patients lwp on lwp.location_id = location.id
            left join loc_availability avail on avail.location_id = location.id
            left join child_loc_users clu1 on clu1.location_id = location.id
                and clu1.group_name = 'NH Clinical HCA Group'
            left join child_loc_users clu2 on clu2.location_id = location.id
                and clu2.group_name = 'NH Clinical Nurse Group'
            left join child_loc_users clu3 on clu3.location_id = location.id
                and clu3.group_name = 'NH Clinical Doctor Group'
            left join loc_risk_patients_count rpc
                on rpc.location_id = location.id
            where location.usage = 'ward'
        )
        """ % (self._table, self._table))


class nh_eobs_bed_dashboard(orm.Model):
    """
    Extends :class:`location<base.nh_clinical_location>`, providing
    an overall state of a bed location.

    It shows number of `assigned` and `following` nurses and hcas
    :class:`users<base.res_users>` as well as the
    :class:`patient<base.nh_clinical_patient>` placed in the bed.
    """

    _name = "nh.eobs.bed.dashboard"
    _inherits = {'nh.clinical.location': 'location_id'}
    _description = "Bed Dashboard"
    _auto = False
    _table = "nh_eobs_bed_dashboard"

    def _get_hca_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from loc_users
                 where group_name = 'NH Clinical HCA Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    def _get_nurse_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, user_ids
                 from loc_users
                 where group_name = 'NH Clinical Nurse Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['user_ids'] for r in cr.dictfetchall()})
        return res

    def _get_patient_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, patient_ids
                 from loc_patients
                 where location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['patient_ids'] for r in cr.dictfetchall()})
        return res

    def _get_nurse_follower_ids(self, cr, uid, ids, field_name, arg,
                                context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, follower_ids
                 from loc_followers
                 where group_name = 'NH Clinical Nurse Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['follower_ids'] for r in cr.dictfetchall()})
        return res

    def _get_hca_follower_ids(self, cr, uid, ids, field_name, arg,
                              context=None):
        res = {}.fromkeys(ids, False)
        sql = """select location_id, follower_ids
                 from loc_followers
                 where group_name = 'NH Clinical HCA Group'
                        and location_id in (%s)""" % ", ".join(
            [str(location_id) for location_id in ids])
        cr.execute(sql)
        res.update(
            {r['location_id']: r['follower_ids'] for r in cr.dictfetchall()})
        return res

    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Location',
                                       required=1, ondelete='restrict'),
        'assigned_hca_ids': fields.function(
            _get_hca_ids, type='many2many', relation='res.users',
            string='HCAs'),
        'assigned_nurse_ids': fields.function(
            _get_nurse_ids, type='many2many', relation='res.users',
            string='Nurses'),
        'patient_ids': fields.function(
            _get_patient_ids, type='many2many', relation='nh.clinical.patient',
            string="Patients"),
        'nurse_follower_ids': fields.function(
            _get_nurse_follower_ids, type='many2many', relation='res.users',
            string="Nurse Stand-Ins"),
        'hca_follower_ids': fields.function(
            _get_hca_follower_ids, type='many2many', relation='res.users',
            string="HCA Stand-Ins"),
    }

    def init(self, cr):
        cr.execute("""
        drop view if exists loc_patients;
        drop view if exists loc_followers;
        drop view if exists %s;

        create or replace view loc_patients as (
            select
                location.id as location_id,
                array_agg(distinct patient.id) as patient_ids
            from nh_clinical_spell spell
            inner join nh_activity activity on activity.id = spell.activity_id
                and activity.state = 'started'
            inner join nh_clinical_patient patient
                on patient.id = spell.patient_id
            left join nh_clinical_location location
                on location.id = spell.location_id
            group by location.id
        );

        create or replace view loc_followers as (
            select
                location.id as location_id,
                groups.name as group_name,
                array_agg(distinct users.id) as follower_ids
            from nh_clinical_spell spell
            inner join nh_activity activity on activity.id = spell.activity_id
                and activity.state = 'started'
            inner join nh_clinical_patient patient
                on patient.id = spell.patient_id
            left join nh_clinical_location location
                on location.id = spell.location_id
            left join user_patient_rel uprel on uprel.patient_id = patient.id
            left join res_users users on users.id = uprel.user_id
            left join res_groups_users_rel gurel on gurel.uid = users.id
            left join res_groups groups on groups.id = gurel.gid
            group by location.id, groups.name
        );

        create or replace view %s as (
            select
                location.id as id,
                location.id as location_id
            from nh_clinical_location location
            where location.usage = 'bed'
        )
        """ % (self._table, self._table))
