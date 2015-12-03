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

    @api.multi
    def render_html(self, data=None):
        cr, uid = self._cr, self._uid
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh.clinical.observation_report')
        pretty_date_format = '%H:%M %d/%m/%y'
        wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"

        if isinstance(data, dict):
            data = self.data_dict_to_obj(data)

        # set up data
        start_time = datetime.strptime(data.start_time, dtf) if data and data.start_time else False
        end_time = datetime.strptime(data.end_time, dtf) if data and data.end_time else False

        # set up pools
        activity_pool = self.pool['nh.activity']
        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        pain_pool = self.pool['nh.clinical.patient.observation.pain']
        blood_product_pool = self.pool['nh.clinical.patient.observation.blood_product']
        bristol_stool_pool = self.pool['nh.clinical.patient.observation.stools']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        weight_pool = self.pool['nh.clinical.patient.observation.weight']
        height_pool = self.pool['nh.clinical.patient.observation.height']
        pbp_pool = self.pool['nh.clinical.patient.observation.pbp']
        gcs_pool = self.pool['nh.clinical.patient.observation.gcs']
        bs_pool = self.pool['nh.clinical.patient.observation.blood_sugar']
        oxygen_target_pool = self.pool['nh.clinical.patient.o2target']
        transfer_history_pool = self.pool['nh.clinical.patient.move']
        company_pool = self.pool['res.company']
        partner_pool = self.pool['res.partner']
        user_pool = self.pool['res.users']
        location_pool = self.pool['nh.clinical.location']
        o2_level_pool = self.pool['nh.clinical.o2level']
        device_session_pool = self.pool['nh.clinical.device.session']
        mrsa_pool = self.pool['nh.clinical.patient.mrsa']
        diabetes_pool = self.pool['nh.clinical.patient.diabetes']
        palliative_care_pool = self.pool['nh.clinical.patient.palliative_care']
        post_surgery_pool = self.pool['nh.clinical.patient.post_surgery']
        critical_care_pool = self.pool['nh.clinical.patient.critical_care']

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
                o2_level_id = oxygen_target_pool.get_last(cr, uid, patient_id, observation['values']['date_terminated'])
                o2_level = o2_level_pool.browse(cr, uid, o2_level_id) if o2_level_id else False
                observation['values']['o2_target'] = o2_level.name if o2_level else False
                observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), dtf) if observation['values']['date_started'] else False
                observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), dtf) if observation['values']['date_terminated'] else False
                observation['triggered_actions'] = [v for v in activity_pool.read(cr, uid, triggered_actions_ids) if v['data_model'] != 'nh.clinical.patient.observation.ews']
                for t in observation['triggered_actions']:
                    t['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(t['date_started'], dtf), pretty_date_format) if t['date_started'] else False
                    t['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(t['date_terminated'], dtf), pretty_date_format) if t['date_terminated'] else False

            #
            # # convert the obs into usable obs for table & report
            ews_for_json = copy.deepcopy(ews)
            json_obs = [v['values'] for v in ews_for_json]
            table_ews = [v['values'] for v in ews]
            for table_ob in table_ews:
                table_ob['date_terminated'] = datetime.strftime(datetime.strptime(table_ob['date_terminated'], dtf), pretty_date_format)
            for json_ob in json_obs:
                json_ob['write_date'] = datetime.strftime(datetime.strptime(json_ob['write_date'], dtf), wkhtmltopdf_format)
                json_ob['create_date'] = datetime.strftime(datetime.strptime(json_ob['create_date'], dtf), wkhtmltopdf_format)
                json_ob['date_started'] = datetime.strftime(datetime.strptime(json_ob['date_started'], dtf), wkhtmltopdf_format)
                json_ob['date_terminated'] = datetime.strftime(datetime.strptime(json_ob['date_terminated'], dtf), wkhtmltopdf_format)
            json_ews = json.dumps(json_obs)

            # Get the script files to load
            observation_report = '/nh_eobs/static/src/js/observation_report.js'

            #
            # # get height observations
            # # - search height model with parent_id of spell - dates
            height_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.height', start_time, end_time))
            heights = activity_pool.read(cr, uid, height_ids)
            for observation in heights:
                observation['values'] = height_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            patient['height'] = heights[-1]['values']['height'] if len(heights) > 0 else False

            # get weight observations
            # - search weight model with parent_id of spell - dates
            weight_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.weight', start_time, end_time))
            weights = activity_pool.read(cr, uid, weight_ids)
            for observation in weights:
                observation['values'] = weight_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
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
            # - search pain model with parent_id of spell - dates
            pain_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.pain', start_time, end_time))
            pains = activity_pool.read(cr, uid, pain_ids)
            for observation in pains:
                observation['values'] = pain_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            # get blood_product observations
            # - search blood_product model with parent_id of spell - dates
            blood_product_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.blood_product', start_time, end_time))
            blood_products = activity_pool.read(cr, uid, blood_product_ids)
            for observation in blood_products:
                observation['values'] = blood_product_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            # get bristol_stool observations
            # - search bristol_stool model with parent_id of spell - dates
            bristol_stool_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.stools', start_time, end_time))
            bristol_stools = activity_pool.read(cr, uid, bristol_stool_ids)
            for observation in bristol_stools:
                observation['values'] = bristol_stool_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['bowel_open'] = 'Yes' if observation['values']['bowel_open'] else 'No'
                    observation['values']['vomiting'] = 'Yes' if observation['values']['vomiting'] else 'No'
                    observation['values']['nausea'] = 'Yes' if observation['values']['nausea'] else 'No'
                    observation['values']['strain'] = 'Yes' if observation['values']['strain'] else 'No'
                    observation['values']['offensive'] = 'Yes' if observation['values']['offensive'] else 'No'
                    observation['values']['laxatives'] = 'Yes' if observation['values']['laxatives'] else 'No'
                    observation['values']['rectal_exam'] = 'Yes' if observation['values']['rectal_exam'] else 'No'
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False

            #
            # # get PBP observations
            # # - search pbp model with parent_id of spell - dates
            pbp_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.pbp', start_time, end_time))
            pbps = activity_pool.read(cr, uid, pbp_ids)
            for observation in pbps:
                observation['values'] = pbp_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
            #
            # # get GCS observations
            # # - search gcs model with parent_id of spell - dates
            gcs_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.gcs', start_time, end_time))
            gcss = activity_pool.read(cr, uid, gcs_ids)
            for observation in gcss:
                observation['values'] = gcs_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
            #
            # # get BS observations
            # # - search bs model with parent_id of spell - dates
            bs_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.blood_sugar', start_time, end_time))
            bss = activity_pool.read(cr, uid, bs_ids)
            for observation in bss:
                observation['values'] = bs_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
            #
            # # get o2 target history
            # # - search o2target model on patient with parent_id of spell - dates
            oxygen_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.o2target', start_time, end_time))
            oxygen_history = activity_pool.read(cr, uid, oxygen_history_ids)
            for observation in oxygen_history:
                observation['values'] = oxygen_target_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format) if observation['values']['date_terminated'] else False
            #
            # # get Device Session history
            # # - search device session model on patient with parent_id of spell - dates
            device_session_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.o2target', start_time, end_time))
            device_session_history = activity_pool.read(cr, uid, device_session_history_ids)
            for device_session in device_session_history:
                device_session['values'] = device_session_pool.read(cr, uid, int(device_session['data_ref'].split(',')[1]), [])
                if device_session['values']:
                    device_session['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(device_session['values']['date_started'], dtf), pretty_date_format) if device_session['values']['date_started'] else False
                    device_session['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(device_session['values']['date_terminated'], dtf), pretty_date_format) if device_session['values']['date_terminated'] else False
            #
            # # get MRSA flag history
            # # - search mrsa model on patient with parent_id of spell - dates
            mrsa_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.mrsa', start_time, end_time))
            mrsa_history = activity_pool.read(cr, uid, mrsa_history_ids)
            for mrsa in mrsa_history:
                mrsa['values'] = mrsa_pool.read(cr, uid, int(mrsa['data_ref'].split(',')[1]), [])
                if mrsa['values']:
                    mrsa['values']['mrsa'] = 'Yes' if mrsa['values']['status'] else 'No'
                    mrsa['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(mrsa['values']['date_started'], dtf), pretty_date_format) if mrsa['values']['date_started'] else False
                    mrsa['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(mrsa['values']['date_terminated'], dtf), pretty_date_format) if mrsa['values']['date_terminated'] else False
            #
            # # get diabetes flag history
            # # - search diabetes model on patient with parent_id of spell - dates
            diabetes_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.diabetes', start_time, end_time))
            diabetes_history = activity_pool.read(cr, uid, diabetes_history_ids)
            for diabetes in diabetes_history:
                diabetes['values'] = diabetes_pool.read(cr, uid, int(diabetes['data_ref'].split(',')[1]), [])
                if diabetes['values']:
                    diabetes['values']['diabetes'] = 'Yes' if diabetes['values']['status'] else 'No'
                    diabetes['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(diabetes['values']['date_started'], dtf), pretty_date_format) if diabetes['values']['date_started'] else False
                    diabetes['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(diabetes['values']['date_terminated'], dtf), pretty_date_format) if diabetes['values']['date_terminated'] else False
            #
            # # get palliative_care flag history
            # # - search palliative_care model on patient with parent_id of spell - dates
            palliative_care_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.palliative_care', start_time, end_time))
            palliative_care_history = activity_pool.read(cr, uid, palliative_care_history_ids)
            for palliative_care in palliative_care_history:
                palliative_care['values'] = palliative_care_pool.read(cr, uid, int(palliative_care['data_ref'].split(',')[1]), [])
                if palliative_care['values']:
                    palliative_care['values']['palliative_care'] = 'Yes' if palliative_care['values']['status'] else 'No'
                    palliative_care['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(palliative_care['values']['date_started'], dtf), pretty_date_format) if palliative_care['values']['date_started'] else False
                    palliative_care['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(palliative_care['values']['date_terminated'], dtf), pretty_date_format) if palliative_care['values']['date_terminated'] else False
            #
            # # get post_surgery flag history
            # # - search post_surgery model on patient with parent_id of spell - dates
            post_surgery_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.post_surgery', start_time, end_time))
            post_surgery_history = activity_pool.read(cr, uid, post_surgery_history_ids)
            for post_surgery in post_surgery_history:
                post_surgery['values'] = post_surgery_pool.read(cr, uid, int(post_surgery['data_ref'].split(',')[1]), [])
                if post_surgery['values']:
                    post_surgery['values']['post_surgery'] = 'Yes' if post_surgery['values']['status'] else 'No'
                    post_surgery['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(post_surgery['values']['date_started'], dtf), pretty_date_format) if post_surgery['values']['date_started'] else False
                    post_surgery['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(post_surgery['values']['date_terminated'], dtf), pretty_date_format) if post_surgery['values']['date_terminated'] else False
            #
            # # get critical_care flag history
            # # - search critical_care model on patient with parent_id of spell - dates
            critical_care_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.critical_care', start_time, end_time))
            critical_care_history = activity_pool.read(cr, uid, critical_care_history_ids)
            for critical_care in critical_care_history:
                critical_care['values'] = critical_care_pool.read(cr, uid, int(critical_care['data_ref'].split(',')[1]), [])
                if critical_care['values']:
                    critical_care['values']['critical_care'] = 'Yes' if critical_care['values']['status'] else 'No'
                    critical_care['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(critical_care['values']['date_started'], dtf), pretty_date_format) if critical_care['values']['date_started'] else False
                    critical_care['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(critical_care['values']['date_terminated'], dtf), pretty_date_format) if critical_care['values']['date_terminated'] else False
            #
            # # get transfer history
            # # - search move on patient with parent_id of spell - dates
            transfer_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.move', start_time, end_time))
            transfer_history = activity_pool.read(cr, uid, transfer_history_ids)
            for observation in transfer_history:
                observation['values'] = transfer_history_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_started'], dtf), pretty_date_format) if observation['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(datetime.strptime(observation['date_terminated'], dtf), pretty_date_format) if observation['date_terminated'] else False
                    patient_location = location_pool.read(cr, uid, observation['values']['location_id'][0], [])
                    if patient_location:
                        observation['bed'] = patient_location['name'] if patient_location['name'] else False
                        observation['ward'] = patient_location['parent_id'][1] if patient_location['parent_id'] else False
            if len(transfer_history) > 0:
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