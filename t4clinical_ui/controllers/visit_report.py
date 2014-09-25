__author__ = 'colin'

import openerp, json
from openerp import http
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request
from openerp.osv import fields

endpoint = '/visit_report/'

graph_js = """
    var records = {json};
    var svg = graph_lib.svg,focus = graph_lib.focus,context = graph_lib.context;
    context.height = 85;
    context.margins.bottom = 28;
    focus.chartHeight = 80;
    focus.chartPadding = 20;
    svg.focusOnly = false;
    svg.margins.left = 30;
    context.margins.top = 20;
    focus.margins.top = 45;
    printing = true;
    graph_lib.svg.printing = true;
    focus.graphs = null;
    focus.graphs = new Array();
    focus.tables = null;
    focus.tables = new Array();

    context.earliestDate = svg.startParse(records[0].date_started);
    context.now = svg.startParse(records[records.length-1].date_started);
    var plotO2 = false;
    context.scoreRange = [{{"class": "green",s: 0,e: 5}},{{"class": "amber",s: 5,e: 7}},{{"class": "red",s: 7,e: 18}}];
    records.forEach(function(d){{
    d.date_started = svg.startParse(d.date_started);
    if (d.flow_rate > -1){{
    plotO2 = true;
    d.inspired_oxygen = "";
    d.inspired_oxygen += "Flow: " + d.flow_rate + "l/hr<br>";
    d.inspired_oxygen += "Concentration: " + d.concentration + "%<br>";
    if(d.cpap_peep > -1){{
    d.inspired_oxygen += "CPAP PEEP: " + d.cpap_peep + "<br>";
    }}else if(d.niv_backup > -1){{
    d.inspired_oxygen += "NIV Backup Rate: " + d.niv_backup + "<br>";
    d.inspired_oxygen += "NIV EPAP: " + d.niv_epap + "<br>";
    d.inspired_oxygen += "NIV IPAP: " + d.niv_ipap + "<br>";
    }}
    }}
    if (d.indirect_oxymetry_spo2) {{
    d.indirect_oxymetry_spo2_label = d.indirect_oxymetry_spo2 + "%";
    }}
    }});

    svg.data = records;
    focus.graphs.push({{key: "respiration_rate",label: "RR",measurement: "/min",max: 60,min: 0,normMax: 20,normMin: 12}});
    focus.graphs.push({{key: "indirect_oxymetry_spo2",label: "Spo2",measurement: "%",max: 100,min: 70,normMax: 100,normMin: 96}});
    focus.graphs.push({{key: "body_temperature",label: "Temp",measurement: "C",max: 50,min: 15,normMax: 37.1,normMin: 35}});
    focus.graphs.push({{key: "pulse_rate",label: "HR",measurement: "/min",max: 200,min: 30,normMax: 100,normMin: 50}});
    focus.graphs.push({{key: "blood_pressure",label: "BP",measurement: "mmHg",max: 260,min: 30,normMax: 150,normMin: 50}});
    focus.tables.push({{
    key: "avpu_text",
    label: "AVPU"
    }});
    focus.tables.push({{
    key: "indirect_oxymetry_spo2_label",
    label: "Oxygen saturation"
    }});
    graph_lib.initGraph(18);
    if (plotO2==true){{
    focus.tables.push({{key:"inspired_oxygen", label:"Inspired oxygen"}});
    }}
    //graph_lib.initTable();
"""

phantom_code = """
   var PhantomJSPrinting = {
    footer: {
    height: "1cm",
    contents: function(pageNum, numPages) {
    return "<div style='width: 17.5cm; font-size: 6pt; font-family: DejaVu Sans, sans-serif;  padding-left: 0.5cm; padding-right: 1.5cm;'><div style='float: left; padding-right: 1.2cm;'><p><strong>REF:</strong> {{user}} - {{time_generated}} - {{hospital_name}} - {{other_identifier}}</p></div><div style='float: right; padding-left: 1.2cm'><p id='pageNumbers'>Page "+pageNum+" of "+numPages+"</p></div></div>";
    //                        return "<div style='width: 16.5cm; font-size: 6pt; font-family: DejaVu Sans, sans-serif;  padding-left: 0.5cm; padding-right: 1.5cm;'><div style='float: left; padding-right: 1.2cm;'><p><strong>REF:</strong> {{user}} - {{time_generated}} - {{hospital_name}} - {{other_identifier}}</p></div><div style='float: right; padding-left: 1.2cm'><p>Page "+$(document).height()+"</p></div></div>";
    }
    }
    };
"""



