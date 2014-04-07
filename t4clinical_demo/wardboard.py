# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools


class t4_clinical_wardboard(orm.Model):
    _name = "t4.clinical.wardboard"
    _inherits = {'t4.clinical.patient': 'patient_id'}
    _description = "Wardboard"
    _auto = False
    _table = "t4_clinical_wardboard"
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'spell_activity_id': fields.many2one('t4.clinical.activity', 'Spell Activity'),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'spell_code': fields.text('Spell Code'),
        'full_name': fields.text("Family Name"),
        'location': fields.text("Location"),
        'sex': fields.text("Sex"),
        'dob': fields.datetime("DOB"),
        'age': fields.integer("Age"),
        'next_diff': fields.text("Time to Next Obs"),
        'frequency': fields.text("Frequency"),
        'ews_score': fields.integer("Latest Score"),
        'ews_trend': fields.integer("Score Trend"),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
drop view if exists %s;
create or replace view %s as (
with 
completed_ews as(
        select 
            spell.patient_id,
            ews.score,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_clinical_activity activity on ews.activity_id = activity.id
        where activity.state = 'completed'
        ),
scheduled_ews as(
        select 
            spell.patient_id,
            activity.date_scheduled,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_clinical_activity activity on ews.activity_id = activity.id
        where activity.state = 'scheduled'
        ),
height_weight_history as(
        select 
            ob.patient_id,
            array_agg(ob.id) as ids
        from t4_clinical_patient_observation_ews ob -- height_weight
        inner join t4_clinical_activity activity on activity.id = ob.activity_id
        where activity.state = 'completed'
        group by ob.patient_id
        )
select 
    spell.patient_id as id,
    spell.patient_id as patient_id,
    spell_activity.id as spell_activity_id,
    spell.pos_id,
    spell.code as spell_code,
    coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
    location.code as location,
    patient.sex,
    patient.dob,
    extract(year from age(now(), patient.dob)) as age,
    (now() - ews0.date_scheduled)::text as next_diff, 
    trigger.unit_qty || ' ' || trigger.unit || '(s)' as frequency,
    ews1.score as ews_score,
    ews1.score - ews2.score as ews_trend
from t4_clinical_spell spell
inner join t4_clinical_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join (select score, patient_id, rank from completed_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
left join (select score, patient_id, rank from completed_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
left join t4_clinical_patient_activity_trigger trigger on trigger.patient_id = patient.id and trigger.data_model = 't4.clinical.patient.observation.ews' and trigger.active = 't'
left join (select date_scheduled, patient_id, rank from scheduled_ews where rank = 1) ews0 on spell.patient_id = ews0.patient_id
left join height_weight_history on height_weight_history.patient_id = patient.id
where spell_activity.state = 'started'
)
        """ % (self._table, self._table))
        
        
