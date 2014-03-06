# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools


class analytic_entries_report(osv.osv):
    _name = "wardboard"
    _description = "Wardboard"
    _auto = False
    _table = "wardboard"
    _columns = {
        'full_name': fields.text("Family Name"),
        'location': fields.text("Location"),
        'dob': fields.datetime("DOB"),
        'age': fields.integer("Age"),
        'gender': fields.text("Gender"),
        'sex': fields.text("Sex"),
        'other_identifier': fields.text("Hopital ID"),
        'score1': fields.integer("Score1"),
        'score2': fields.integer("Score2"),
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
            create or replace view wardboard as (
                with 
                ranked_ews as(
                        select 
                            spell.patient_id,
                            ews.score,
                            rank() over (partition by spell.patient_id order by task.date_terminated, task.id desc)
                        from t4_clinical_spell spell
                        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
                        inner join t4_clinical_task task on ews.task_id = task.id
                        where task.state = 'completed'
                        )
                
                select 
                    spell.patient_id as id,
                    coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
                    location.code as location,
                    patient.dob,
                    extract(year from age(now(), patient.dob)) as age,
                    patient.gender,
                    patient.sex,
                    patient.other_identifier,
                    ews1.score as score1, 
                    ews2.score as score2
                from t4_clinical_spell spell
                inner join t4_clinical_patient patient on spell.patient_id = patient.id
                left join t4_clinical_location location on location.id = spell.location_id -- FIXME spell.location update on placement.complete
                left join (select score, patient_id, rank from ranked_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
                left join (select score, patient_id, rank from ranked_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
            )
        """)