# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools
from openerp.addons.t4activity.activity import except_if

class wardboard_patient_placement(orm.TransientModel):
    _name = "wardboard.patient.placement"
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'ward_location_id':  fields.many2one('t4.clinical.location',"Ward"),
        'bed_src_location_id':  fields.many2one('t4.clinical.location',"Source Bed"),
        'bed_dst_location_id':  fields.many2one('t4.clinical.location',"Destination Bed")
    }
    def do_move(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0])
        spell_activity_id = self.pool['t4.clinical.api'].get_patient_spell_activity_id(cr, uid, wiz.patient_id.id)
        placement_activity_id = self.pool['t4.clinical.patient.placement']\
                                .create_activity(cr, uid, {'parent_id': spell_activity_id}, 
                                                           {
                                                            'suggested_location_id': wiz.bed_dst_location_id.id,
                                                            'location_id': wiz.bed_dst_location_id.id,
                                                            'patient_id': wiz.patient_id.id
                                                           })
        self.pool['t4.activity'].complete(cr, uid, placement_activity_id, context)

class wardboard_device_session(orm.TransientModel):
    _name = "wardboard.device.session"
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'device_id':  fields.many2one('t4.clinical.device',"Device"),
    }
    def do_start(self, cr, uid, ids, context=None):
        wiz = self.browse(cr, uid, ids[0])
        spell_activity_id = self.pool['t4.clinical.api'].get_patient_spell_activity_id(cr, uid, wiz.patient_id.id)
        device_activity_id = self.pool['t4.clinical.device.session']\
                                .create_activity(cr, uid, {'parent_id': spell_activity_id}, 
                                                           {
                                                            'patient_id': wiz.patient_id.id,
                                                            'device_id': wiz.device_id.id
                                                           })
        self.pool['t4.activity'].start(cr, uid, device_activity_id, context)        

