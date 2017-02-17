# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Creates a report containing information about observations performed on a
patient.

===========
Terminology
===========
report entry: A single line on the report. One activity may result in multiple
'entries' on the report.

report data: A giant dictionary containing all data that will be used to
generate the report.
"""
import copy
import json
from datetime import datetime

from openerp import api, models
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

from . import helpers


class ObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'

    pretty_date_format = '%H:%M %d/%m/%y'
    wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"
    patient_id = None
    spell_activity_id = None

    monitoring_dict = {
        'targeto2': 'nh.clinical.patient.o2target',
        'mrsa_history': 'nh.clinical.patient.mrsa',
        'diabetes_history': 'nh.clinical.patient.diabetes',
        'palliative_care_history': 'nh.clinical.patient.palliative_care',
        'post_surgery_history': 'nh.clinical.patient.post_surgery',
        'critical_care_history': 'nh.clinical.patient.critical_care'
    }

    @api.multi
    def render_html(self, data=None):
        """"
        This is a special method that the Odoo report module executes instead
        of it's built-in `render_html` method when generating a report.
        """
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

    def get_report_data(self, data, ews_only=False):
        """
        Returns a dictionary that will be used to populate the report.
        Most of the values are themselves dictionaries returned by
        `activity.read()`. However they also have an additional key named
        'values' that contains the activities `data_ref` record as dictionaries
        returned by `model.read()`.

        :param data:
        :param ews_only:
        :return:
        :rtype: dict
        """
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
        self.spell_activity_id = spell_activity_id
        spell_docs = spell['con_doctor_ids']
        spell['consultants'] = False
        if len(spell_docs) > 0:
            spell['consultants'] = partner_pool.read(cr, uid, spell_docs)
        self.patient_id = spell['patient_id'][0]
        patient_id = self.patient_id

        # Get patient information
        patient = patient_pool.read(cr, uid, [patient_id])[0]
        patient_location = patient.get('current_location_id')
        patient['dob'] = helpers.convert_db_date_to_context_date(
            cr, uid, datetime.strptime(patient['dob'], dtf),
            '%d/%m/%Y', context=None) if patient.get('dob', False) else ''
        ews = self.get_ews_observations(data, spell_activity_id)
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

        monitoring = self.create_patient_monitoring_exception_dictionary(
            data, spell_activity_id
        )

        transfer_history = self.process_transfer_history(
            self.get_model_data(
                spell_activity_id,
                'nh.clinical.patient.move',
                data.start_time, data.end_time)
        )
        if patient_location:
            location_pool = self.pool['nh.clinical.location']
            current_loc = location_pool.read(cr, uid, patient_location[0])
            loc = current_loc.get('full_name')
            patient['location'] = loc if loc else ''

        device_session_history = self.get_multi_model_data(
            spell_activity_id,
            'nh.clinical.patient.o2target',
            'nh.clinical.device.session',
            data.start_time, data.end_time
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
    def get_activity_data(
            self, spell_activity_id, model, start_time, end_time):
        """
        Returns a list of dictionaries, each one representing the values of one
        :class:<nh_activity.activity.nh_activity> record.

        :param spell_activity_id:
        :param model: The name of the model matching the type of activity data
        to retrieve activities for.
        :type model: str
        :param start_time:
        :param end_time:
        :return:
        :rtype: dict
        """
        cr, uid = self._cr, self._uid
        activity_model = self.pool['nh.activity']

        states = self._get_allowed_activity_states_for_model(model)
        domain = helpers.create_search_filter(
            spell_activity_id, model, start_time, end_time, states=states
        )
        self.add_exclude_placement_cancel_reason_parameter_to_domain(domain)

        activity_ids = activity_model.search(cr, uid, domain)
        activity_data = activity_model.read(cr, uid, activity_ids)
        self.add_user_key(activity_data)

        return activity_data

    def add_user_key(self, activity_data_list):
        for activity_data in activity_data_list:
            terminate_user_tuple = activity_data.get('terminate_uid')
            is_tuple = isinstance(terminate_user_tuple, tuple)
            user_name = terminate_user_tuple[1] \
                if is_tuple and len(terminate_user_tuple) > 1 else False
            if not user_name and is_tuple:
                user_id = terminate_user_tuple[0]
                user_model = self.env['res.users']
                user_name = user_model.get_name(user_id)
            activity_data['user'] = user_name

    def add_exclude_placement_cancel_reason_parameter_to_domain(self, domain):
        model_data = self.env['ir.model.data']
        cancel_reason_placement = \
            model_data.get_object('nh_clinical', 'cancel_reason_placement')
        # Using the `!=` would not return anything, possible bug, or it could
        # be that this operator only includes fields that are set AND do not
        # match the specified value. Either way I had to use `not in` to get
        # the desired result.
        parameter_exclude_placement_cancel_reason = \
            ('cancel_reason_id', 'not in', [cancel_reason_placement.id])
        domain.append(parameter_exclude_placement_cancel_reason)

    def _get_allowed_activity_states_for_model(self, model):
        """
        Returns the states that an activity can be in if it is to be included
        on the observation report.

        :param model:
        :type model: str
        :return: string or list of strings.
        :rtype: str or list
        """
        monitoring_models = self.monitoring_dict.values()

        if model in monitoring_models:
            # Add activities of any state to the report for these models.
            return ['started', 'completed', 'cancelled']
        if model == 'nh.clinical.patient.observation.ews':
            return ['completed', 'cancelled']
        else:
            return 'completed'

    def get_model_data(self, spell_activity_id, model, start, end):
        """
        Get activities associated with the passed model and spell id and
        return them as a dictionary.

        :param spell_activity_id:
        :type spell_activity_id: int
        :param model:
        :type model: str
        :param start:
        :type start: str
        :param end:
        :type end: str
        :return: Activities for the passed spell id and model within the date
        range.
        :rtype: dict
        """
        activity_data = \
            self.get_activity_data(spell_activity_id, model, start, end)
        if activity_data:
            self.convert_activities_dates_to_context_dates(activity_data)
        return self.get_model_values(model, activity_data)

    def get_model_values(self, model, activity_data):
        """
        Adds a `values` key to the passed activity dictionary which
        is associated with another dictionary of values representing the
        record which is the data ref of the passed activity.

        :param model:
        :type model: str
        :param activity_data:
        :type activity_data: str
        :return:
        :rtype: dict
        """
        cr, uid = self._cr, self._uid
        model_pool = self.pool[model]
        for activity in activity_data:
            obs_id = self._get_data_ref_id(activity)
            if 'nh.clinical.patient.observation' in model_pool._name:
                model_data = model_pool.read_labels(cr, uid, obs_id, [])
            else:
                model_data = model_pool.read(cr, uid, obs_id, [])
            if isinstance(model_data, list):
                # V8 read always returns a list, V7 doesn't when single int is
                # passed as id instead of a list.
                if len(model_data) > 1:
                    message = "Should have read data for only one record but " \
                              "more than one was found."
                    raise ValueError(message)
                model_data = model_data[0]

            if model_data:
                stat = 'No'
                date_terminated = 'date_terminated'
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
                if date_terminated in model_data \
                        and model_data[date_terminated]:
                    model_data['date_terminated'] = \
                        helpers.convert_db_date_to_context_date(
                            cr, uid,
                            datetime.strptime(
                                model_data['date_terminated'],
                                dtf
                            ),
                            self.pretty_date_format
                        )
            activity['values'] = model_data
        return activity_data

    @classmethod
    def _get_data_ref_id(cls, activity_dictionary):
        """
        Takes the string value of a `data_ref` field on a record and extracts
        the id from it.

        :param activity_dictionary: A dictionary representing an activity as
        returned from :method:<read>.
        :return:
        :rtype: int
        """
        return int(activity_dictionary['data_ref'].split(',')[1])

    @classmethod
    def _get_id_from_tuple(cls, tuple):
        """
        Extracts the id from one of the tuples commonly seen as the value of
        relational fields on models.

        :param tuple:
        :return:
        :rtype: int
        """
        return int(tuple[0])

    def get_multi_model_data(self, spell_id,
                             model_one, model_two,  start, end):
        act_data = self.get_activity_data(spell_id, model_one, start, end)
        return self.get_model_values(model_two, act_data)

    def get_model_data_as_json(self, model_data):
        for data in model_data:
            if 'write_date' in data and data['write_date']:
                data['write_date'] = datetime.strftime(
                    datetime.strptime(data['write_date'], dtf),
                    self.wkhtmltopdf_format
                )
            if 'create_date' in data and data['create_date']:
                data['create_date'] = datetime.strftime(
                    datetime.strptime(data['create_date'], dtf),
                    self.wkhtmltopdf_format
                )
            if 'date_started' in data and data['date_started']:
                data['date_started'] = datetime.strftime(
                    datetime.strptime(
                        data['date_started'],
                        self.pretty_date_format
                    ),
                    self.wkhtmltopdf_format
                )
            if 'date_terminated' in data and data['date_terminated']:
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

    @api.model
    def add_triggered_action_keys_to_obs_dicts(self, obs_dict_list):
        for observation in obs_dict_list:
            triggered_actions = self.get_triggered_actions(observation['id'])
            for t in triggered_actions:
                ds = t.get('date_started', False)
                dt = t.get('date_terminated', False)
                if ds:
                    t['date_started'] = \
                        helpers.convert_db_date_to_context_date(
                            self.env.cr, self.env.uid,
                            datetime.strptime(t['date_started'], dtf),
                            self.pretty_date_format
                        )
                if dt:
                    t['date_terminated'] = \
                        helpers.convert_db_date_to_context_date(
                            self.env.cr, self.env.uid,
                            datetime.strptime(t['date_terminated'], dtf),
                            self.pretty_date_format
                        )
            observation['triggered_actions'] = triggered_actions

    @api.model
    def get_triggered_actions(self, observation_activity_id,
                              activity_list=None):
        triggered_actions_ids = self.get_triggered_action_ids(
            observation_activity_id, activity_list=activity_list
        )
        return self.pool['nh.activity'].read(
            self.env.cr, self.env.uid, triggered_actions_ids
        )

    def get_triggered_action_ids(self, cr, uid,
                                 activity_id, activity_list=None):
        """
        Recursively get the triggered actions of the activity passed to it
        and then it's children and so on.

        :param activity_id: The current activity under inspection
        :type activity_id: int
        :param activity_list: the list to use
        :return: list of activity ids
        :rtype: list
        """
        if not activity_list:
            activity_list = []
        activity_pool = self.pool['nh.activity']
        created_ids = activity_pool.search(
            cr, uid, [
                ['creator_id', '=', activity_id],
                ['data_model', '!=', 'nh.clinical.patient.observation.ews']
            ])
        if created_ids:
            activity_list += created_ids
            for created_id in created_ids:
                self.get_triggered_action_ids(cr, uid, created_id,
                                              activity_list=activity_list)
        return activity_list

    @api.multi
    def get_ews_observations(self, data, spell_activity_id):
        """
        Gets all completed or cancelled EWS observations associated with the
        passed spell activity id and returns them as a list of dictionaries.

        :param data:
        :param spell_activity_id:
        :type spell_activity_id: int
        :return:
        :rtype: dict
        """
        cr, uid = self._cr, self._uid
        ews_model = 'nh.clinical.patient.observation.ews'
        ews = self.get_model_data(spell_activity_id,
                                  ews_model,
                                  data.start_time, data.end_time)
        ews = self.convert_partial_reasons_to_labels(ews)

        for observation in ews:
            o2target_dt = datetime.strptime(
                observation['values']['date_terminated'],
                self.pretty_date_format
            ).strftime(dtf)
            o2_level_id = self.pool['nh.clinical.patient.o2target'].get_last(
                cr, uid, self.patient_id,
                datetime=o2target_dt)
            o2_level = False
            if o2_level_id:
                o2_level = self.pool['nh.clinical.o2level'].browse(
                    cr, uid, o2_level_id)
            observation['values']['o2_target'] = False
            if o2_level:
                observation['values']['o2_target'] = o2_level.name

        self.add_triggered_action_keys_to_obs_dicts(ews)

        return ews

    @api.model
    def convert_partial_reasons_to_labels(self, ews_obs):
        ews_model = self.env['nh.clinical.patient.observation.ews']
        for ews in ews_obs:
            partial_reason = ews.get('values', {}).get('partial_reason', None)
            if not partial_reason:
                continue
            if ews['values']['partial_reason'] == 'refused':
                ews['values']['partial_reason'] = 'Refusal'
            else:
                ews['values']['partial_reason'] = \
                    ews_model.get_partial_reason_label(
                        ews['values']['partial_reason']
                    )
        return ews_obs

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
            if isinstance(data.start_time, str):
                start_time = datetime.strptime(data.start_time, dtf)
                data.start_time = start_time
        if data.end_time:
            if isinstance(data.end_time, str):
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

    def create_patient_monitoring_exception_dictionary(self, data,
                                                       spell_activity_id):
        """
        Creates a dictionary containing data for patient monitoring exceptions
        that can be used to populate the observation report.

        :param data:
        :param spell_activity_id:
        :type spell_activity_id: int
        :return:
        :rtype: dict
        """
        old_style_patient_monitoring_exceptions = \
            copy.deepcopy(self.monitoring_dict)
        old_style_patient_monitoring_exceptions = \
            self.get_activity_data_from_dict(
                old_style_patient_monitoring_exceptions,
                spell_activity_id, data
            )

        new_style_patient_monitoring_exceptions = \
            self.get_patient_monitoring_exception_report_data(
                spell_activity_id, data.start_time, data.end_time
            )

        patient_monitoring_exception_dictionary = helpers.merge_dicts(
            old_style_patient_monitoring_exceptions,
            new_style_patient_monitoring_exceptions
        )

        return patient_monitoring_exception_dictionary

    def get_patient_monitoring_exception_report_data(self,
                                                     spell_activity_id,
                                                     start_date=None,
                                                     end_date=None):
        """
        Returns a dictionary containing data for 'new style' patient monitoring
        exceptions. These are patient monitoring exceptions which are records
        of the :class:<nh_eobs.models.PatientMonitoringException> model.

        The data returned is meant for use on the observation report, it is
        not a full representation of the record, just a few fields that
        are ready to be mapped directly onto the report.

        :param spell_activity_id:
        :type spell_activity_id: int
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: dict
        """
        pme_activity_ids = \
            self.get_monitoring_exception_activity_ids_for_report(
                spell_activity_id, start_date, end_date
            )

        report_data = \
            self.get_monitoring_exception_report_data_from_activities(
                pme_activity_ids, start_date, end_date
            )

        dictionary = {
            'patient_monitoring_exception_history': report_data
        }
        return dictionary

    def get_monitoring_exception_activity_ids_for_report(self,
                                                         spell_activity_id,
                                                         start_date=None,
                                                         end_date=None):
        """
        Returns a list of ids for all activities whose information should be
        included in the report. Exactly what entries should be created for
        these activities on the report is decided later.

        :param spell_activity_id:
        :type spell_activity_id: int
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        """
        cr, uid = self._cr, self._uid
        activity_model = self.pool['nh.activity']

        domain = self.build_monitoring_exception_domain(spell_activity_id,
                                                        start_date, end_date)
        activity_ids = activity_model.search(cr, uid, domain)
        if not isinstance(activity_ids, list):
            activity_ids = [activity_ids]
        return activity_ids

    @classmethod
    def build_monitoring_exception_domain(cls, spell_activity_id,
                                          start_date=None, end_date=None):
        """
        Contained in the domain is all the business logic for deciding whether
        an activity may need to included on the report in some way.

        The domain uses Polish Notation. You can learn how to read it
        `on Wikipedia
        <https://en.wikipedia.org/wiki/Polish_notation#Computer_programming>`_.

        :param spell_activity_id:
        :param start_date:
        :param end_date:
        :return:
        """
        model = 'nh.clinical.patient_monitoring_exception'

        base_domain = [
            ('parent_id', '=', spell_activity_id),
            ('data_model', '=', model),
        ]
        include_all_parameters = [
            ('state', 'in', ['started', 'completed', 'cancelled'])
        ]
        filter_on_date_parameters = [
            '|',
            ('state', '=', 'started'),
            '&',
            ('state', 'in', ['completed', 'cancelled']),
            '|',
            '&' if start_date and end_date else None,
            ('date_started', '>=', start_date) if start_date else None,
            ('date_started', '<=', end_date) if end_date else None,
            '&' if start_date and end_date else None,
            ('date_terminated', '>=', start_date) if start_date else None,
            ('date_terminated', '<=', end_date) if end_date else None
        ]
        domain = base_domain
        if not start_date and not end_date:
            return domain + include_all_parameters
        else:
            # Get rid of any Nones.
            filter_on_date_parameters = \
                [parameter for parameter in filter_on_date_parameters
                 if parameter is not None]
            return domain + filter_on_date_parameters

    def get_monitoring_exception_report_data_from_activities(
            self, pme_activity_ids, start_date=None, end_date=None):
        """
        Calls :method:<get_monitoring_exception_report_data_from_activity>
        recursively.

        :param pme_activity_ids:
        :type pme_activity_ids: list
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: dict
        """
        report_entries = []

        for pme_activity_id in pme_activity_ids:
            some_more_report_entries = \
                self.get_monitoring_exception_report_data_from_activity(
                    pme_activity_id, start_date, end_date
                )
            report_entries += some_more_report_entries

        return report_entries

    def get_monitoring_exception_report_data_from_activity(
            self, pme_activity_id, start_date=None, end_date=None):
        """
        Gets data from the activities with the passed ids and returns a
        dictionary containing just the values needed for the observation
        report.

        :param pme_activity_id:
        :type pme_activity_id: int
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: dict
        """
        cr, uid = self._cr, self._uid
        activity_model = self.pool['nh.activity']

        activity = activity_model.read(cr, uid, pme_activity_id)
        if isinstance(activity, list):
            activity = activity[0]

        report_entries = []
        # Get report entry for start of patient monitoring exception.
        if self.include_stop_obs_entry(activity, start_date, end_date):
            stop_obs_report_entry = \
                self.get_report_entry_dictionary(pme_activity_id)
            report_entries.append(stop_obs_report_entry)

        # Get report entry for end of patient monitoring exception if it is not
        # still open.
        if self.include_restart_obs_entry(activity, start_date, end_date):
            restart_obs_report_entry = \
                self.get_report_entry_dictionary(pme_activity_id,
                                                 restart_obs=True)
            report_entries.append(restart_obs_report_entry)

        return report_entries

    def include_stop_obs_entry(self, activity, start_date=None, end_date=None):
        """
        Encapsulates the logic for deciding if a 'Stop Observations' entry
        should be included on the report for the passed activity dictionary.

        :param activity: dictionary as returned by :method:<read>
        :type activity: dict
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: bool
        """
        if not start_date and end_date:
            return True
        try:
            if activity['state'] == 'started':
                return True
            if activity['date_started']:
                if self.is_datetime_within_range(activity['date_started'],
                                                 start_date, end_date):
                    return True
                if self.is_activity_date_terminated_within_date_range(
                    activity, start_date, end_date
                ):
                    return True
            return False
        except KeyError, e:
            raise ValueError("A KeyError was raised because the activity did "
                             "not have the expected keys.", e)

    def include_restart_obs_entry(self, activity,
                                  start_date=None, end_date=None):
        """
        Encapsulates the logic for deciding if a 'Restart Observations' entry
        should be included on the report for the passed activity dictionary.

        :param activity: dictionary as returned by :method:<read>
        :type activity: dict
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: bool
        """
        if activity['date_terminated']:
            if not start_date and end_date:
                return True
            return self.is_activity_date_terminated_within_date_range(
                activity, start_date, end_date
            )
        return False

    def is_activity_date_terminated_within_date_range(self, activity,
                                                      start_date=None,
                                                      end_date=None):
        """
        Returns a boolean indicating whether a particular activity's
        date_terminated field falls within the specified date range.

        :param activity: dictionary as returned by :method:<read>
        :type activity: dict
        :param start_date:
        :type start_date: str
        :param end_date:
        :type end_date: str
        :return:
        :rtype: bool
        """
        if activity['date_terminated']:
            return self.is_datetime_within_range(
                activity['date_terminated'], start_date, end_date
            )
        return False

    @classmethod
    def is_datetime_within_range(cls, date_time,
                                 start_date=None, end_date=None):
        """
        Returns a boolean indicating whether the passed datetime falls within
        the specified date range.

        :param date_time:
        :type date_time: str or datetime
        :param start_date:
        :type start_date: str or datetime
        :param end_date:
        :type end_date: str or datetime
        :return:
        :rtype: bool
        """
        if isinstance(date_time, str):
            date_time = datetime.strptime(date_time, dtf)

        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, dtf)
            if not date_time >= start_date:
                return False

        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, dtf)
            if not date_time <= end_date:
                return False

        return True

    def get_report_entry_dictionary(self, pme_activity_id,
                                    restart_obs=False):
        """
        Creates a dictionary that contains the data that will be used to
        populate the report for a single entry concerning a
        patient monitoring exception activity.

        Contains various bits of logic to return different values depending on
        whether it has been instructed to create a 'Stop Observations' entry or
        a 'Restart Observations' entry, or if the patient monitoring exception
        activity was cancelled due to a transfer.

        :param pme_activity_id:
        :type pme_activity_id: int
        :param restart_obs:
        :type restart_obs: bool
        :return:
        :rtype: dict
        """
        cr, uid = self._cr, self._uid
        activity_model = self.pool['nh.activity']
        pme_model = \
            self.pool['nh.clinical.patient_monitoring_exception']
        cancel_reason_model = self.pool['nh.cancel.reason']
        users_model = self.pool['res.users']

        activity = activity_model.read(cr, uid, pme_activity_id)
        if isinstance(activity, list):
            activity = activity[0]

        self.convert_activity_dates_to_context_dates(activity)

        pme_id = self._get_data_ref_id(activity)
        pme = pme_model.read(cr, uid, pme_id)

        date = activity['date_started'] if not restart_obs \
            else activity['date_terminated']
        status = 'Stop Observations' if not restart_obs \
            else 'Restart Observations'

        if restart_obs and activity['cancel_reason_id']:
            cancel_reason_id = \
                self._get_id_from_tuple(activity['cancel_reason_id'])
            cancel_reason = \
                cancel_reason_model.read(cr, uid, cancel_reason_id)
            if cancel_reason['name'] == 'Transfer':
                user = 'Transfer'
                reason = 'Transfer'
        else:
            user_id = activity['create_uid']
            user_id = self._get_id_from_tuple(user_id)
            user_dict = users_model.read(cr, uid, user_id, fields=['name'])
            user = user_dict['name']

            # pme['reason'] is a tuple: (id, display_name)
            reason = pme['reason'][1] if not restart_obs else None

        return {
            'date': date,
            'user': user,
            'status': status,
            'reason': reason
        }

    def convert_activities_dates_to_context_dates(self, activity_data):
        """
        Calls :method:<convert_activity_dates_to_context_dates> recursively.

        :param activity_data:
        :type activity_data: list
        :return: No return, just side effects.
        """
        for activity in activity_data:
            self.convert_activity_dates_to_context_dates(activity)

    def convert_activity_dates_to_context_dates(self, activity):
        """
        Ensures dates on the passed activity are in the correct format and
        timezone.

        :param activity:
        :type activity: dict
        :return:
        :rtype: No return, just side effects.
        """
        cr, uid = self._cr, self._uid
        date_started = False
        date_terminated = False
        if 'date_started' in activity and activity['date_started']:
            date_started = activity['date_started']
        if 'date_terminated' in activity \
                and activity['date_terminated']:
            date_terminated = activity['date_terminated']
        if date_started:
            date_started = helpers.convert_db_date_to_context_date(
                cr, uid, datetime.strptime(date_started, dtf),
                self.pretty_date_format
            )
            activity['date_started'] = date_started
        if date_terminated:
            date_terminated = helpers.convert_db_date_to_context_date(
                cr, uid, datetime.strptime(date_terminated, dtf),
                self.pretty_date_format
            )
            activity['date_terminated'] = date_terminated
