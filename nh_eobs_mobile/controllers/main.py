# -*- coding: utf-8 -*-s
import openerp, re, json, urls, jinja2, bisect
from openerp import http
from openerp.http import Root, Response
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request
from werkzeug import utils, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

URL_PREFIX = '/mobile/'
URLS = urls.URLS


db_list = http.db_list

db_monodb = http.db_monodb

loader = jinja2.FileSystemLoader(get_module_path('nh_eobs_mobile') + '/views/')
env = jinja2.Environment(loader=loader)


def abort_and_redirect(url):
    r = request.httprequest
    response = utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    exceptions.abort(response)

def ensure_db(redirect=URLS['login']):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    db = request.params.get('db')

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = r.base_url
        if r.query_string:
            # Can't use werkzeug.wrappers.BaseRequest.url with encoded hashes:
            # https://github.com/amigrave/werkzeug/commit/b4a62433f2f7678c234cdcac6247a869f90a7eb7
            url_redirect += '?' + r.query_string
        response = utils.redirect(url_redirect, 302)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db:
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        exceptions.abort(utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db


class MobileFrontend(openerp.addons.web.controllers.main.Home):


    @http.route(URLS['stylesheet'], type='http', auth='none')
    def get_stylesheet(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/css/nhc.css', 'r') as stylesheet:
            return request.make_response(stylesheet.read(), headers={'Content-Type': 'text/css; charset=utf-8'})

    @http.route(URLS['manifest'], type='http', auth='none')
    def get_manifest(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/manifest.json', 'r') as manifest:
            return request.make_response(manifest.read(), headers={'Content-Type': 'application/json'})

    @http.route(URLS['small_icon'], type='http', auth='none')
    def get_small_icon(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/icon/hd_small.png', 'r') as icon:
            return request.make_response(icon.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['big_icon'], type='http', auth='none')
    def get_big_icon(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/icon/hd_hi.png', 'r') as icon:
            return request.make_response(icon.read(), headers={'Content-Type': 'image/png'})

    @http.route('/mobile/src/fonts/<xmlid>', auth='none', type='http')
    def get_font(self, xmlid, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/fonts/' + xmlid, 'r') as font:
            return request.make_response(font.read(), headers={'Content-Type': 'application/font-woff'})


    @http.route(URLS['logo'], type='http', auth='none')
    def get_logo(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/img/open_eobs_logo.png', 'r') as logo:
            return request.make_response(logo.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['bristol_stools_chart'], type='http', auth='none')
    def get_bristol_stools_chart(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/img/bristol_stools.png', 'r') as bsc:
            return request.make_response(bsc.read(), headers={'Content-Type': 'image/png'})

    @http.route(URLS['jquery'], type='http', auth='none')
    def get_jquery(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/js/jquery.js', 'r') as jquery:
            return request.make_response(jquery.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['observation_form_js'], type='http', auth='none')
    def get_observation_js(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/js/observation.js', 'r') as js:
            return request.make_response(js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['observation_form_validation'], type='http', auth='none')
    def get_observation_validation(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/js/validation.js', 'r') as js:
            return request.make_response(js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['js_routes'], type='http', auth='none')
    def javascript_routes(self, *args, **kw):
        urls.BASE_URL = request.httprequest.host_url[:-1] + URL_PREFIX
        URLS = urls.URLS
        routes = urls.routes
        for route in routes:
            route['args_list'] = ','.join(route['args']) if route['args'] else False
        return request.make_response(env.get_template('routes_template.js').render({
            'routes': routes,
            'base_url': request.httprequest.host_url[:-1] + URL_PREFIX
        }), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['graph_lib'], type='http', auth='none')
    def graph_lib(self, *args, **kw):
        with open(get_module_path('nh_graphs') + '/static/src/js/nh_graphlib.js', 'r') as pg:
            return request.make_response(pg.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['patient_graph'], type='http', auth='none')
    def patient_graph_js(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile') + '/static/src/js/draw_ews_graph.js', 'r') as js:
            return request.make_response(js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URLS['data_driven_documents'], type='http', auth='none')
    def d_three(self, *args, **kw):
        with open(get_module_path('nh_graphs') + '/static/lib/js/d3.js', 'r') as js:
            return request.make_response(js.read(), headers={'Content-Type': 'text/javascript'})

    @http.route(URL_PREFIX, type='http', auth='none')
    def index(self, *args, **kw):
        ensure_db()
        if request.session.uid:
            return utils.redirect(URLS['task_list'], 303)
        else:
            return utils.redirect(URLS['login'], 303)

    @http.route(URLS['login'], type="http", auth="none")
    def mobile_login(self, *args, **kw):

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        values['databases'] = [values['database']] if 'database' in values and values['database'] in values['databases'] else values['databases']

        login_template = env.get_template('login.html')


        if request.httprequest.method == 'GET':
            response = request.make_response(login_template.render(stylesheet=URLS['stylesheet'], logo=URLS['logo'], form_action=URLS['login'], errors='', databases=values['databases']))  # , headers={'X-Openerp-Session-Id': request.session_id})
            response.set_cookie('session_id', value=request.session_id, max_age=3600)
            return response
        if request.httprequest.method == 'POST':
            database = values['database'] if 'database' in values else False
            if database:
                uid = request.session.authenticate(database, request.params['username'], request.params['password'])
                if uid is not False:
                    request.uid = uid
                    return utils.redirect(URLS['task_list'], 303)
            response = request.make_response(login_template.render(stylesheet=URLS['stylesheet'], logo=URLS['logo'], form_action=URLS['login'], errors='<div class="alert alert-error">Invalid username/password</div>', databases=values['databases']))  # , headers={'X-Openerp-Session-Id': request.session_id})
            response.set_cookie('session_id', value=request.session_id, max_age=3600)
            return response
    @http.route(URLS['logout'], type='http', auth="user")
    def mobile_logout(self, *args, **kw):
        api = request.registry['nh.eobs.api']
        api.unassign_my_activities(request.cr, request.session.uid)
        request.session.logout()
        return utils.redirect(URLS['login'], 303)


    def calculate_ews_class(self, score):
        if score == 'None':
            return 'level-none'
        elif score == 'Low':
            return 'level-one'
        elif score == 'Medium':
            return 'level-two'
        elif score == 'High':
            return 'level-three'
        else:
            return 'level-none'

    @http.route(URLS['patient_list'], type='http', auth="user")
    def get_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.session.uid, request.context
        patient_api = request.registry['nh.eobs.api']
        patient_api.unassign_my_activities(cr, uid)
        follow_activities = patient_api.get_assigned_activities(cr, uid,
                                                                activity_type='nh.clinical.patient.follow',
                                                                context=context)
        patients = patient_api.get_patients(cr, uid, [], context=context)
        patient_api.get_patient_followers(cr, uid, patients, context=context)
        following_patients = patient_api.get_followed_patients(cr, uid, [])
        for patient in patients:
            patient['url'] = '{0}{1}'.format(URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(patient['clinical_risk'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False
        for fpatient in following_patients:
            fpatient['url'] = '{0}{1}'. format(URLS['single_patient'], fpatient['id'])
            fpatient['color'] = self.calculate_ews_class(fpatient['clinical_risk'])
            fpatient['trend_icon'] = 'icon-{0}-arrow'.format(fpatient['ews_trend'])
            fpatient['deadline_time'] = fpatient['next_ews_time']
            fpatient['summary'] = fpatient['summary'] if fpatient.get('summary') else False
        return request.render('nh_eobs_mobile.patient_task_list', qcontext={'notifications': follow_activities,
                                                                            'items': patients,
                                                                            'followed_items': following_patients,
                                                                            'section': 'patient',
                                                                            'username': request.session['login'],
                                                                            'urls': URLS})

    @http.route(URLS['share_patient_list'], type='http', auth='user')
    def get_share_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.session.uid, request.context
        api = request.registry['nh.eobs.api']
        api.unassign_my_activities(cr, uid)
        patients = api.get_patients(cr, uid, [], context=context)
        api.get_patient_followers(cr, uid, patients, context=context)
        api.get_invited_users(cr, uid, patients, context=context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False
            if patient.get('followers'):
                followers = patient['followers']
                patient['followers'] = ', '.join([f['name'] for f in followers])
                patient['follower_ids'] = [f['id'] for f in followers]
            if patient.get('invited_users'):
                users = patient['invited_users']
                patient['invited_users'] = ', '.join([u['name'] for u in users])
        sorted_pts = sorted(patients, key=lambda k: cmp(k['followers'], k['invited_users']))
        return request.render('nh_eobs_mobile.share_patients_list', qcontext={'items': sorted_pts,
                                                                              'section': 'patient',
                                                                              'username': request.session['login'],
                                                                              'share_list': True,
                                                                              'urls': URLS,
                                                                              'user_id': uid})

    @http.route(URLS['json_share_patients'], type='http', auth='user')
    def share_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        user_api = request.registry['res.users']
        kw_copy = kw.copy()
        user_ids = [int(id) for id in kw_copy['user_ids'].split(',')]
        patient_ids = [int(id) for id in kw_copy['patient_ids'].split(',')]
        users = user_api.read(cr, uid, user_ids, context=context)
        for user_id in user_ids:
            api.follow_invite(cr, uid, patient_ids, user_id, context=context)
        return request.make_response(json.dumps({'status': True,
                                                 'reason': 'An invite has been sent to follow the selected patients.',
                                                 'shared_with': [user['display_name'] for user in users]}),
                                     headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_claim_patients'], type='http', auth='user')
    def claim_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        kw_copy = kw.copy()
        patient_ids = [int(id) for id in kw_copy['patient_ids'].split(',')]
        api.remove_followers(cr, uid, patient_ids, context=context)
        return request.make_response(json.dumps({'status': True,
                                                 'reason': 'Followers removed successfully.'}),
                                     headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_colleagues_list'], type='http', auth='user')
    def get_colleagues(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        return request.make_response(json.dumps(api.get_share_users(cr, uid, context=context)),
                                     headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_invite_patients']+'<activity_id>', type='http', auth='user')
    def get_shared_patients(self, activity_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(cr, uid, activity_type='nh.clinical.patient.follow', context=context)
        res = {}
        for a in activities:
            if a['id'] == int(activity_id):
                res = api.get_patients(cr, uid, a['patient_ids'], context=context)
                break
        return request.make_response(json.dumps(res), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_accept_patients']+'<activity_id>', type='http', auth='user')
    def accept_shared_patients(self, activity_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(cr, uid, activity_type='nh.clinical.patient.follow', context=context)
        res = {}
        for a in activities:
            if a['id'] == int(activity_id):
                res = a
                res['status'] = True
                break
        api.complete(cr, uid, int(activity_id), {}, context=context)
        return request.make_response(json.dumps(res), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_reject_patients']+'<activity_id>', type='http', auth='user')
    def reject_shared_patients(self, activity_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry['nh.eobs.api']
        activities = api.get_assigned_activities(cr, uid, activity_type='nh.clinical.patient.follow', context=context)
        res = {}
        for a in activities:
            if a['id'] == int(activity_id):
                res = a
                res['status'] = True
                break
        api.cancel(cr, uid, int(activity_id), {}, context=context)
        return request.make_response(json.dumps(res), headers={'Content-Type': 'application/json'})

    @http.route(URLS['task_list'], type='http', auth='user')
    def get_tasks(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        task_api = request.registry['nh.eobs.api']
        task_api.unassign_my_activities(cr, uid)
        # grab the patient object and get id?
        tasks = task_api.get_activities(cr, uid, [], context=context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(URLS['single_task'], task['id'])
            task['color'] = self.calculate_ews_class(task['clinical_risk'])
        return request.render('nh_eobs_mobile.patient_task_list', qcontext={'items': tasks,
                                                                             'section': 'task',
                                                                             'username': request.session['login'],
                                                                             'urls': URLS})

    @http.route(URLS['json_take_task']+'<task_id>', type="http", auth="user")
    def take_task_ajax(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        task_id = int(task_id)
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']
        task = activity_reg.read(cr, uid, task_id, ['user_id'], context=context)
        if 'user_id' in task and task['user_id'][0] != uid:
            return request.make_response(json.dumps({'status': 'false', 'reason': 'task assigned to another user'}), headers={'Content-Type': 'application/json'})
        else:
            return request.make_response(json.dumps({'status': 'true'}), headers={'Content-Type': 'application/json'})
        try:
            api_reg.assign(cr, uid, task_id, {'user_id': uid}, context=context)
            return request.make_response(json.dumps({'status': 'true'}), headers={'Content-Type': 'application/json'})
        except Exception:
            return request.make_response(json.dumps({'status': 'false', 'reason': 'unable to assign to user'}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_cancel_take_task']+'<task_id>', type="http", auth="user")
    def cancel_take_task_ajax(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        task_id = int(task_id)
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']
        task = activity_reg.read(cr, uid, task_id, ['user_id'], context=context)
        if task.get('user_id') and task['user_id'][0] != uid:
            return request.make_response(json.dumps({'status': 'false', 'reason': "Can't cancel other user's task"}), headers={'Content-Type': 'application/json'})
        else:
            try:
                api_reg.unassign(cr, uid, task_id, context=context)
                return request.make_response(json.dumps({'status': 'true'}), headers={'Content-Type': 'application/json'})
            except Exception:
                return request.make_response(json.dumps({'status': 'false', 'reason': "Unable to unassign task"}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['single_task']+'<task_id>', type='http', auth='user')
    def get_task(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        activity_reg = request.registry['nh.activity']
        api_reg = request.registry['nh.eobs.api']
        task_id = int(task_id)
        task = activity_reg.read(cr, uid, task_id, ['user_id', 'data_model', 'summary', 'patient_id'], context=context)
        patient = dict()
        if task['patient_id']:
            patient_info = api_reg.get_patients(cr, uid, [task['patient_id'][0]], context=context)
            if len(patient_info) >0:
                patient_info = patient_info[0]
            patient['url'] = URLS['single_patient'] + '{0}'.format(patient_info['id'])
            patient['name'] = patient_info['full_name']
            patient['id'] = patient_info['id']
        else:
            patient = False
        form = dict()
        form['action'] = URLS['task_form_action']+'{0}'.format(task_id)
        form['type'] = task['data_model']
        form['task-id'] = int(task_id)
        form['patient-id'] = int(patient['id'])
        form['source'] = "task"
        form['start'] = datetime.now().strftime('%s')
        if task.get('user_id') and task['user_id'][0] != uid:
            return request.render('nh_eobs_mobile.error', qcontext={'error_string': 'Task is taken by another user',
                                                                     'section': 'task',
                                                                     'username': request.session['login'],
                                                                     'urls': URLS})
        try:
            api_reg.assign(cr, uid, task_id, {'user_id': uid}, context=context)
        except Exception:
            #return 'unable to take task'
            a = 0

        if 'notification' in task['data_model'] or 'placement' in task['data_model']:
            # load notification foo
            obs_reg = request.registry['nh.eobs.api']
            form_desc = obs_reg.get_form_description(cr, uid, task['patient_id'][0], task['data_model'], context=context)
            cancellable = obs_reg.is_cancellable(cr, uid, task['data_model'], context=context)
            form['confirm_url'] = "{0}{1}".format(URLS['confirm_clinical_notification'], task_id)
            form['action'] = "{0}{1}".format(URLS['confirm_clinical_notification'], task_id)
            for form_input in form_desc:
                if form_input['type'] in ['float', 'integer']:
                    form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                    form_input['type'] = 'number'
                    form_input['number'] = True
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    #if form_input['target']:
                    #    form_input['target'] = False
                elif form_input['type'] == 'selection':
                    form_input['selection_options'] = []
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    for option in form_input['selection']:
                        opt = dict()
                        opt['value'] = '{0}'.format(option[0])
                        opt['label'] = option[1]
                        form_input['selection_options'].append(opt)
            if cancellable:
                form['cancel_url'] = "{0}{1}".format(URLS['cancel_clinical_notification'], task_id)
            if 'notification' in task['data_model']:
                form['type'] = re.match(r'nh\.clinical\.notification\.(.*)', task['data_model']).group(1)
            else:
                form['type'] = 'placement'
            return request.render('nh_eobs_mobile.notification_confirm_cancel', qcontext={'name': task['summary'],
                                                                                           'inputs': form_desc,
                                                                                           'cancellable': cancellable,
                                                                                           'patient': patient,
                                                                                           'form': form,
                                                                                           'section': 'task',
                                                                                           'username': request.session['login'],
                                                                                           'urls': URLS})
        elif 'observation' in task['data_model']:
            # load obs foo
            obs_reg = request.registry['nh.eobs.api']
            form_desc = obs_reg.get_form_description(cr, uid, task['patient_id'][0], task['data_model'], context=context)
            form['type'] = re.match(r'nh\.clinical\.patient\.observation\.(.*)', task['data_model']).group(1)
            form['obs_needs_score'] = False
            for form_input in form_desc:
                if form_input['type'] in ['float', 'integer']:
                    form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                    form_input['type'] = 'number'
                    form_input['number'] = True
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    #if form_input['target']:
                    #    form_input['target'] = False
                elif form_input['type'] == 'selection':
                    form_input['selection_options'] = []
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    for option in form_input['selection']:
                        opt = dict()
                        opt['value'] = '{0}'.format(option[0])
                        opt['label'] = option[1]
                        form_input['selection_options'].append(opt)
                elif form_input['type'] == 'meta':
                    form['obs_needs_score'] = form_input['score'] if 'score' in form_input else False

            return request.render('nh_eobs_mobile.observation_entry', qcontext={'inputs': [i for i in form_desc if i['type'] is not 'meta'],
                                                                                'name': task['summary'],
                                                                                'patient': patient,
                                                                                'form': form,
                                                                                'section': 'task',
                                                                                'username': request.session['login'],
                                                                                'urls': URLS})
        else:
            return request.render('nh_eobs_mobile.error', qcontext={'error_string': 'Task is neither a notification nor an observation',
                                                                     'section': 'task',
                                                                     'username': request.session['login'],
                                                                     'urls': URLS})

    @http.route(URLS['task_form_action']+'<task_id>', type="http", auth="user")
    def process_form(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.clinical.api')
        kw_copy = kw.copy()
        del kw_copy['taskId']
        kw_copy['date_started'] = datetime.fromtimestamp(int(kw_copy['startTimestamp'])).strftime(DTF)
        del kw_copy['startTimestamp']
        api.submit_complete(cr, uid, int(task_id), kw_copy, context)
        return utils.redirect(URLS['task_list'])


    @http.route(URLS['json_task_form_action']+'<observation>/<task_id>', type="http", auth="user")
    def process_ajax_form(self, observation, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        base_api = request.registry('nh.clinical.api')
        ews_pool = request.registry('nh.clinical.patient.observation.'+observation)
        converter_pool = request.registry('ir.fields.converter')
        converter = converter_pool.for_model(cr, uid, ews_pool, str, context=context)
        kw_copy = kw.copy()
        test = {}
        timestamp = kw_copy['startTimestamp']
        device_id = kw_copy['device_id'] if 'device_id' in kw_copy else False

        del kw_copy['startTimestamp']
        if 'taskId' in kw_copy:
            del kw_copy['taskId']
        if device_id:
            del kw_copy['device_id']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        converted_data = converter(kw_copy, test)
        converted_data['date_started'] = datetime.fromtimestamp(int(timestamp)).strftime(DTF)
        if device_id:
            converted_data['device_id'] = device_id
        result = api.complete(cr, uid, int(task_id), converted_data, context)
        triggered_tasks = [v for v in base_api.activity_map(cr, uid, creator_ids=[int(task_id)]).values() if observation not in v['data_model'] and api.check_activity_access(cr, uid, v['id']) and v['state'] not in ['completed', 'cancelled']]
        return request.make_response(json.dumps({'status': 1, 'related_tasks': triggered_tasks}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['calculate_obs_score']+'<observation>', type="http", auth="user")
    def calculate_obs_score(self, observation, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        model = 'nh.clinical.patient.observation.'+observation
        converter_pool = request.registry('ir.fields.converter')
        observation_pool = request.registry(model)
        converter = converter_pool.for_model(cr, uid, observation_pool, str, context=context)
        data = kw.copy()
        test = {}
        section = 'task' if 'taskId' in data else 'patient'
        if 'startTimestamp' in data:
            del data['startTimestamp']
        if 'taskId' in data:
            del data['taskId']
        if observation == 'ews':
            observation = 'news'
            for key, value in data.items():
                if not value or key not in ['avpu_text', 'blood_pressure_systolic', 'body_temperature', 'indirect_oxymetry_spo2', 'oxygen_administration_flag', 'pulse_rate', 'respiration_rate']:
                    del data[key]
        converted_data = converter(data, test)

        score_dict = api_pool.get_activity_score(cr, uid, model, converted_data, context=context)
        modal_vals = {}
        modal_vals['next_action'] = 'json_task_form_action' if section == 'task' else 'json_patient_form_action'
        modal_vals['title'] = 'Submit {score_type} of {score}'.format(score_type=observation.upper(), score=score_dict['score'])
        if 'clinical_risk' in score_dict:
            modal_vals['content'] = '<p><strong>Clinical risk: {risk}</strong></p><p>Please confirm you want to submit this score</p>'.format(risk=score_dict['clinical_risk'])
        else:
            modal_vals['content'] = '<p>Please confirm you want to submit this score</p>'

        return request.make_response(json.dumps({'status': 3, 'score': score_dict, 'modal_vals': modal_vals}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_partial_reasons'], type="http", auth="user")
    def get_partial_reasons(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        ews_pool = request.registry('nh.clinical.patient.observation.ews')
        return request.make_response(json.dumps(ews_pool._partial_reasons), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_patient_info']+'<patient_id>', type="http", auth="user")
    def get_patient_info(self, patient_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        patient_info = api_pool.get_patients(cr, uid, [int(patient_id)], context=context)
        if len(patient_info) > 0:
            return request.make_response(json.dumps(patient_info[0]), headers={'Content-Type': 'application/json'})
        else:
            return request.make_response(json.dumps({'status': 2, 'error': 'Patient not found'}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['json_patient_barcode']+'<hospital_number>', type="http", auth="user")
    def get_patient_barcode(self, hospital_number, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        patient_info = api_pool.get_patient_info(cr, uid, hospital_number, context=context)
        if len(patient_info) > 0:
            return request.make_response(json.dumps(patient_info[0]), headers={'Content-Type': 'application/json'})
        else:
            return request.make_response(json.dumps({'status': 2, 'error': 'Patient not found'}), headers={'Content-Type': 'application/json'})

    @http.route('/ajax_test', type="http", auth="user")
    def ajax_test(self, *args, **kw):
        test_html = '<html><head><script src="{jquery}"></script><script src="{routes}"></script></head><body>Test</body></html>'.format(jquery=URLS['jquery'], routes=URLS['js_routes'])
        return test_html


    @http.route(URLS['confirm_clinical_notification']+'<task_id>', type="http", auth="user")
    def confirm_clinical(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        base_api = request.registry('nh.clinical.api')
        kw_copy = kw.copy()
        if 'taskId' in kw_copy:
            del kw_copy['taskId']
        if 'frequency' in kw_copy:
            kw_copy['frequency'] = int(kw_copy['frequency'])
        if 'location_id' in kw_copy:
            kw_copy['location_id'] = int(kw_copy['location_id'])
        result = api.complete(cr, uid, int(task_id), kw_copy)
        triggered_tasks = [v for v in base_api.activity_map(cr, uid, creator_ids=[int(task_id)]).values() if 'ews' not in v['data_model'] and api.check_activity_access(cr, uid, v['id'], context=context)]
        return request.make_response(json.dumps({'status': 1, 'related_tasks': triggered_tasks}), headers={'Content-Type': 'application/json'})

    # TODO: remove this once switch to coffeescript

    @http.route(URLS['confirm_review_frequency']+'<task_id>', type="http", auth="user")
    def confirm_review_frequency(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        base_api = request.registry('nh.clinical.api')
        kw_copy = kw.copy()
        del kw_copy['taskId']
        kw_copy['frequency'] = int(kw_copy['frequency'])
        result = api.complete(cr, uid, int(task_id), kw_copy)
        triggered_tasks = [v for v in base_api.activity_map(cr, uid, creator_ids=[int(task_id)]).values() if 'ews' not in v['data_model'] and api.check_activity_access(cr, uid, v['id'], context=context)]
        return request.make_response(json.dumps({'status': 1, 'related_tasks': triggered_tasks}), headers={'Content-Type': 'application/json'})

    # TODO: remove this once switch to coffeescript

    @http.route(URLS['confirm_bed_placement']+'<task_id>', type="http", auth="user")
    def confirm_bed_placement(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        base_api = request.registry('nh.clinical.api')
        kw_copy = kw.copy()
        del kw_copy['taskId']
        kw_copy['location_id'] = int(kw_copy['location_id'])
        result = api.complete(cr, uid, int(task_id), kw_copy)
        # triggered_tasks = [v for v in base_api.activity_map(cr, uid, creator_ids=[int(task_id)]).values() if 'ews' not in v['data_model'] and api.check_activity_access(cr, uid, v['id'], context=context)]
        return request.make_response(json.dumps({'status': 1, 'related_tasks': []}), headers={'Content-Type': 'application/json'})


    @http.route(URLS['cancel_clinical_notification']+'<task_id>', type="http", auth="user")
    def cancel_clinical(self, task_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        kw_copy = kw.copy()
        kw_copy['reason'] = int(kw_copy['reason'])
        result = api_pool.cancel(cr, uid, int(task_id), kw_copy)
        return request.make_response(json.dumps({'status':1, 'related_tasks': []}), headers={'Content-Type': 'application/json'})

    @http.route(URLS['ajax_task_cancellation_options'], type='http', auth='user')
    def cancel_reasons(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        return request.make_response(json.dumps(api_pool.get_cancel_reasons(cr, uid, context=context)), headers={'Content-Type': 'application/json'})

    @http.route(URLS['single_patient']+'<patient_id>', type='http', auth='user')
    def get_patient(self, patient_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        patient = api_pool.get_patients(cr, uid, [int(patient_id)], context=context)[0]
        obs = api_pool.get_active_observations(cr, uid, context=context)
        return request.render('nh_eobs_mobile.patient', qcontext={'patient': patient,
                                                                   'urls': URLS,
                                                                   'section': 'patient',
                                                                   'obs_list': obs,
                                                                   'username': request.session['login']})




    @http.route(URLS['ajax_get_patient_obs']+'<patient_id>', type='http', auth='user')
    def get_patient_obs(self, patient_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')
        ews = api_pool.get_activities_for_patient(cr, uid, patient_id=int(patient_id), activity_type='ews')
        return request.make_response(json.dumps({'obs': ews, 'obsType': 'ews'}), headers={'Content-Type': 'application/json'})


    @http.route(URLS['patient_ob']+'<observation>/<patient_id>', type='http', auth='user')
    def take_patient_observation(self, observation, patient_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api_pool = request.registry('nh.eobs.api')

        patient = dict()
        patient_info = api_pool.get_patients(cr, uid, [int(patient_id)], context=context)
        if len(patient_info) >0:
            patient_info = patient_info[0]
        patient['url'] = URLS['single_patient'] + '{0}'.format(patient_info['id'])
        patient['name'] = patient_info['full_name']
        patient['id'] = patient_info['id']

        form = dict()
        form['action'] = URLS['patient_form_action']+'{0}/{1}'.format(observation, patient_id)
        form['type'] = observation
        form['task-id'] = False
        form['patient-id'] = int(patient_id)
        form['source'] = "patient"
        form['start'] = datetime.now().strftime('%s')
        form['obs_needs_score'] = False

        form_desc = api_pool.get_form_description(cr, uid, int(patient_id), 'nh.clinical.patient.observation.{0}'.format(observation), context=context)

        for form_input in form_desc:
            if form_input['type'] in ['float', 'integer']:
                form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                form_input['type'] = 'number'
                form_input['number'] = True
                form_input['info'] = ''
                form_input['errors'] = ''
                #if form_input['target']:
                #    form_input['target'] = False
            elif form_input['type'] == 'selection':
                form_input['selection_options'] = []
                form_input['info'] = ''
                form_input['errors'] = ''
                for option in form_input['selection']:
                    opt = dict()
                    opt['value'] = '{0}'.format(option[0])
                    opt['label'] = option[1]
                    form_input['selection_options'].append(opt)
            elif form_input['type'] == 'meta':
                form['obs_needs_score'] = form_input['score'] if 'score' in form_input else False

        return request.render('nh_eobs_mobile.observation_entry', qcontext={'inputs': form_desc,
                                                                             'name': [v['name'] for v in api_pool._active_observations if v['type'] == observation][0],
                                                                             'patient': patient,
                                                                             'form': form,
                                                                             'section': 'patient',
                                                                             'username': request.session['login'],
                                                                             'urls': URLS})

    @http.route(URLS['json_patient_form_action']+'<observation>/<patient_id>', type='http', auth='user')
    def process_patient_observation_form(self, observation, patient_id, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        api = request.registry('nh.eobs.api')
        base_api = request.registry('nh.clinical.api')
        observation_pool = request.registry('nh.clinical.patient.observation.'+observation)
        converter_pool = request.registry('ir.fields.converter')
        converter = converter_pool.for_model(cr, uid, observation_pool, str, context=context)
        kw_copy = kw.copy()
        test = {}
        timestamp = kw_copy['startTimestamp']
        device_id = kw_copy['device_id'] if 'device_id' in kw_copy else False

        del kw_copy['startTimestamp']
        if 'taskId' in kw_copy:
            del kw_copy['taskId']
        if device_id:
            del kw_copy['device_id']
        for key, value in kw_copy.items():
            if not value:
                del kw_copy[key]

        converted_data = converter(kw_copy, test)
        converted_data['date_started'] = datetime.fromtimestamp(int(timestamp)).strftime(DTF)
        if device_id:
            converted_data['device_id'] = device_id

        new_activity = api.create_activity_for_patient(cr, uid, int(patient_id), observation, context=context)
        result = api.complete(cr, uid, int(new_activity), converted_data, context)
        triggered_tasks = [v for v in base_api.activity_map(cr, uid, creator_ids=[int(new_activity)]).values() if observation not in v['data_model'] and api.check_activity_access(cr, uid, v['id']) and v['state'] not in ['completed', 'cancelled']]
        return request.make_response(json.dumps({'status': 1, 'related_tasks': triggered_tasks}), headers={'Content-Type': 'application/json'})

    # # hack to get cookies to play nice
    # def get_response(self, httprequest, result, explicit_session):
    #     if isinstance(result, Response) and result.is_qweb:
    #         try:
    #             result.flatten()
    #         except(Exception), e:
    #             if request.db:
    #                 result = request.registry['ir.http']._handle_exception(e)
    #             else:
    #                 raise
    #
    #     if isinstance(result, basestring):
    #         response = Response(result, mimetype='text/html')
    #     else:
    #         response = result
    #
    #     if httprequest.session.should_save:
    #         self.session_store.save(httprequest.session)
    #
    #     cookie_lifespan = 3600*12 # 12 hours, maybe set in config?
    #
    #     if response.response and not isinstance(response, exceptions.HTTPException):
    #         response.set_cookie('session_id', httprequest.session.sid, max_age=cookie_lifespan)
    #     return response
    #
    # Root.get_response = get_response