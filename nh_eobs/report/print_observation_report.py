# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
from openerp import api, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import fields
import json
import copy
from . import helpers


class ObservationReport(models.AbstractModel):
    _name = 'report.nh.clinical.observation_report'

    pretty_date_format = '%H:%M %d/%m/%y'
    wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"
    patient_id = None

    def get_activity_data(self, spell_id, model, start_time, end_time):
        cr, uid = self._cr, self._uid
        act_pool = self.pool['nh.activity']
        activity_ids = act_pool.search(cr, uid,
                                       helpers.create_search_filter(
                                           spell_id,
                                           model, start_time, end_time))
        return act_pool.read(cr, uid, activity_ids)

    def get_model_data(self, spell_id, model, start, end):
        cr, uid = self._cr, self._uid
        act_data = self.get_activity_data(spell_id, model, start, end)
        if act_data:
            for act in act_data:
                ds = False
                dt = False
                if 'date_started' in act and act['date_started']:
                    ds = act['date_started']
                if 'date_terminated' in act and act['date_terminated']:
                    dt = act['date_terminated']
                if ds:
                    ds = helpers.convert_db_date_to_context_date(
                        cr, uid, datetime.strptime(ds, dtf),
                        self.pretty_date_format)
                    act['date_started'] = ds
                if dt:
                    dt = helpers.convert_db_date_to_context_date(
                        cr, uid, datetime.strptime(dt, dtf),
                        self.pretty_date_format)
                    act['date_terminated'] = dt
        return self.get_model_values(model, act_data)

    def get_model_values(self, model, act_data):
        cr, uid = self._cr, self._uid
        model_pool = self.pool[model]
        for act in act_data:
            model_data = model_pool.read(cr, uid,
                                         int(act['data_ref'].split(',')[1]),
                                         [])
            if model_data:
                stat = 'No'
                dt = 'date_terminated'
                if 'status' in model_data and model_data['status']:
                    stat = 'Yes'
                    model_data['status'] = stat
                if 'date_started' in model_data and model_data['date_started']:
                    model_data['date_started'] = \
                        helpers.convert_db_date_to_context_date(
                            cr, uid,
                            datetime.strptime(
                                model_data['date_started'],
                                dtf
                            ),
                            self.pretty_date_format
                        )
                if dt in model_data and model_data[dt]:
                    model_data['date_terminated'] = \
                        helpers.convert_db_date_to_context_date(
                            cr, uid,
                            datetime.strptime(
                                model_data['date_terminated'],
                                dtf
                            ),
                            self.pretty_date_format
                        )
            act['values'] = model_data
        return act_data

    def get_multi_model_data(self, spell_id,
                             model_one, model_two,  start, end):
        act_data = self.get_activity_data(spell_id, model_one, start, end)
        return self.get_model_values(model_two, act_data)

    def get_model_data_as_json(self, model_data):
        for data in model_data:
            data['write_date'] = datetime.strftime(
                datetime.strptime(data['write_date'], dtf),
                self.wkhtmltopdf_format
            )
            data['create_date'] = datetime.strftime(
                datetime.strptime(data['create_date'], dtf),
                self.wkhtmltopdf_format
            )
            data['date_started'] = datetime.strftime(
                datetime.strptime(
                    data['date_started'],
                    self.pretty_date_format
                ),
                self.wkhtmltopdf_format
            )
            data['date_terminated'] = datetime.strftime(
                datetime.strptime(
                    data['date_terminated'],
                    self.pretty_date_format
                ),
                self.wkhtmltopdf_format
            )
        return json.dumps(model_data)

    def create_report_data(self, data):
        cr, uid = self._cr, self._uid
        pretty_date_format = self.pretty_date_format

        # set up pools
        company_pool = self.pool['res.company']
        partner_pool = self.pool['res.partner']
        user_pool = self.pool['res.users']

        # get user data
        user = user_pool.read(cr, uid, uid, ['name'])['name']

        # get company data
        company_name = company_pool.read(cr, uid, 1, ['name'])['name']
        company_logo = partner_pool.read(cr, uid, 1, ['image'])['image']

        # generate report timestamp
        time_generated = fields.datetime.context_timestamp(
            cr, uid,
            datetime.now(),
            context=None
        ).strftime(pretty_date_format)
        return helpers.BaseReport(
            user,
            company_name,
            company_logo,
            time_generated
        )

    def get_ews_observations(self, data):
        cr, uid = self._cr, self._uid
        ews_model = 'nh.clinical.patient.observation.ews'
        ews = self.get_model_data(data.spell_id,
                                  ews_model,
                                  data.start_time, data.end_time)
        for observation in ews:
            triggered_actions_ids = self.pool['nh.activity'].search(
                cr, uid, [['creator_id', '=', observation['id']]])
            o2_level_id = self.pool['nh.clinical.patient.o2target'].get_last(
                cr, uid, self.patient_id,
                observation['values']['date_terminated'])
            o2_level = False
            if o2_level_id:
                o2_level = self.pool['nh.clinical.o2level'].browse(
                    cr, uid, o2_level_id)
            observation['values']['o2_target'] = False
            if o2_level:
                observation['values']['o2_target'] = o2_level.name
            triggered_actions = []
            for activity in self.pool['nh.activity'].read(
                    cr, uid, triggered_actions_ids):
                if activity['data_model'] != ews_model:
                    triggered_actions.append(activity)
            observation['triggered_actions'] = triggered_actions
            for t in observation['triggered_actions']:
                ds = t.get('date_started', False)
                dt = t.get('date_terminated', False)
                if ds:
                    t['date_started'] = \
                        helpers.convert_db_date_to_context_date(
                            cr, uid,
                            datetime.strptime(t['date_started'], dtf),
                            self.pretty_date_format
                        )
                if dt:
                    t['date_terminated'] = \
                        helpers.convert_db_date_to_context_date(
                            cr, uid,
                            datetime.strptime(t['date_terminated'], dtf),
                            self.pretty_date_format
                        )
        return ews

    @staticmethod
    def convert_bristol_stools_booleans(model_data):
        for ob in model_data:
            vals = ob['values']
            vals['bowel_open'] = helpers.boolean_to_text(vals['bowel_open'])
            vals['vomiting'] = helpers.boolean_to_text(vals['vomiting'])
            vals['nausea'] = helpers.boolean_to_text(vals['nausea'])
            vals['strain'] = helpers.boolean_to_text(vals['strain'])
            vals['offensive'] = helpers.boolean_to_text(vals['offensive'])
            vals['laxatives'] = helpers.boolean_to_text(vals['laxatives'])
            vals['rectal_exam'] = helpers.boolean_to_text(vals['rectal_exam'])
        return model_data

    @staticmethod
    def convert_pbp_booleans(model_data):
        for ob in model_data:
            vals = ob['values']
            vals['result'] = helpers.boolean_to_text(vals['result'])
        return model_data

    @staticmethod
    def convert_device_session_booleans(model_data):
        for ob in model_data:
            vals = ob['values']
            vals['planned'] = helpers.boolean_to_text(vals['planned'])
        return model_data

    def process_transfer_history(self, model_data):
        for observation in model_data:
                patient_location = self.pool['nh.clinical.location'].read(
                    self._cr,
                    self._uid,
                    observation['values']['location_id'][0], [])
                if patient_location:
                    observation['bed'] = patient_location.get('name', False)
                    ward = patient_location.get('parent_id', False)
                if ward:
                    observation['ward'] = ward[1]
        return model_data

    def process_report_dates(self, data, spell, base_report):
        start_time = False
        end_time = False
        if data.start_time:
            start_time = datetime.strptime(data.start_time, dtf)
            data.start_time = start_time
        if data.end_time:
            end_time = datetime.strptime(data.end_time, dtf)
            data.end_time = end_time

        # - get the start and end date of spell
        spell_start = helpers.convert_db_date_to_context_date(
            self._cr, self._uid, datetime.strptime(spell['date_started'], dtf),
            self.pretty_date_format, context=None)
        spell_end = spell['date_terminated']
        report_start = spell_start
        report_end = base_report.time_generated
        if start_time:
            report_start = start_time.strftime(self.pretty_date_format)
        if end_time:
            report_end = end_time.strftime(self.pretty_date_format)
        else:
            if spell_end:
                report_end = helpers.convert_db_date_to_context_date(
                    self._cr, self._uid, datetime.strptime(spell_end, dtf),
                    self.pretty_date_format,
                    context=None)
        return helpers.ReportDates(
            report_start,
            report_end,
            spell_start,
            spell_end
        )

    def get_activity_data_from_dict(self, dict, spell_id, data):
        for k, v in dict.iteritems():
            dict[k] = self.get_model_data(
                spell_id, v, data.start_time, data.end_time)
        return dict

    @staticmethod
    def process_patient_height_weight(patient, height_weight):
        heights = height_weight['height']
        height = False
        if len(heights) > 0:
            height = heights[-1]['values']['height']
        patient['height'] = height

        # get weight observations
        weights = height_weight['weight']
        weight = False
        if len(weights) > 0:
            weight = weights[-1]['values']['weight']
        patient['weight'] = weight
        return patient

    def get_report_data(self, data, ews_only=False):
        cr, uid = self._cr, self._uid
        # set up pools
        report = self.env['report']._get_report_from_name(
            'nh.clinical.observation_report')
        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        partner_pool = self.pool['res.partner']
        base_report = self.create_report_data(data)
        spell_id = int(data.spell_id)
        spell = spell_pool.read(cr, uid, [spell_id])[0]
        dates = self.process_report_dates(data, spell, base_report)
        spell_activity_id = spell['activity_id'][0]

        spell_docs = spell['con_doctor_ids']
        spell['consultants'] = False
        if len(spell_docs) > 0:
            spell['consultants'] = partner_pool.read(cr, uid, spell_docs)
        #
        # # - get patient id
        self.patient_id = spell['patient_id'][0]
        patient_id = self.patient_id
        #
        # get patient information
        patient = patient_pool.read(cr, uid, [patient_id])[0]
        patient['dob'] = helpers.convert_db_date_to_context_date(
            cr, uid, datetime.strptime(patient['dob'], dtf),
            '%d/%m/%Y', context=None)
        ews = self.get_ews_observations(data)
        json_data = []
        table_ews = []
        for activity in ews:
            json_data.append(copy.deepcopy(activity['values']))
            table_ews.append(copy.deepcopy(activity['values']))
        json_ews = self.get_model_data_as_json(json_data)

        # Get the script files to load
        observation_report = '/nh_eobs/static/src/js/observation_report.js'

        height_weight_dict = {
            'height': 'nh.clinical.patient.observation.height',
            'weight': 'nh.clinical.patient.observation.weight'
        }
        height_weight = self.get_activity_data_from_dict(
            height_weight_dict,
            spell_activity_id,
            data
        )
        patient = self.process_patient_height_weight(patient, height_weight)

        monitoring_dict = {
            'targeto2': 'nh.clinical.patient.o2target',
            'mrsa_history': 'nh.clinical.patient.mrsa',
            'diabetes_history': 'nh.clinical.patient.diabetes',
            'palliative_care_history': 'nh.clinical.patient.palliative_care',
            'post_surgery_history': 'nh.clinical.patient.post_surgery',
            'critical_care_history': 'nh.clinical.patient.critical_care'
        }

        monitoring = self.get_activity_data_from_dict(
            monitoring_dict,
            spell_activity_id,
            data
        )

        transfer_history = self.process_transfer_history(
            self.get_model_data(
                spell_activity_id,
                'nh.clinical.patient.move',
                data.start_time, data.end_time)
        )
        if transfer_history:
            th = transfer_history[-1]
            patient['bed'] = th.get('bed',  False)
            patient['ward'] = th.get('ward',  False)

        device_session_history = self.convert_device_session_booleans(
            self.get_multi_model_data(
                spell_activity_id,
                'nh.clinical.patient.o2target',
                'nh.clinical.device.session',
                data.start_time, data.end_time
            )
        )

        ews_dict = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'spell': spell,
            'patient': patient,
            'ews': ews,
            'table_ews': table_ews,
            'report_start': dates.report_start,
            'report_end': dates.report_end,
            'spell_start': dates.spell_start,
            'ews_data': json_ews,
            'draw_graph_js': observation_report,
            'device_session_history': device_session_history,
            'transfer_history': transfer_history,
        }

        ews_report = helpers.merge_dicts(ews_dict,
                                         base_report.footer_values,
                                         monitoring)
        if ews_only:
            return ews_report

        basic_obs_dict = {
            'gcs': 'nh.clinical.patient.observation.gcs',
            'bs': 'nh.clinical.patient.observation.blood_sugar',
            'pains': 'nh.clinical.patient.observation.pain',
            'blood_products': 'nh.clinical.patient.observation.blood_product'
        }

        basic_obs = self.get_activity_data_from_dict(
            basic_obs_dict,
            spell_activity_id,
            data
        )

        pbps = self.convert_pbp_booleans(
            self.get_model_data(
                spell_activity_id,
                'nh.clinical.patient.observation.pbp',
                data.start_time, data.end_time)
        )

        bristol_stools = self.convert_bristol_stools_booleans(
            self.get_model_data(
                spell_activity_id,
                'nh.clinical.patient.observation.stools',
                data.start_time, data.end_time))

        weights = height_weight['weight']

        non_basic_obs = {
            'bristol_stools': bristol_stools,
            'weights': weights,
            'pbps': pbps
        }

        rep_data = helpers.merge_dicts(
            basic_obs,
            non_basic_obs,
            ews_report
        )
        return rep_data

    @api.multi
    def render_html(self, data=None):

        if isinstance(data, dict):
            data = helpers.data_dict_to_obj(data)

        if data and data.spell_id:
            report_obj = self.env['report']
            if hasattr(data, 'ews_only') and data.ews_only:
                ews_report = self.get_report_data(data, ews_only=True)
                return report_obj.render('nh_eobs.observation_report',
                                         ews_report)
            rep_data = self.get_report_data(data)
            return report_obj.render(
                'nh_eobs.observation_report',
                rep_data)
        else:
            return None