class VisitReportController(openerp.addons.web.controllers.main.Home):

    def mimeifier(self, type):
        if type == 'css':
            return 'text/css'
        if type == 'js':
            return 'text/javascript'
        if type == 'tsv':
            return 'text/tab-separated-values'

    @http.route(endpoint + 'src/<type>/<resource>', type='http', auth='none')
    def get_resource(self, type, resource, *args, **kw):
        with open(get_module_path('t4clinical_ui') + '/static/src/{type}/{resource}'.format(type=type, resource=resource), 'r') as resource:
            return request.make_response(resource.read(), headers={'Content-Type': self.mimeifier(type)})

    @http.route(endpoint+'<spell_id>', type='http', auth='user')
    def get_report_for_spell(self, spell_id, *args, **kw):

        # Sort out optional arguments
        options = kw.copy()
        user = options['user'] if 'user' in options else 'Administrator'
        database = openerp.modules.registry.RegistryManager.get(options['database']) if 'database' in options else request.session.db
        cr = database.db.cursor if 'database' in options else request.cr

        # Setup API calls
        uid, context = 1, request.context
        api_pool = request.registry['t4.clinical.api']
        activity_pool = request.registry['t4.activity']
        spell_pool = request.registry['t4.clinical.spell']
        patient_pool = request.registry['t4.clinical.patient']
        ews_pool = request.registry['t4.clinical.patient.observation.ews']
        weight_pool = request.registry['t4.clinical.patient.observation.weight']
        height_pool = request.registry['t4.clinical.patient.observation.height']
        pbp_pool = request.registry['t4.clinical.patient.observation.pbp']
        oxygen_target_pool = request.registry['t4.clinical.patient.o2target']
        transfer_history_pool = request.registry['t4.clinical.patient.move']
        company_pool = request.registry['res.company']
        partner_pool = request.registry['res.partner']
        user_pool = request.registry['res.users']
        location_pool = request.registry['t4.clinical.location']

        if int(spell_id):

            # get user
            user_id = user_pool.search(cr, uid, [('login', '=', request.session['login'])],context=context)[0]
            user = user_pool.read(cr, uid, user_id, ['name'], context=context)['name']

            # get company information
            company_name = company_pool.read(cr, uid, 1, ['name'], context=context)['name']
            company_logo = partner_pool.read(cr, uid, 1, ['image'], context=context)['image']

            # generate report timestamp
            time_generated = fields.datetime.context_timestamp(cr, user_id, datetime.now(), context=context) \
                .strftime('%d/%m/%Y %H:%M')

            # get spell
            spell_id = int(spell_id)
            spell = spell_pool.read(cr, uid, [spell_id])[0]
            # - get the start and end date of spell
            spell_start = datetime.strptime(spell['date_started'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            spell_end = spell['date_terminated']
            report_start = spell_start
            report_end = spell_end if spell_end else time_generated

            spell_activity_id = spell['activity_id'][0]
            spell['consultants'] = partner_pool.read(cr, uid, spell['con_doctor_ids']) if len(spell['con_doctor_ids']) > 0 else False

            # - get patient id
            patient_id = spell['patient_id'][0]

            # get patient information
            patient = patient_pool.read(cr, uid, [patient_id])[0]

            # get ews observations for patient
            # - search ews model with parent_id of spell id (maybe dates for refined foo) - activity: search with data_model of ews
            ews_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.observation.ews'], ['state', '=', 'completed']])
            ews = activity_pool.read(cr, uid, ews_ids)

            # get triggered actions from ews
            # - search activity with ews ids as creator_id filter out EWS tasks
            for observation in ews:
                triggered_actions_ids = activity_pool.search(cr, uid, [['creator_id', '=', observation['id']]])
                observation['values'] = ews_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                observation['triggered_actions'] = [v for v in activity_pool.read(cr, uid, triggered_actions_ids) if v['data_model'] != 't4.clinical.patient.observation.ews']

            # get weight observations
            # - search weight model with parent_id of spell - dates
            weight_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.observation.weight'], ['state', '=', 'completed']])
            weights = activity_pool.read(cr, uid, weight_ids)
            for observation in weights:
                observation['values'] = weight_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
            patient['weight'] = weights[-1]['values']['weight'] if len(weights) > 0 else False

            # get height observations
            # - search height model with parent_id of spell - dates
            height_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.observation.height'], ['state', '=', 'completed']])
            heights = activity_pool.read(cr, uid, height_ids)
            for observation in heights:
                observation['values'] = height_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
            patient['height'] = heights[-1]['values']['height'] if len(heights) > 0 else False

            # get PBP observations
            # - search pbp model with parent_id of spell - dates
            pbp_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.observation.pbp'], ['state', '=', 'completed']])
            pbps = activity_pool.read(cr, uid, pbp_ids)
            for observation in pbps:
                observation['values'] = pbp_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])

            # get o2 target history
            # - search o2target model on patient with parent_id of spell - dates
            oxygen_history_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.o2target']])
            oxygen_history = activity_pool.read(cr, uid, oxygen_history_ids)
            for observation in oxygen_history:
                observation['values'] = oxygen_target_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])

            # get transfer history
            # - search move on patient with parent_id of spell - dates
            transfer_history_ids = activity_pool.search(cr, uid, [['parent_id', '=', spell_activity_id], ['data_model', '=', 't4.clinical.patient.move']])
            transfer_history = activity_pool.read(cr, uid, transfer_history_ids)
            for observation in transfer_history:
                observation['values'] = transfer_history_pool.read(cr, uid, int(observation['data_ref'].split(',')[1]), [])
                patient_location = location_pool.read(cr, uid, observation['values']['location_id'][0], [])
                observation['bed'] = patient_location['name'] if patient_location['name'] else False
                observation['ward'] = patient_location['parent_id'][1] if patient_location['parent_id'] else False
            if len(transfer_history) > 0:
                patient['bed'] = transfer_history[-1]['bed'] if transfer_history[-1]['bed'] else False
                patient['ward'] = transfer_history[-1]['ward'] if transfer_history[-1]['ward'] else False

            json_ews = json.dumps([v['values'] for v in ews])
            ews_code = graph_js.format(json=json_ews)

            return request.render('t4clinical_ui.visit_report_base', qcontext={'spell': spell,
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
                                                                               'phantom_code': phantom_code})






