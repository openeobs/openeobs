# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools
from openerp.addons.t4activity.activity import except_if
from openerp import SUPERUSER_ID

class wardboard_patient_placement(orm.TransientModel):
    _name = "wardboard.patient.placement"
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'ward_location_id':  fields.many2one('t4.clinical.location', "Ward"),
        'bed_src_location_id':  fields.many2one('t4.clinical.location', "Source Bed"),
        'bed_dst_location_id':  fields.many2one('t4.clinical.location', "Destination Bed")
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

class wardboard_device_session_start(orm.TransientModel):
    _name = "wardboard.device.session.start"
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

class wardboard_device_session_complete(orm.TransientModel):
    _name = "wardboard.device.session.complete"

    _columns = {

        'session_id': fields.many2one('t4.clinical.device.session', 'Session'),
    }   
    
    def do_complete(self, cr, uid, ids, context=None):
        activity_pool = self.pool['t4.activity']
        wiz = self.browse(cr, uid, ids[0])
        activity_pool.complete(cr, uid, wiz.session_id.activity_id.id, context)
        # refreshing view
        spell_activity_id = wiz.session_id.activity_id.parent_id.id
        wardboard_pool = self.pool['t4.clinical.wardboard']
        wardboard_id = wardboard_pool.search(cr, uid, [['spell_activity_id','=',spell_activity_id]])[0]
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 't4clinical_ui', 'view_wardboard_form')[1]
        #FIXME should be done more elegantly on client side
        return {
            'type': 'ir.actions.act_window',
            'res_model': 't4.clinical.wardboard',
            'res_id': wardboard_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'inline',
            'context': context,
            'view_id': view_id
        }
        
        context.update({'active_model': 't4.clinical.wardboard', 'active_id': wardboard_id, 'active_ids': [wardboard_id]})        

