# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
from openerp import api, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.osv import fields
import json
import copy


class DataObj(object):
    def __init__(self,
                 spell_id=None,
                 start_time=None,
                 end_time=None,
                 ews_only=None):
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
        if model in ['nh.clinical.patient.o2target',
                     'nh.clinical.patient.move']:
            sfilter = [['parent_id', '=', spell_activity_id],
                      ['data_model', '=', model]]
        else:
            sfilter = [
                ['parent_id', '=', spell_activity_id],
                ['data_model', '=', model],
                ['state', '=', 'completed']
            ]
        if start_date:
            sfilter.append(['date_started', '>=', start_date.strftime(dtf)])
        if end_date:
            sfilter.append(['date_terminated', '<=', end_date.strftime(dtf)])
        return sfilter

    def convert_db_date_to_context_date(self, cr, uid, date_string, format,
                                        context=None):
        if format:
            return fields.datetime.context_timestamp(
                cr, uid, date_string, context=context).strftime(format)
        else:
            return fields.datetime.context_timestamp(
                cr, uid, date_string, context=context)

    @staticmethod
    def data_dict_to_obj(data_dict):
        has_spell = 'spell_id' in data_dict and data_dict['spell_id']
        has_start = 'start_time' in data_dict and data_dict['start_time']
        has_end = 'end_time' in data_dict and data_dict['end_time']
        has_ews = 'ews_only' in data_dict and data_dict['ews_only']
        spell_id = data_dict['spell_id'] if has_spell else None
        start = data_dict['start_time'] if has_start else None
        end = data_dict['end_time'] if has_end else None
        ews_only = data_dict['ews_only'] if has_ews else None
        return DataObj(spell_id, start, end, ews_only)

    @api.multi
    def render_html(self, data=None):
        cr, uid = self._cr, self._uid
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'nh.clinical.observation_report')
        pretty_date_format = '%H:%M %d/%m/%y'
        wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"

        if isinstance(data, dict):
            data = self.data_dict_to_obj(data)

        # set up data
        start_time = False
        end_time = False
        if data and data.start_time:
            start_time = datetime.strptime(data.start_time, dtf)
        if data and data.end_time
            end_time = datetime.strptime(data.end_time, dtf)

        # set up pools
        activity_pool = self.pool['nh.activity']
        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        pain_pool = self.pool['nh.clinical.patient.observation.pain']
        blood_product_pool = \
            self.pool['nh.clinical.patient.observation.blood_product']
        bristol_stool_pool = \
            self.pool['nh.clinical.patient.observation.stools']
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
        user = user_pool.read(cr, uid, uid, ['name'], context=None)['name']

        # get company data
        company_name = company_pool.read(cr, uid, 1, ['name'])['name']
        company_logo = partner_pool.read(cr, uid, 1, ['image'])['image']

        # generate report timestamp
        time_generated = fields.datetime.context_timestamp(
            cr, uid, datetime.now(), context=None).strftime(pretty_date_format)

        if data and data.spell_id:
            spell_id = int(data.spell_id)
            spell = spell_pool.read(cr, uid, [spell_id])[0]
            # - get the start and end date of spell
            spell_start = self.convert_db_date_to_context_date(
                datetime.strptime(spell['date_started'], dtf),
                pretty_date_format, context=None)
            spell_end = spell['date_terminated']
            report_start = spell_start
            report_end = time_generated
            if start_time:
                report_start = start_time.strftime(pretty_date_format)
            if end_time:
                report_end = end_time.strftime(pretty_date_format)
            else:
                if spell_end:
                    report_end = self.convert_db_date_to_context_date(
                        datetime.strptime(spell_end, dtf),
                        pretty_date_format, context=None)
            spell_activity_id = spell['activity_id'][0]
            consults = False
            if len(spell['con_doctor_ids']) > 0:
                consults = partner_pool.read(
                    cr, uid, spell['con_doctor_ids'])
            spell['consultants'] = consults
            # - get patient id
            patient_id = spell['patient_id'][0]
            # get patient information
            patient = patient_pool.read(cr, uid, [patient_id])[0]
            patient['dob'] = self.convert_db_date_to_context_date(
                datetime.strptime(patient['dob'], dtf),
                '%d/%m/%Y', context=None)
            # get ews observations for patient
            # search ews model with parent_id of spell id
            # (maybe dates for refined foo) - activity: search
            # with data_model of ews
            ews_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.ews',
                    start_time, end_time
                )
            )
            ews = activity_pool.read(cr, uid, ews_ids)

            # get triggered actions from ews
            # - search activity with ews ids as creator_id filter out EWS tasks
            for observation in ews:
                observation['date_started'] = \
                    self.convert_db_date_to_context_date(
                        datetime.strptime(
                            observation['date_started'], dtf
                        ), pretty_date_format
                    )
                dt = False
                if observation['date_terminated']:
                    dt = self.convert_db_date_to_context_date(
                        datetime.strptime(
                            observation['date_terminated'], dtf
                        ), pretty_date_format
                    )
                observation['date_terminated'] = dt
                triggered_actions_ids = activity_pool.search(
                    cr, uid, [['creator_id', '=', observation['id']]])
                observation['values'] = ews_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                o2_level_id = oxygen_target_pool.get_last(
                    cr, uid, patient_id,
                    observation['values']['date_terminated'])
                o2_level = False
                if o2_level_id:
                    o2_level = o2_level_pool.browse(cr, uid, o2_level_id)
                o2_target = False
                if o2_level:
                    o2_target = o2_level.name
                ob_vals = observation['values']
                ob_vals['o2_target'] = o2_target
                ds = False
                dt = False
                if ob_vals['date_started']:
                    ds = self.convert_db_date_to_context_date(
                        datetime.strptime(ob_vals['date_started'], dtf), dtf)
                ob_vals['date_started'] = ds
                if ob_vals['date_terminated']:
                    dt = self.convert_db_date_to_context_date(
                        datetime.strptime(ob_vals['date_terminated'], dtf),
                        dtf)
                ob_vals['date_terminated'] = dt
                observation['values'] = ob_vals
                trig = []
                for act in activity_pool.read(cr, uid, triggered_actions_ids):
                    dm = act['data_model']
                    if dm != 'nh.clinical.patient.observation.ews':
                        trig.append(act)
                observation['triggered_actions'] = trig
                for t in observation['triggered_actions']:
                    tds = False
                    if t['date_started']:
                        tds = self.convert_db_date_to_context_date(
                            datetime.strptime(t['date_started'], dtf),
                            pretty_date_format)
                    tdt = False
                    if t['date_terminated']:
                        tdt = self.convert_db_date_to_context_date(
                            datetime.strptime(t['date_terminated'], dtf),
                            pretty_date_format)
                    t['date_started'] =  tds
                    t['date_terminated'] =  tdt

            # convert the obs into usable obs for table & report
            ews_for_json = copy.deepcopy(ews)
            json_obs = [v['values'] for v in ews_for_json]
            table_ews = [v['values'] for v in ews]
            for table_ob in table_ews:
                table_ob['date_terminated'] = datetime.strftime(
                    datetime.strptime(table_ob['date_terminated'], dtf),
                    pretty_date_format)
            for json_ob in json_obs:
                json_ob['write_date'] = datetime.strftime(
                    datetime.strptime(json_ob['write_date'], dtf),
                    wkhtmltopdf_format)
                json_ob['create_date'] = datetime.strftime(
                    datetime.strptime(json_ob['create_date'], dtf),
                    wkhtmltopdf_format)
                json_ob['date_started'] = datetime.strftime(
                    datetime.strptime(json_ob['date_started'], dtf),
                    wkhtmltopdf_format)
                json_ob['date_terminated'] = datetime.strftime(
                    datetime.strptime(json_ob['date_terminated'], dtf),
                    wkhtmltopdf_format)
            json_ews = json.dumps(json_obs)

            # Get the script files to load
            observation_report = '/nh_eobs/static/src/js/observation_report.js'

            # get height observations
            # search height model with parent_id of spell - dates
            height_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.height',
                    start_time, end_time
                )
            )
            heights = activity_pool.read(cr, uid, height_ids)
            for observation in heights:
                observation['values'] = height_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    ob_vals['date_started'] = ds
                    ob_vals['date_terminated'] = dt
                    observation['values'] = ob_vals
            ph = False
            if len(heights) > 0:
                ph = heights[-1]['values']['height']
            patient['height'] = ph

            # get weight observations
            # - search weight model with parent_id of spell - dates
            weight_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.weight',
                    start_time, end_time
                )
            )
            weights = activity_pool.read(cr, uid, weight_ids)
            for observation in weights:
                observation['values'] = weight_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            pw = False
            if len(weights) > 0:
                pw = weights[-1]['values']['weight']
            patient['weight'] = pw

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
            pain_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.pain',
                    start_time, end_time

                ))
            pains = activity_pool.read(cr, uid, pain_ids)
            for observation in pains:
                observation['values'] = pain_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get blood_product observations
            # - search blood_product model with parent_id of spell - dates
            blood_product_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.blood_product',
                    start_time, end_time
                )
            )
            blood_products = activity_pool.read(cr, uid, blood_product_ids)
            for observation in blood_products:
                observation['values'] = blood_product_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get bristol_stool observations
            # - search bristol_stool model with parent_id of spell - dates
            bristol_stool_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.stools',
                    start_time, end_time
                )
            )
            bristol_stools = activity_pool.read(cr, uid, bristol_stool_ids)
            for observation in bristol_stools:
                observation['values'] = bristol_stool_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    bo = 'bowel_open'
                    vom = 'vomiting'
                    off = 'offensive'
                    lax = 'laxatives'
                    rect = 'rectal_exam'
                    ob_vals[bo] = 'Yes' if ob_vals[bo] else 'No'
                    ob_vals[vom] = 'Yes' if ob_vals[vom] else 'No'
                    ob_vals['nausea'] = 'Yes' if ob_vals['nausea'] else 'No'
                    ob_vals['strain'] = 'Yes' if ob_vals['strain'] else 'No'
                    ob_vals[off] = 'Yes' if ob_vals[off] else 'No'
                    ob_vals[lax] = 'Yes' if ob_vals[lax] else 'No'
                    ob_vals[rect] = 'Yes' if ob_vals[rect] else 'No'
                    observation['values'] = ob_vals
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt

            # get PBP observations
            # search pbp model with parent_id of spell - dates
            pbp_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.pbp',
                    start_time, end_time
                )
            )
            pbps = activity_pool.read(cr, uid, pbp_ids)
            for observation in pbps:
                observation['values'] = pbp_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get GCS observations
            # search gcs model with parent_id of spell - dates
            gcs_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.gcs',
                    start_time, end_time
                )
            )
            gcss = activity_pool.read(cr, uid, gcs_ids)
            for observation in gcss:
                observation['values'] = gcs_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get BS observations
            # search bs model with parent_id of spell - dates
            bs_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.observation.blood_sugar',
                    start_time, end_time
                )
            )
            bss = activity_pool.read(cr, uid, bs_ids)
            for observation in bss:
                observation['values'] = bs_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get o2 target history
            # search o2target model on patient with parent_id of
            # spell - dates
            oxygen_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.o2target',
                    start_time, end_time
                )
            )
            oxygen_history = activity_pool.read(cr, uid, oxygen_history_ids)
            for observation in oxygen_history:
                observation['values'] = oxygen_target_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get Device Session history
            # search device session model on patient with parent_id of
            # spell - dates
            device_session_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.o2target',
                    start_time, end_time
                )
            )
            device_session_history = activity_pool.read(
                cr, uid, device_session_history_ids)
            for observation in device_session_history:
                observation['values'] = device_session_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get MRSA flag history
            # search mrsa model on patient with parent_id of spell - dates
            mrsa_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.mrsa',
                    start_time, end_time
                )
            )
            mrsa_history = activity_pool.read(cr, uid, mrsa_history_ids)
            for observation in mrsa_history:
                observation['values'] = mrsa_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    stat = ob_vals['status']
                    observation['values']['mrsa'] = 'Yes' if stat else 'No'
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get diabetes flag history
            # search diabetes model on patient with parent_id of spell
            # dates
            diabetes_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.diabetes',
                    start_time, end_time
                )
            )
            diabetes_history = activity_pool.read(
                cr, uid, diabetes_history_ids)
            for observation in diabetes_history:
                observation['values'] = diabetes_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    stat = ob_vals['status']
                    observation['values']['diabetes'] = 'Yes' if stat else 'No'
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get palliative_care flag history
            # search palliative_care model on patient with parent_id of spell
            # dates
            palliative_care_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.palliative_care',
                    start_time, end_time
                )
            )
            palliative_care_history = activity_pool.read(
                cr, uid, palliative_care_history_ids)
            for observation in palliative_care_history:
                observation['values'] = palliative_care_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]),
                    [])
                if observation['values']:
                    ob_vals = observation['values']
                    stat = ob_vals['status']
                    observation['values']['palliative_care'] = \
                        'Yes' if stat else 'No'
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get post_surgery flag history
            # search post_surgery model on patient with parent_id of spel
            #  dates
            post_surgery_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.post_surgery',
                    start_time, end_time
                )
            )
            post_surgery_history = activity_pool.read(
                cr, uid, post_surgery_history_ids)
            for observation in post_surgery_history:
                observation['values'] = post_surgery_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    stat = ob_vals['status']
                    observation['values']['post_surgery'] = \
                        'Yes' if stat else 'No'
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            # get critical_care flag history
            # search critical_care model on patient with parent_id of spell
            # dates
            critical_care_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.critical_care',
                    start_time, end_time
                )
            )
            critical_care_history = activity_pool.read(
                cr, uid, critical_care_history_ids)
            for observation in critical_care_history:
                observation['values'] = critical_care_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    stat = ob_vals['status']
                    observation['values']['critical_care'] = \
                        'Yes' if stat else 'No'
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
            #
            # get transfer history
            # search move on patient with parent_id of spell - dates
            transfer_history_ids = activity_pool.search(
                cr, uid, self.create_search_filter(
                    spell_activity_id,
                    'nh.clinical.patient.move',
                    start_time, end_time
                )
            )
            transfer_history = activity_pool.read(
                cr, uid, transfer_history_ids)
            for observation in transfer_history:
                observation['values'] = transfer_history_pool.read(
                    cr, uid, int(observation['data_ref'].split(',')[1]), [])
                if observation['values']:
                    ob_vals = observation['values']
                    ds = False
                    dt = False
                    if ob_vals['date_started']:
                        ds = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_started'], dtf),
                            pretty_date_format)
                    if ob_vals['date_terminated']:
                        dt = self.convert_db_date_to_context_date(
                            datetime.strptime(ob_vals['date_terminated'], dtf),
                            pretty_date_format)
                    observation['values']['date_started'] = ds
                    observation['values']['date_terminated'] = dt
                    patient_location = location_pool.read(
                        cr, uid, observation['values']['location_id'][0], [])
                    if patient_location:
                        pln = False
                        plp = False
                        if patient_location['name']:
                            pln = patient_location['name']
                        if patient_location['parent_id'][1]:
                            plp = patient_location['parent_id'][1]
                        observation['bed'] = pln
                        observation['ward'] = plp
            if len(transfer_history) > 0:
                th = transfer_history[-1]
                patient['bed'] = th['bed'] if th['bed'] else False
                patient['ward'] = th['ward'] if th['ward'] else False


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
