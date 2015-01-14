# -*- coding: utf-8 -*-

import openerp, json
from openerp import http
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request, Response
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import logging

_logger = logging.getLogger(__name__)

endpoint = '/visit_report/'

phantom_code = """
   var PhantomJSPrinting = {{
    footer: {{
    height: "1cm",
    contents: function(pageNum, numPages) {{
    return "<div style='width: 17.5cm; font-size: 6pt; font-family: DejaVu Sans, sans-serif;  padding-left: 0.5cm; padding-right: 1.5cm;'><div style='float: left; padding-right: 1.2cm;'><p><strong>REF:</strong> {user} - {time_generated} - {hospital_name} - {other_identifier}</p></div><div style='float: right; padding-left: 1.2cm'><p id='pageNumbers'>Page "+pageNum+" of "+numPages+"</p></div></div>";
    //                        return "<div style='width: 16.5cm; font-size: 6pt; font-family: DejaVu Sans, sans-serif;  padding-left: 0.5cm; padding-right: 1.5cm;'><div style='float: left; padding-right: 1.2cm;'><p><strong>REF:</strong> {user} - {time_generated} - {hospital_name} - {other_identifier}</p></div><div style='float: right; padding-left: 1.2cm'><p>Page "+$(document).height()+"</p></div></div>";
    }}
    }}
    }};
"""

pretty_date_format = '%d/%m/%Y %H:%M'
phantomjs_date_format = "%Y-%m-%dT%H:%M:%S"



