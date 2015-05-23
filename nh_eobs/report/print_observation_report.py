__author__ = 'colinwren'
from openerp import api, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import fields
import json


class DataObj(object):
    def __init__(self, spell_id=None, start_time=None, end_time=None):
        self.spell_id = spell_id
        self.start_time = start_time
        self.end_time = end_time

class ObservationReport(models.AbstractModel):
    _name = 'report.nh.clinical.observation_report'

    @staticmethod
    def create_search_filter(spell_activity_id, model, start_date, end_date):
        filter = []
        if model in ['nh.clinical.patient.o2target', 'nh.clinical.patient.move']:
            filter = [['parent_id', '=', spell_activity_id], ['data_model', '=', model]]
        else:
            filter = [['parent_id', '=', spell_activity_id], ['data_model', '=', model], ['state', '=', 'completed']]
        if start_date:
            filter.append(['date_started', '>=', start_date.strftime(dtf)])
        if end_date:
            filter.append(['date_terminated', '<=', end_date.strftime(dtf)])
        return filter

    def convert_db_date_to_context_date(self, cr, uid, date_string, format, context=None):
        if format:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context).strftime(format)
        else:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context)

    @staticmethod
    def data_dict_to_obj(data_dict):
        spell_id = data_dict['spell_id'] if 'spell_id' in data_dict and data_dict['spell_id'] else None
        start = data_dict['start_time'] if 'start_time' in data_dict and data_dict['start_time'] else None
        end = data_dict['end_time'] if 'end_time' in data_dict and data_dict['end_time'] else None
        return DataObj(spell_id, start, end)


    @api.multi
    def render_html(self, data=None):
        cr, uid = self._cr, self._uid
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh.clinical.observation_report')
        pretty_date_format = '%d/%m/%Y %H:%M'

        if isinstance(data, dict):
            data = self.data_dict_to_obj(data)

        # set up data
        start_time = datetime.strptime(data.start_time, dtf) if data and data.start_time else False
        end_time = datetime.strptime(data.end_time, dtf) if data and data.end_time else False

        # set up pools
        api_pool = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        weight_pool = self.pool['nh.clinical.patient.observation.weight']
        height_pool = self.pool['nh.clinical.patient.observation.height']
        pbp_pool = self.pool['nh.clinical.patient.observation.pbp']
        oxygen_target_pool = self.pool['nh.clinical.patient.o2target']
        transfer_history_pool = self.pool['nh.clinical.patient.move']
        company_pool = self.pool['res.company']
        partner_pool = self.pool['res.partner']
        user_pool = self.pool['res.users']
        location_pool = self.pool['nh.clinical.location']

        # get user data
        #user_id = user_pool.search(cr, uid, [('login', '=', request.session['login'])],context=context)[0]
        user = user_pool.read(cr, uid, uid, ['name'], context=None)['name']

        # get company data
        company_name = company_pool.read(cr, uid, 1, ['name'])['name']
        company_logo = partner_pool.read(cr, uid, 1, ['image'])['image']

        # generate report timestamp
        time_generated = fields.datetime.context_timestamp(cr, uid, datetime.now(), context=None) \
            .strftime(pretty_date_format)

        if data and data.spell_id:
            spell_id = int(data.spell_id)
            spell = spell_pool.read(cr, uid, [spell_id])[0]
            # - get the start and end date of spell
            spell_start = self.convert_db_date_to_context_date(datetime.strptime(spell['date_started'], dtf), pretty_date_format, context=None)
            spell_end = spell['date_terminated']
            report_start = start_time.strftime(pretty_date_format) if start_time else spell_start
            if end_time:
                report_end = end_time.strftime(pretty_date_format)
            else:
                report_end = self.convert_db_date_to_context_date(datetime.strptime(spell_end, dtf), pretty_date_format, context=None) if spell_end else time_generated
            #
            spell_activity_id = spell['activity_id'][0]
            spell['consultants'] = partner_pool.read(cr, uid, spell['con_doctor_ids']) if len(spell['con_doctor_ids']) > 0 else False
            #
            # # - get patient id
            patient_id = spell['patient_id'][0]
            #
            # get patient information
            patient = patient_pool.read(cr, uid, [patient_id])[0]
            patient['dob'] = self.convert_db_date_to_context_date(datetime.strptime(patient['dob'], dtf), '%d/%m/%Y', context=None)
            #
            # # get ews observations for patient
            # # - search ews model with parent_id of spell id (maybe dates for refined foo) - activity: search with data_model of ews
            ews_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.ews', start_time, end_time))
            ews = activity_pool.read(cr, uid, ews_ids)

            # get triggered actions from ews
            # - search activity with ews ids as creator_id filter out EWS tasks
            for observation in ews:
                observation['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format)
                observation['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
                triggered_actions_ids = activity_pool.search(cr, uid, [['creator_id', '=', observation['id']]])
                observation['values'] = ews_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), dtf) if observation['values']['date_started'] else False
                observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), dtf) if observation['values']['date_terminated'] else False
                observation['triggered_actions'] = [v for v in activity_pool.read(cr, uid, triggered_actions_ids) if v['data_model'] != 'nh.clinical.patient.observation.ews']
                for t in observation['triggered_actions']:
                    t['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(t['date_started'], dtf), pretty_date_format) if t['date_started'] else False
                    t['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(t['date_terminated'], dtf), pretty_date_format) if t['date_terminated'] else False

            # get weight observations
            # - search weight model with parent_id of spell - dates
            weight_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.weight', start_time, end_time))
            weights = activity_pool.read(cr, uid, weight_ids)
            for observation in weights:
                observation['values'] = weight_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            patient['weight'] = weights[-1]['values']['weight'] if len(weights) > 0 else False
            #
            # # get height observations
            # # - search height model with parent_id of spell - dates
            height_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.height', start_time, end_time))
            heights = activity_pool.read(cr, uid, height_ids)
            for observation in heights:
                observation['values'] = height_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            patient['height'] = heights[-1]['values']['height'] if len(heights) > 0 else False
            #
            # # get PBP observations
            # # - search pbp model with parent_id of spell - dates
            pbp_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.pbp', start_time, end_time))
            pbps = activity_pool.read(cr, uid, pbp_ids)
            for observation in pbps:
                observation['values'] = pbp_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                observation['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
            #
            # # get o2 target history
            # # - search o2target model on patient with parent_id of spell - dates
            oxygen_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.o2target', start_time, end_time))
            oxygen_history = activity_pool.read(cr, uid, oxygen_history_ids)
            for observation in oxygen_history:
                observation['values'] = oxygen_target_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            #
            # # get transfer history
            # # - search move on patient with parent_id of spell - dates
            transfer_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.move', start_time, end_time))
            transfer_history = activity_pool.read(cr, uid, transfer_history_ids)
            for observation in transfer_history:
                observation['values'] = transfer_history_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                observation['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
                patient_location = location_pool.read(cr, uid, observation['values']['location_id'][0], [])
                observation['bed'] = patient_location['name'] if patient_location['name'] else False
                observation['ward'] = patient_location['parent_id'][1] if patient_location['parent_id'] else False
            if len(transfer_history) > 0:
                patient['bed'] = transfer_history[-1]['bed'] if transfer_history[-1]['bed'] else False
                patient['ward'] = transfer_history[-1]['ward'] if transfer_history[-1]['ward'] else False
            #
            json_obs = [v['values'] for v in ews]
            # for json_ob in json_obs:
            #     json_ob['date_terminated'] = datetime.strftime(datetime.strptime(json_ob['date_terminated'], dtf), phantomjs_date_format)
            json_ews = json.dumps(json_obs)

            docargs = {
                'doc_ids': self._ids,
                'doc_model': report.model,
                'docs': self,
                'spell': spell,
                'patient': patient,
                'ews': ews,
                'weights': weights,
                'pbps': pbps,
                'targeto2': oxygen_history,
                'transfer_history': transfer_history,
                'report_start': report_start,
                'report_end': report_end,
                'spell_start': spell_start,
                'company_logo': company_logo,
                'time_generated': time_generated,
                'hospital_name': company_name,
                'user_name': user,
            }
            return report_obj.render('nh_eobs.observation_report', docargs)
        else:
            return None