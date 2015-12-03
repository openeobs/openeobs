# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
from openerp import api, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import fields
import json
import copy


class DataObj(object):
    def __init__(self, spell_id=None, start_time=None, end_time=None, ews_only=None):
        self.spell_id = spell_id
        self.start_time = start_time
        self.end_time = end_time
        self.ews_only = ews_only

class ObservationReport(models.AbstractModel):
    _name = 'report.nh.clinical.observation_report'

    pretty_date_format = '%H:%M %d/%m/%y'
    wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"

    @staticmethod
    def create_search_filter(spell_activity_id, model, start_date, end_date):
        if not spell_activity_id:
            raise ValueError('No spell activity id supplied')
        if not model:
            raise ValueError('No model supplied')
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

    @staticmethod
    def convert_db_date_to_context_date(cr, uid, date_string, format, context=None):
        if format:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context).strftime(format)
        else:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context)

    @staticmethod
    def data_dict_to_obj(data_dict):
        spell_id = data_dict['spell_id'] if 'spell_id' in data_dict and data_dict['spell_id'] else None
        start = data_dict['start_time'] if 'start_time' in data_dict and data_dict['start_time'] else None
        end = data_dict['end_time'] if 'end_time' in data_dict and data_dict['end_time'] else None
        ews_only = data_dict['ews_only'] if 'ews_only' in data_dict and data_dict['ews_only'] else None
        return DataObj(spell_id, start, end, ews_only)

    def get_activity_data(self, spell_id, model, start_time, end_time):
        cr, uid = self._cr, self._uid
        act_pool = self.pool['nh.activity']
        activity_ids = act_pool.search(cr, uid,
                                       self.create_search_filter(
                                           spell_id,
                                           model, start_time, end_time))
        return act_pool.read(cr, uid, activity_ids)

    def get_model_data(self, spell_id, model, start, end):
        cr, uid = self._cr, self._uid
        model_pool = self.pool[model]
        act_data = self.get_activity_data(spell_id, model, start, end)
        if act_data:
            ds = act_data['date_started'] if 'data_started' in act_data and act_data['date_started'] else False
            dt = act_data['date_terminated'] if 'date_terminated' in act_data and act_data['date_terminated'] else False
            if ds:
                ds = self.convert_db_date_to_context_date(
                    cr, uid, datetime.strptime(ds, dtf),
                    self.pretty_date_format)
            if dt:
                dt = self.convert_db_date_to_context_date(
                    cr, uid, datetime.strptime(dt, dtf),
                    self.pretty_date_format)
        return self.get_model_values(model, act_data)

    def get_model_values(self, model, act_data):
        cr, uid = self._cr, self._uid
        model_pool = self.pool[model]
        for act in act_data:
            model_data = model_pool.read(cr, uid,
                                         int(act['data_ref'].split(',')[1]),
                                         [])
            if model_data:
                ds = model_data['date_started'] if 'data_started' in model_data and model_data['date_started'] else False
                dt = model_data['date_terminated'] if 'date_terminated' in model_data and model_data['date_terminated'] else False
                model_data['status'] = 'Yes' if 'status' in model_data and model_data['status'] else 'No'
                if ds:
                    ds = self.convert_db_date_to_context_date(
                        cr, uid, datetime.strptime(ds, dtf),
                        self.pretty_date_format)
                if dt:
                    dt = self.convert_db_date_to_context_date(
                        cr, uid, datetime.strptime(dt, dtf),
                        self.pretty_date_format)
            act['values'] = model_data
        return act_data

    def get_multi_model_data(self, spell_id, model_one, model_two,  start, end):
        act_data = self.get_activity_data(spell_id, model_one, start, end)
        return self.get_model_values(model_two, act_data)

    def get_model_data_as_json(self, model_data):
        for data in model_data:
            data['write_date'] = datetime.strftime(
                datetime.strptime(data['write_date'], dtf),
                self.wkhtmltopdf_format)
            data['create_date'] = datetime.strftime(
                datetime.strptime(data['create_date'], dtf),
                self.wkhtmltopdf_format)
            data['date_started'] = datetime.strftime(
                datetime.strptime(data['date_started'], dtf),
                self.wkhtmltopdf_format)
            data['date_terminated'] = datetime.strftime(
                datetime.strptime(data['date_terminated'], dtf),
                self.wkhtmltopdf_format)
        return json.dumps(model_data)


    @api.multi
    def render_html(self, data=None):
        cr, uid = self._cr, self._uid
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh.clinical.observation_report')
        pretty_date_format = self.pretty_date_format
        wkhtmltopdf_format = self.wkhtmltopdf_format

        if isinstance(data, dict):
            data = self.data_dict_to_obj(data)

        # set up data
        start_time = datetime.strptime(data.start_time, dtf) if data and data.start_time else False
        end_time = datetime.strptime(data.end_time, dtf) if data and data.end_time else False

        # set up pools
        activity_pool = self.pool['nh.activity']
        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        oxygen_target_pool = self.pool['nh.clinical.patient.o2target']
        company_pool = self.pool['res.company']
        partner_pool = self.pool['res.partner']
        user_pool = self.pool['res.users']
        location_pool = self.pool['nh.clinical.location']
        o2_level_pool = self.pool['nh.clinical.o2level']

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
            spell_start = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(spell['date_started'], dtf), pretty_date_format, context=None)
            spell_end = spell['date_terminated']
            report_start = start_time.strftime(pretty_date_format) if start_time else spell_start
            if end_time:
                report_end = end_time.strftime(pretty_date_format)
            else:
                report_end = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(spell_end, dtf), pretty_date_format, context=None) if spell_end else time_generated
            #
            spell_activity_id = spell['activity_id'][0]
            spell['consultants'] = partner_pool.read(cr, uid, spell['con_doctor_ids']) if len(spell['con_doctor_ids']) > 0 else False
            #
            # # - get patient id
            patient_id = spell['patient_id'][0]
            #
            # get patient information
            patient = patient_pool.read(cr, uid, [patient_id])[0]
            patient['dob'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(patient['dob'], dtf), '%d/%m/%Y', context=None)
            #
            # # get ews observations for patient
            # # - search ews model with parent_id of spell id (maybe dates for refined foo) - activity: search with data_model of ews
            ews = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.ews',
                                         start_time, end_time)

            # get triggered actions from ews
            # - search activity with ews ids as creator_id filter out EWS tasks
            for observation in ews:
                triggered_actions_ids = activity_pool.search(cr, uid, [['creator_id', '=', observation['id']]])
                o2_level_id = oxygen_target_pool.get_last(cr, uid, patient_id, observation['values']['date_terminated'])
                o2_level = o2_level_pool.browse(cr, uid, o2_level_id) if o2_level_id else False
                observation['values']['o2_target'] = o2_level.name if o2_level else False
                observation['triggered_actions'] = [v for v in activity_pool.read(cr, uid, triggered_actions_ids) if v['data_model'] != 'nh.clinical.patient.observation.ews']
                for t in observation['triggered_actions']:
                    t['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(t['date_started'], dtf), pretty_date_format) if t['date_started'] else False
                    t['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(t['date_terminated'], dtf), pretty_date_format) if t['date_terminated'] else False

            #
            # # convert the obs into usable obs for table & report
            json_ews = self.get_model_data_as_json([v['values'] for v in copy.deepcopy(ews)])
            table_ews = [v['values'] for v in ews]
            for table_ob in table_ews:
                table_ob['date_terminated'] = datetime.strftime(datetime.strptime(table_ob['date_terminated'], dtf), pretty_date_format)


            # Get the script files to load
            observation_report = '/nh_eobs/static/src/js/observation_report.js'

            #
            # # get height observations
            heights = self.get_model_data(spell_activity_id,
                                          'nh.clinical.patient.observation.height',
                                          start_time, end_time)
            patient['height'] = heights[-1]['values']['height'] if len(heights) > 0 else False

            # get weight observations
            weights = self.get_model_data(spell_activity_id,
                                          'nh.clinical.patient.observation.weight',
                                          start_time, end_time)
            patient['weight'] = weights[-1]['values']['weight'] if len(weights) > 0 else False

            if hasattr(data, 'ews_only') and data.ews_only:
                docargs = {
                    'doc_ids': self._ids,
                    'doc_model': report.model,
                    'docs': self,
                    'spell': spell,
                    'patient': patient,
                    'ews': ews,
                    'table_ews': table_ews,
                    'weights': weights,
                    'pbps': [],
                    'gcs': [],
                    'bs': [],
                    'bristol_stools': [],
                    'pains':[],
                    'blood_products': [],
                    'targeto2': [],
                    'device_session_history': [],
                    'mrsa_history': [],
                    'diabetes_history': [],
                    'palliative_care_history': [],
                    'post_surgery_history': [],
                    'critical_care_history': [],
                    'transfer_history': [],
                    'report_start': report_start,
                    'report_end': report_end,
                    'spell_start': spell_start,
                    'company_logo': company_logo,
                    'time_generated': time_generated,
                    'hospital_name': company_name,
                    'user_name': user,
                    'ews_data': json_ews,
                    'draw_graph_js': observation_report
                }
                return report_obj.render('nh_eobs.observation_report', docargs)


            # get pain observations
            pains = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.pain',
                                         start_time, end_time)
            # get blood_product observations
            blood_products = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.blood_product',
                                         start_time, end_time)
            # get bristol_stool observations
            bristol_stools = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.stools',
                                         start_time, end_time)
            for observation in bristol_stools:
                observation['values']['bowel_open'] = 'Yes' if observation['values']['bowel_open'] else 'No'
                observation['values']['vomiting'] = 'Yes' if observation['values']['vomiting'] else 'No'
                observation['values']['nausea'] = 'Yes' if observation['values']['nausea'] else 'No'
                observation['values']['strain'] = 'Yes' if observation['values']['strain'] else 'No'
                observation['values']['offensive'] = 'Yes' if observation['values']['offensive'] else 'No'
                observation['values']['laxatives'] = 'Yes' if observation['values']['laxatives'] else 'No'
                observation['values']['rectal_exam'] = 'Yes' if observation['values']['rectal_exam'] else 'No'
            # # get PBP observations
            pbps = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.pbp',
                                         start_time, end_time)
            # # get GCS observations
            gcss = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.gcs',
                                         start_time, end_time)
            # # get BS observations
            bss = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.observation.blood_sugar',
                                         start_time, end_time)
            # # get o2 target history

            oxygen_history = self.get_model_data(spell_activity_id,
                                                 'nh.clinical.patient.o2target',
                                                 start_time, end_time)
            # # get Device Session history
            device_session_history = self.get_multi_model_data(spell_activity_id,
                                                               'nh.clinical.patient.o2target',
                                                               'nh.clinical.device.session',
                                                               start_time, end_time)
              #
            # # get MRSA flag history
            mrsa_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.mrsa',
                                         start_time, end_time)
            # # get diabetes flag history
            diabetes_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.diabetes',
                                         start_time, end_time)
            # # get palliative_care flag history
            palliative_care_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.palliative_care',
                                         start_time, end_time)
            # # get post_surgery flag history
            post_surgery_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.post_surgery',
                                         start_time, end_time)
            # # get critical_care flag history
            critical_care_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.critical_care',
                                         start_time, end_time)
            # # get transfer history
            transfer_history = self.get_model_data(spell_activity_id,
                                         'nh.clinical.patient.move',
                                         start_time, end_time)
            for observation in transfer_history:
                patient_location = location_pool.read(cr, uid, observation['values']['location_id'][0], [])
                if patient_location:
                    observation['bed'] = patient_location['name'] if patient_location['name'] else False
                    observation['ward'] = patient_location['parent_id'][1] if patient_location['parent_id'] else False
            if transfer_history:
                patient['bed'] = transfer_history[-1]['bed'] if transfer_history[-1]['bed'] else False
                patient['ward'] = transfer_history[-1]['ward'] if transfer_history[-1]['ward'] else False


            docargs = {
                'doc_ids': self._ids,
                'doc_model': report.model,
                'docs': self,
                'spell': spell,
                'patient': patient,
                'ews': ews,
                'table_ews': table_ews,
                'weights': weights,
                'pbps': pbps,
                'gcs': gcss,
                'bs': bss,
                'bristol_stools': bristol_stools,
                'pains': pains,
                'blood_products': blood_products,
                'targeto2': oxygen_history,
                'device_session_history': device_session_history,
                'mrsa_history': mrsa_history,
                'diabetes_history': diabetes_history,
                'palliative_care_history': palliative_care_history,
                'post_surgery_history': post_surgery_history,
                'critical_care_history': critical_care_history,
                'transfer_history': transfer_history,
                'report_start': report_start,
                'report_end': report_end,
                'spell_start': spell_start,
                'company_logo': company_logo,
                'time_generated': time_generated,
                'hospital_name': company_name,
                'user_name': user,
                'ews_data': json_ews,
                'draw_graph_js': observation_report
            }
            return report_obj.render('nh_eobs.observation_report', docargs)
        else:
            return None