class VisitReportController(openerp.addons.web.controllers.main.Home):

    def mimeifier(self, type):
        if type == 'css':
            return 'text/css'
        if type == 'js':
            return 'text/javascript'
        if type == 'tsv':
            return 'text/tab-separated-values'

    def create_search_filter(self, spell_activity_id, model, start_date, end_date):
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

    def convert_db_date_to_context_date(self, cr, uid, date_string, format, context):
        if format:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context).strftime(format)
        else:
            return fields.datetime.context_timestamp(cr, uid, date_string, context=context)


    # @http.route(endpoint + 'src/<type>/<resource>', type='http', auth='none')
    # def get_visit_report_resource(self, type, resource, *args, **kw):
    #     if resource == 'd3.js':
    #         with open(get_module_path('nh_graphs') + '/static/lib/js/d3.js'.format(type=type, resource=resource), 'r') as resource:
    #             return request.make_response(resource.read(), headers={'Content-Type': self.mimeifier(type)})
    #     elif resource == 'graph_lib.js':
    #         with open(get_module_path('nh_graphs') + '/static/src/js/nh_graphlib.js'.format(type=type, resource=resource), 'r') as resource:
    #             return request.make_response(resource.read(), headers={'Content-Type': self.mimeifier(type)})
    #     else:
    #         with open(get_module_path('nh_eobs') + '/static/src/{type}/{resource}'.format(type=type, resource=resource), 'r') as resource:
    #             return request.make_response(resource.read(), headers={'Content-Type': self.mimeifier(type)})

    @http.route(endpoint+'<spell_id>', type='http', auth='none')
    def get_report_for_spell(self, spell_id, *args, **kw):
        _logger.info('Getting Report For Spell: %s' % spell_id)

        options = kw.copy()
        uid = self.authenticate(request)
        if uid:
            # Sort out optional arguments
            options = kw.copy()
            user = options['user'] if 'user' in options else 'Administrator'
            database = openerp.modules.registry.RegistryManager.get(options['database']) if 'database' in options else request.session.db
            cr = database.db.cursor if 'database' in options else request.cr
            # timestamps be UTC
            start_date = datetime.fromtimestamp(int(options['start_date'])) if 'start_date' in options else False
            end_date = datetime.fromtimestamp(int(options['end_date'])) if 'end_date' in options else False

            # Setup API calls
            uid, context = 1, request.context
            api_pool = request.registry['nh.clinical.api']
            activity_pool = request.registry['nh.activity']
            spell_pool = request.registry['nh.clinical.spell']
            patient_pool = request.registry['nh.clinical.patient']
            ews_pool = request.registry['nh.clinical.patient.observation.ews']
            weight_pool = request.registry['nh.clinical.patient.observation.weight']
            height_pool = request.registry['nh.clinical.patient.observation.height']
            pbp_pool = request.registry['nh.clinical.patient.observation.pbp']
            oxygen_target_pool = request.registry['nh.clinical.patient.o2target']
            transfer_history_pool = request.registry['nh.clinical.patient.move']
            company_pool = request.registry['res.company']
            partner_pool = request.registry['res.partner']
            user_pool = request.registry['res.users']
            location_pool = request.registry['nh.clinical.location']

            if int(spell_id):
                graph_js = open(get_module_path('nh_eobs_reports') + '/views/visit_report.js', 'r').read()
                # get user
                user_id = user_pool.search(cr, uid, [('login', '=', request.session['login'])],context=context)[0]
                user = user_pool.read(cr, uid, user_id, ['name'], context=context)['name']

                # get company information
                company_name = company_pool.read(cr, uid, 1, ['name'], context=context)['name']
                company_logo = partner_pool.read(cr, uid, 1, ['image'], context=context)['image']

                # generate report timestamp
                time_generated = fields.datetime.context_timestamp(cr, user_id, datetime.now(), context=context) \
                    .strftime(pretty_date_format)

                # get spell
                spell_id = int(spell_id)
                spell = spell_pool.read(cr, uid, [spell_id])[0]
                # - get the start and end date of spell
                spell_start = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(spell['date_started'], dtf), pretty_date_format, context=context)
                spell_end = spell['date_terminated']
                report_start = start_date.strftime(pretty_date_format) if start_date else spell_start
                if end_date:
                    report_end = end_date.strftime(pretty_date_format)
                else:
                    report_end = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(spell_end, dtf), pretty_date_format, context=context) if spell_end else time_generated

                spell_activity_id = spell['activity_id'][0]
                spell['consultants'] = partner_pool.read(cr, uid, spell['con_doctor_ids']) if len(spell['con_doctor_ids']) > 0 else False

                # - get patient id
                patient_id = spell['patient_id'][0]

                # get patient information
                patient = patient_pool.read(cr, uid, [patient_id])[0]
                patient['dob'] = self.convert_db_date_to_context_date(cr, uid,  datetime.strptime(patient['dob'], dtf), '%d/%m/%Y', context=context)

                # get ews observations for patient
                # - search ews model with parent_id of spell id (maybe dates for refined foo) - activity: search with data_model of ews
                ews_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.ews', start_date, end_date))
                ews = activity_pool.read(cr, uid, ews_ids)

                # get triggered actions from ews
                # - search activity with ews ids as creator_id filter out EWS tasks
                for observation in ews:
                    observation['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_started'], dtf), pretty_date_format, context=context)
                    observation['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_terminated'], dtf), pretty_date_format, context=context) if observation['date_terminated'] else False
                    triggered_actions_ids = activity_pool.search(cr, uid, [['creator_id', '=', observation['id']]])
                    observation['values'] = ews_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_started'], dtf), dtf, context=context) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_terminated'], dtf), dtf, context=context) if observation['values']['date_terminated'] else False
                    observation['triggered_actions'] = [v for v in activity_pool.read(cr, uid, triggered_actions_ids) if v['data_model'] != 'nh.clinical.patient.observation.ews']
                    for t in observation['triggered_actions']:
                        t['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(t['date_started'], dtf), pretty_date_format, context=context) if t['date_started'] else False
                        t['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(t['date_terminated'], dtf), pretty_date_format, context=context) if t['date_terminated'] else False

                # get weight observations
                # - search weight model with parent_id of spell - dates
                weight_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.weight', start_date, end_date))
                weights = activity_pool.read(cr, uid, weight_ids)
                for observation in weights:
                    observation['values'] = weight_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format, context=context) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format, context=context) if observation['values']['date_terminated'] else False
                patient['weight'] = weights[-1]['values']['weight'] if len(weights) > 0 else False

                # get height observations
                # - search height model with parent_id of spell - dates
                height_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.height', start_date, end_date))
                heights = activity_pool.read(cr, uid, height_ids)
                for observation in heights:
                    observation['values'] = height_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format, context=context) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format, context=context) if observation['values']['date_terminated'] else False
                patient['height'] = heights[-1]['values']['height'] if len(heights) > 0 else False

                # get PBP observations
                # - search pbp model with parent_id of spell - dates
                pbp_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.observation.pbp', start_date, end_date))
                pbps = activity_pool.read(cr, uid, pbp_ids)
                for observation in pbps:
                    observation['values'] = pbp_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_started'], dtf), pretty_date_format, context=context) if observation['date_started'] else False
                    observation['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_terminated'], dtf), pretty_date_format, context=context) if observation['date_terminated'] else False

                # get o2 target history
                # - search o2target model on patient with parent_id of spell - dates
                oxygen_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.o2target', start_date, end_date))
                oxygen_history = activity_pool.read(cr, uid, oxygen_history_ids)
                for observation in oxygen_history:
                    observation['values'] = oxygen_target_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['values']['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_started'], dtf), pretty_date_format, context=context) if observation['values']['date_started'] else False
                    observation['values']['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['values']['date_terminated'], dtf), pretty_date_format, context=context) if observation['values']['date_terminated'] else False

                # get transfer history
                # - search move on patient with parent_id of spell - dates
                transfer_history_ids = activity_pool.search(cr, uid, self.create_search_filter(spell_activity_id, 'nh.clinical.patient.move', start_date, end_date))
                transfer_history = activity_pool.read(cr, uid, transfer_history_ids)
                for observation in transfer_history:
                    observation['values'] = transfer_history_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                    observation['date_started'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_started'], dtf), pretty_date_format, context=context) if observation['date_started'] else False
                    observation['date_terminated'] = self.convert_db_date_to_context_date(cr, uid, datetime.strptime(observation['date_terminated'], dtf), pretty_date_format, context=context) if observation['date_terminated'] else False
                    patient_location = location_pool.read(cr, uid, observation['values']['location_id'][0], [])
                    observation['bed'] = patient_location['name'] if patient_location['name'] else False
                    observation['ward'] = patient_location['parent_id'][1] if patient_location['parent_id'] else False
                if len(transfer_history) > 0:
                    patient['bed'] = transfer_history[-1]['bed'] if transfer_history[-1]['bed'] else False
                    patient['ward'] = transfer_history[-1]['ward'] if transfer_history[-1]['ward'] else False

                json_obs = [v['values'] for v in ews]
                for json_ob in json_obs:
                    json_ob['date_terminated'] = datetime.strftime(datetime.strptime(json_ob['date_terminated'], dtf), phantomjs_date_format)
                json_ews = json.dumps(json_obs)
                ews_code = graph_js.format(json=json_ews)
                phantom_footer_code = phantom_code.format(user=user, time_generated=time_generated, hospital_name=company_name, other_identifier=patient['other_identifier'])

                d3 = open(get_module_path('nh_graphs') + '/static/lib/js/d3.js', 'r').read()
                graph_lib = open(get_module_path('nh_graphs') + '/static/src/js/nh_graphlib.js', 'r').read()
                style = open(get_module_path('nh_eobs') + '/static/src/css/report.css', 'r').read()

                return request.render('nh_eobs_reports.visit_report_base', qcontext={'spell': spell,
                                                                                   'user': user,
                                                                                   'hospital_logo': company_logo,
                                                                                   'hosptial_name': company_name,
                                                                                   'patient': patient,
                                                                                   'ews': ews,
                                                                                   'weights': weights,
                                                                                   'pbps': pbps,
                                                                                   'targeto2': oxygen_history,
                                                                                   'transfer_history': transfer_history,
                                                                                   'report_start': report_start,
                                                                                   'report_end': report_end,
                                                                                   'spell_start': spell_start,
                                                                                   'ews_code': ews_code,
                                                                                   'phantom_code': phantom_footer_code,
                                                                                   'd3': d3,
                                                                                   'graph_lib': graph_lib,
                                                                                   'style': style})
        else:
            return Response('Could not verify your access level for that URL.\n'
                            'You have to login with proper credentials', 401,
                            {'WWW-Authenticate': 'Basic realm="login required"'})

    def authenticate(self, request):
        db = False
        if not db:
            db = request.params.get('db') if 'db' in request.params else False
        if not db:
            db = request.db if request.db else False
        if request.httprequest.authorization and db:
            return self.check_auth(db, request.httprequest.authorization.username, request.httprequest.authorization.password)
        else:
            return False

    def check_auth(self, db, username, password):
        #user = request.session.model('res.users').search(['login', '=', username])
        #if user:
            #uid = request.session.model('res.users').read(user)[0]
            if 'HTTP_HOST' not in request.httprequest.environ:
                request.httprequest.environ['HTTP_HOST'] = request.httprequest.host
            return request.session.authenticate(db, username, password)
        #else:
        #    return False