class t4_clinical_device_session(orm.TransientModel):
    _inherit = "t4.clinical.device.session"            

    def device_session_complete(self, cr, uid, ids, context=None):

        device_session = self.browse(cr, uid, ids[0], context=context)
        res_id = self.pool['wardboard.device.session.complete'].create(cr, uid, {'session_id': device_session.id})
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 't4clinical_ui', 'view_wardboard_device_session_complete_form')[1]

        return {
            'name': "Complete Device Session: %s" % device_session.patient_id.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.complete',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }



class t4_clinical_wardboard(orm.Model):
    _name = "t4.clinical.wardboard"
    _inherits = {
                 't4.clinical.patient': 'patient_id',
#                 't4.clinical.spell': 'spell_activity_id'
    }
    _description = "Wardboard"
    _auto = False
    _table = "t4_clinical_wardboard"
    _trend_strings = [('up', 'up'), ('down', 'down'), ('same', 'same'), ('none', 'none'), ('one', 'one')]
    _rec_name = 'full_name'

    def _get_logo(self, cr, uid, ids, fields_name, arg, context=None):
        res = {}
        for board in self.browse(cr, uid, ids, context=context):
            res[board.id] = board.patient_id.partner_id.company_id.logo
        return res

    _clinical_risk_selection = [['NoScore', 'No Score Yet'],
                                ['High', 'High Risk'],
                                ['Medium', 'Medium Risk'],
                                ['Low', 'Low Risk'],
                                ['None', 'No Risk']]
    _boolean_selection = [('yes', 'Yes'),
                          ('no', 'No')]
    
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        umap = self.pool['t4.clinical.api'].user_map(cr,user, 
                                                     group_xmlids=['group_t4clinical_hca', 'group_t4clinical_nurse',
                                                                   'group_t4clinical_ward_manager', 'group_t4clinical_doctor'])
        
        self._columns['o2target'].readonly = not (umap.get(user) and 'group_t4clinical_doctor' in umap[user]['group_xmlids'])
        res = super(t4_clinical_wardboard, self).fields_view_get(cr, user, view_id, view_type, context, toolbar, submenu)    
        return res
    
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=1, ondelete='restrict'),
        'company_logo': fields.function(_get_logo, type='binary', string='Logo'),
        'spell_activity_id': fields.many2one('t4.activity', 'Spell Activity'),
        'spell_date_started': fields.datetime('Spell Start Date'),
        'spell_date_terminated': fields.datetime('Spell Discharge Date'),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'spell_code': fields.text('Spell Code'),
        'full_name': fields.text("Family Name"),
        'location': fields.text("Location"),
        'clinical_risk': fields.selection(_clinical_risk_selection, "Clinical Risk"),
        'ward_id': fields.many2one('t4.clinical.location', 'Ward'),
        'location_id': fields.many2one('t4.clinical.location', "Location"),
        'sex': fields.text("Sex"),
        'dob': fields.datetime("DOB"),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'age': fields.integer("Age"),
        'next_diff': fields.text("Time to Next Obs"),
        'frequency': fields.text("Frequency"),
        'ews_score_string': fields.text("Latest Score"),
        'ews_score': fields.integer("Latest Score"),
        'ews_trend_string': fields.selection(_trend_strings, "Score Trend String"),
        'ews_trend': fields.integer("Score Trend"),
        'mrsa': fields.selection(_boolean_selection, "MRSA"),
        'diabetes': fields.selection(_boolean_selection, "Diabetes"),
        'pbp_monitoring': fields.selection(_boolean_selection, "Postural Blood Pressure Monitoring"),
        'height': fields.float("Height"),
        'o2target': fields.many2one('t4.clinical.o2level', 'O2 Target'),
        'consultant_names': fields.text("Consulting Doctors"),
    }

    def _get_cr_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [['NoScore', 'No Score Yet'], ['High', 'High Risk'], ['Medium', 'Medium Risk'], ['Low', 'Low Risk'], ['None', 'No Risk']]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'clinical_risk': _get_cr_groups,
    }
    
    def device_session_start(self, cr, uid, ids, context=None):
        from pprint import pprint as pp
        print "ids: %s" % ids
        wardboard = self.browse(cr, uid, ids[0], context=context)
        res_id = self.pool['wardboard.device.session.start'].create(cr, uid, 
                                                        {
                                                         'patient_id': wardboard.patient_id.id,
                                                         'device_id': None
                                                         })
        view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 't4clinical_ui', 'view_wardboard_device_session_start_form')[1]
        return {
            'name': "Start Device Session: %s" % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.start',
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

    def write(self, cr, uid, ids, vals, context=None):
        activity_pool = self.pool['t4.activity']
        for wb in self.browse(cr, uid, ids, context=context):
            if 'mrsa' in vals:
                mrsa_pool = self.pool['t4.clinical.patient.mrsa']
                mrsa_id = mrsa_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'mrsa': vals['mrsa'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, mrsa_id, context=context)
            if 'diabetes' in vals:
                diabetes_pool = self.pool['t4.clinical.patient.diabetes']
                diabetes_id = diabetes_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'diabetes': vals['diabetes'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, diabetes_id, context=context)
            if 'pbp_monitoring' in vals:
                pbpm_pool = self.pool['t4.clinical.patient.pbp_monitoring']
                pbpm_id = pbpm_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'pbp_monitoring': vals['pbp_monitoring'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, pbpm_id, context=context)
            if 'o2target' in vals:
                o2target_pool = self.pool['t4.clinical.patient.o2target']
                o2target_id = o2target_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'level_id': vals['o2target']
                }, context=context)
                activity_pool.complete(cr, uid, o2target_id, context=context)
        return True

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
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_activity activity on ews.activity_id = activity.id
        where activity.state = 'completed'
        ),
scheduled_ews as(
        select 
            spell.patient_id,
            activity.date_scheduled,
            ews.frequency,
            case when activity.date_scheduled >= now() then '' else 'overdue: ' end as next_diff_polarity,
            case activity.date_scheduled is null
                when false then justify_hours(greatest(now(),activity.date_scheduled) - least(now(),activity.date_scheduled)) 
                else interval '0s' 
            end as next_diff_interval,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
        inner join t4_activity activity on ews.activity_id = activity.id
        where activity.state = 'scheduled'
        ),