class t4_clinical_wardboard(orm.Model):
    _name = "t4.clinical.wardboard"
    _inherits = {
                 't4.clinical.patient': 'patient_id',
#                 't4.clinical.spell': 'spell_activity_id'
    }
    _description = "Wardboard"
    _auto = False
    _table = "t4_clinical_wardboard"
    _trend_strings = [('up','up'), ('down','down'), ('same','same'), ('none','none'), ('one','one')]
    _rec_name = 'full_name'

    def _get_logo(self, cr, uid, ids, fields_name, arg, context=None):
        res = {}
        for board in self.browse(cr, uid, ids, context=context):
            res[board.id] = board.patient_id.partner_id.company_id.logo
        return res

    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'company_logo': fields.function(_get_logo, type='binary', string='Logo'),
        'spell_activity_id': fields.many2one('t4.activity', 'Spell Activity'),
        'spell_date_started': fields.datetime('Spell Start Date'),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'spell_code': fields.text('Spell Code'),
        'full_name': fields.text("Family Name"),
        'location': fields.text("Location"),
        'clinical_risk': fields.text("Clinical Risk"),
        'location_id': fields.many2one('t4.clinical.location',"Location"),
        'sex': fields.text("Sex"),
        'dob': fields.datetime("DOB"),
        'age': fields.integer("Age"),
        'next_diff': fields.text("Time to Next Obs"),
        'frequency': fields.text("Frequency"),
        'ews_score_string': fields.text("Latest Score"),
        'ews_score': fields.integer("Latest Score"),
        'ews_trend_string': fields.selection(_trend_strings, "Score Trend String"),
        'ews_trend': fields.integer("Score Trend"),
        'height': fields.float("Height"),
        'o2target_min': fields.integer("O2 Target Min"),
        'o2target_max': fields.integer("O2 Target Max"),
        'o2target_string': fields.text("O2 Target"),
        'consultant_names': fields.text("Consulting Doctors"),
    }
    
    def start_device_session(self, cr, uid, ids, context=None):
        from pprint import pprint as pp
        print "ids: %s" % ids
        wardboard = self.browse(cr, uid, ids[0], context=context)
        res_id = self.pool['wardboard.device.session'].create(cr, uid, 
                                                        {
                                                         'patient_id': wardboard.patient_id.id,
                                                         'device_id': None
                                                         })
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 't4clinical_ui', 'view_wardboard_device_session_form')[1]
        return {
            'name': "Start Device Session: %s" % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }
    
    def wardboard_patient_placement(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)
        # assumed that patient's placement is completed
        # parent location of bed is taken as ward
        except_if(wardboard.location_id.usage != 'bed', msg="Patient must be placed to bed before moving!")
        res_id = self.pool['wardboard.patient.placement'].create(cr, uid, 
                                                        {
                                                         'patient_id': wardboard.patient_id.id,
                                                         'ward_location_id': wardboard.location_id.parent_id.id,
                                                         'bed_src_location_id': wardboard.location_id.id,
                                                         'bed_dst_location_id': None
                                                         })
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 't4clinical_ui', 'view_wardboard_patient_placement_form')[1]
        return {
            'name': "Move Patient: %s" % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.patient.placement',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }
        
    def wardboard_chart(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_wardboard_chart_form')], context=context)
        if not model_data_ids:
            pass
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_weight_chart(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_wardboard_weight_chart_form')], context=context)
        if not model_data_ids:
            pass
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']

        context.update({'height': wardboard.height})
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_bs_chart(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_wardboard_bs_chart_form')], context=context)
        if not model_data_ids:
            pass
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_ews(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.patient.observation.ews',
            'view_mode': 'tree',
            'view_type': 'tree',
            'domain': [('patient_id', '=', wardboard.patient_id.id), ('state', '=', 'completed')],
            'target': 'new',
            'context': context
        }

    def print_chart(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_wardboard_print_chart_form')], context=context)
        if not model_data_ids:
            pass
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        context.update({'printing': 'true'})
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'inline',
            'context': context,
            'view_id': int(view_id)
        }

    def print_report(self, cr, uid, ids, context=None):
        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_wardboard_print_report_form')], context=context)
        if not model_data_ids:
            pass
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        context.update({'printing': 'true'})
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'inline',
            'context': context,
            'view_id': int(view_id)
        }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
drop view if exists %s;
create or replace view %s as (
with 
completed_ews as(
        select
            ews.id,
            spell.patient_id,
            ews.score,
            ews.clinical_risk,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_activity activity on ews.activity_id = activity.id
        where activity.state = 'completed'
        ),
scheduled_ews as(
        select 
            spell.patient_id,
            activity.date_scheduled,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_activity activity on ews.activity_id = activity.id
        where activity.state = 'scheduled'
        ),
completed_height as(
        select 
            spell.patient_id,
            height.height,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_height height on height.patient_id = spell.patient_id
        inner join t4_activity activity on height.activity_id = activity.id
        where activity.state = 'completed'
        ),
completed_o2target as(
        select 
            spell.patient_id,
            level.min,
            level.max,
            rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_o2target o2target on o2target.patient_id = spell.patient_id
        inner join t4_activity activity on o2target.activity_id = activity.id
        inner join t4_clinical_o2level level on level.id = o2target.level_id
        where activity.state = 'completed'
        ),
cosulting_doctors as(
        select 
            spell.id as spell_id,
            array_to_string(array_agg(doctor.name), ' / ') as names    
        from t4_clinical_spell spell
        inner join con_doctor_spell_rel on con_doctor_spell_rel.spell_id = spell.id
        inner join res_partner doctor on con_doctor_spell_rel.doctor_id = doctor.id
        group by spell.id
        )
select 
    spell.patient_id as id,
    spell.patient_id as patient_id,
    spell_activity.id as spell_activity_id,
    spell_activity.date_started as spell_date_started,    
    spell.pos_id,
    spell.code as spell_code,
    coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
    location.code as location,
    location.id as location_id,
    patient.sex,
    patient.dob,
    extract(year from age(now(), patient.dob)) as age,
    case
        when extract('epoch' from (now() - ews0.date_scheduled)) > 0 then
            coalesce( nullif( extract('day' from (now() - ews0.date_scheduled))::text || ' day(s) ','0 day(s) '),'' ) ||
            to_char((now() - ews0.date_scheduled), 'HH24:MI')
        else
            'overdue: ' ||
            coalesce( nullif( extract('day' from (now() - ews0.date_scheduled))::text || ' day(s) ','0 day(s) '),'' ) ||
            to_char(now() - ews0.date_scheduled, 'HH24:MI')            
        end as next_diff,
    spell.ews_frequency as frequency,
    case
        when ews1.id is null then 'none'
        else ews1.score::text
    end as ews_score_string,    
    ews1.score as ews_score,
    case
        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'down'
        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'up'
        when ews1.id is null and ews2.id is null then 'none'
        when ews1.id is not null and ews2.id is null then 'one'
        when ews1.id is null and ews2.id is not null then 'one' -- shouldn't happen. 
    end as ews_trend_string,
    case
        when ews1.clinical_risk is not null then ews1.clinical_risk
        when ews1.clinical_risk is null then 'None'
    end as clinical_risk,
    ews1.score - ews2.score as ews_trend,
    height_ob.height,
    o2target_ob.min as o2target_min,
    o2target_ob.max as o2target_max,
    o2target_ob.min::text || '-' || o2target_ob.max::text as o2target_string,
    cosulting_doctors.names as consultant_names
from t4_clinical_spell spell
inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join (select id, score, patient_id, rank, clinical_risk from completed_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
left join (select id, score, patient_id, rank from completed_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
left join (select date_scheduled, patient_id, rank from scheduled_ews where rank = 1) ews0 on spell.patient_id = ews0.patient_id
left join (select height, patient_id, rank from completed_height where rank = 1) height_ob on spell.patient_id = height_ob.patient_id
left join (select min, max, patient_id, rank from completed_o2target where rank = 1) o2target_ob on spell.patient_id = o2target_ob.patient_id
left join cosulting_doctors on cosulting_doctors.spell_id = spell.id
where spell_activity.state = 'started'
)
        """ % (self._table, self._table))
        
        
