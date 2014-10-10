# -*- coding: utf-8 -*-s
import openerp, re, json, jinja2, bisect, time
from openerp.addons.nh_eobs_mobile.controllers import urls
from openerp import http
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request
from werkzeug import utils, exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


URL_PREFIX = '/mobile/'
URLS = urls.URLS


db_list = http.db_list

db_monodb = http.db_monodb

loader = jinja2.FileSystemLoader(get_module_path('nh_eobs_mobile_theme_block') + '/views/')
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


class BlockStyleFrontend(openerp.addons.nh_eobs_mobile.controllers.main.MobileFrontend):

    @http.route(URLS['stylesheet'], type='http', auth='none')
    def get_stylesheet(self, *args, **kw):
        with open(get_module_path('nh_eobs_mobile_theme_block') + '/static/src/css/blockstyle.css', 'r') as stylesheet:
            return request.make_response(stylesheet.read(), headers={'Content-Type': 'text/css; charset=utf-8'})

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
            return request.make_response(login_template.render(stylesheet=URLS['stylesheet'], logo=URLS['logo'], form_action=URLS['login'], errors='', databases=values['databases']))
        if request.httprequest.method == 'POST':
            database = values['database'] if 'database' in values else False
            if database:
                uid = request.session.authenticate(database, request.params['username'], request.params['password'])
                if uid is not False:
                    request.uid = uid
                    return utils.redirect(URLS['task_list'], 303)
            return request.make_response(login_template.render(stylesheet=URLS['stylesheet'], logo=URLS['logo'], form_action=URLS['login'], errors='<div class="alert alert-error">Invalid username/password</div>', databases=values['databases']))

    @http.route(URLS['logout'], type='http', auth="user")
    def mobile_logout(self, *args, **kw):
        request.session.logout()
        return utils.redirect(URLS['login'], 303)

    def calculate_ews_class(self, score):
        if score == 'None':
            return 'white'
        elif score == 'Low':
            return 'green'
        elif score == 'Medium':
            return 'yellow'
        elif score == 'High':
            return 'orange'
        else:
            return 'orange'



    def convert_task_deadline(self, deadline):
        time_diff = int(time.mktime(datetime.strptime(deadline, DTF).timetuple()) - time.mktime(datetime.now().timetuple())) / 60
        if time_diff < 60:
            if time_diff < 0:
                if time_diff < -60:
                    return ['{hours}H {minutes}M'.format(hours=int((time_diff*-1)/60), minutes=int(time_diff%60)), True]
                else:
                    return ['{minutes}M'.format(minutes=(time_diff*-1)), True]
            else:
                return ['{minutes}M'.format(minutes=time_diff), False]
        else:
            return ['{hours}H {minutes}M'.format(hours=int(time_diff/60), minutes=int(time_diff%60)), False]


    @http.route(URLS['task_list'], type='http', auth='user')
    def get_tasks(self, *args, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        task_api = request.registry['nh.eobs.api']
        tasks = task_api.get_activities(cr, uid, [], context=context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(URLS['single_task'], task['id'])
            task['color'] = self.calculate_ews_class(task['clinical_risk'])
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task_deadline = self.convert_task_deadline(task['deadline'])
            task['deadline_time'] = task_deadline[0]
            task['overdue'] = task_deadline[1]

            # return super(BlockStyleFrontend, self).get_tasks(args, kw)

        return request.render('nh_eobs_mobile_theme_block.task_list', qcontext={'items': tasks,
                                                                            'section': 'task',
                                                                            'username': request.session['login'],
                                                                            'urls': URLS})


    @http.route(URLS['patient_list'], type='http', auth="user")
    def get_patients(self, *args, **kw):
        cr, uid, context = request.cr, request.session.uid, request.context
        patient_api = request.registry['nh.eobs.api']
        patients = patient_api.get_patients(cr, uid, [], context=context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(URLS['single_patient'], patient['id'])
            patient['color'] = self.calculate_ews_class(patient['clinical_risk'])
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            task_deadline = ['mehH', False] # self.convert_task_deadline(patient['deadline'])
            patient['deadline_time'] = task_deadline[0]
            patient['overdue'] = task_deadline[1]
            patient['summary'] = patient['summary'] if patient.get('summary') else False
        return request.render('nh_eobs_mobile_theme_block.patient_list', qcontext={'items': patients,
                                                                                   'section': 'patient',
                                                                                   'username': request.session['login'],
                                                                                   'urls': URLS})


    @http.route('/mobile/src/img/<xmlid>', auth='none', type='http')
    def get_image(self, xmlid, *args, **kw):
        with open(get_module_path('nh_eobs_mobile_theme_block') + '/static/src/img/' + xmlid, 'r') as image:
            return request.make_response(image.read(), headers={'Content-Type': 'image/png'})