completed_mrsa as(
        select
            mrsa.id,
            spell.patient_id,
            mrsa.mrsa,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_mrsa mrsa on mrsa.patient_id = spell.patient_id
        inner join t4_activity activity on mrsa.activity_id = activity.id
        where activity.state = 'completed'
        ),
completed_diabetes as(
        select
            diabetes.id,
            spell.patient_id,
            diabetes.diabetes,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_diabetes diabetes on diabetes.patient_id = spell.patient_id
        inner join t4_activity activity on diabetes.activity_id = activity.id
        where activity.state = 'completed'
        ),
completed_pbp_monitoring as(
        select
            pbpm.id,
            spell.patient_id,
            pbpm.pbp_monitoring,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_pbp_monitoring pbpm on pbpm.patient_id = spell.patient_id
        inner join t4_activity activity on pbpm.activity_id = activity.id
        where activity.state = 'completed'
        ),
completed_height as(
        select 
            spell.patient_id,
            height.height,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
        from t4_clinical_spell spell
        left join t4_clinical_patient_observation_height height on height.patient_id = spell.patient_id
        inner join t4_activity activity on height.activity_id = activity.id
        where activity.state = 'completed'
        ),
completed_o2target as(
        select 
            spell.patient_id,
            level.id,
            rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
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
    spell_activity.date_terminated as spell_date_terminated,
    spell.pos_id,
    spell.code as spell_code,
    coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
    location.code as location,
    location.id as location_id,
    location.parent_id as ward_id,
    patient.sex,
    patient.dob,
    patient.other_identifier as hospital_number,
    patient.patient_identifier as nhs_number,
    extract(year from age(now(), patient.dob)) as age,
    case
        when extract(day from ews0.next_diff_interval) = 0 then ews0.next_diff_polarity || to_char(ews0.next_diff_interval, 'HH24:MI')
        else ews0.next_diff_polarity || extract(day from ews0.next_diff_interval) || ' day(s) ' || to_char(ews0.next_diff_interval, 'HH24:MI')
    end as next_diff,
    case ews0.frequency < 60
        when true then ews0.frequency || ' min(s)'
        else ews0.frequency/60 || ' hour(s) ' || ews0.frequency - ews0.frequency/60*60 || ' min(s)'
    end as frequency,
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
        when ews1.id is not null and ews2.id is null then 'first'
        when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen. 
    end as ews_trend_string,
    case
        when ews1.id is null then 'NoScore'
        else ews1.clinical_risk
    end as clinical_risk,
    ews1.score - ews2.score as ews_trend,
    height_ob.height,
    o2target_ob.id as o2target,
    case
        when mrsa.mrsa then 'yes'
        when mrsa.mrsa is null then 'no'
        else 'no'
    end as mrsa,
    case
        when diabetes.diabetes then 'yes'
        when diabetes.diabetes is null then 'no'
        else 'no'
    end as diabetes,
    case
        when pbpm.pbp_monitoring then 'yes'
        when pbpm.pbp_monitoring is null then 'no'
        else 'no'
    end as pbp_monitoring,
    cosulting_doctors.names as consultant_names
from t4_clinical_spell spell
inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join completed_ews ews1 on spell.patient_id = ews1.patient_id and ews1.rank = 1
left join completed_ews ews2 on spell.patient_id = ews2.patient_id and ews2.rank = 2
left join scheduled_ews ews0 on spell.patient_id = ews0.patient_id and ews0.rank = 1
left join completed_mrsa mrsa on spell.patient_id = mrsa.patient_id and mrsa.rank = 1 
left join completed_diabetes diabetes on spell.patient_id = diabetes.patient_id and diabetes.rank = 1
left join completed_pbp_monitoring pbpm on spell.patient_id = pbpm.patient_id and pbpm.rank = 1
left join completed_height height_ob on spell.patient_id = height_ob.patient_id and height_ob.rank = 1
left join completed_o2target o2target_ob on spell.patient_id = o2target_ob.patient_id and o2target_ob.rank = 1
left join cosulting_doctors on cosulting_doctors.spell_id = spell.id
where spell_activity.state = 'started'


)
        """ % (self._table, self._table))
        
        
