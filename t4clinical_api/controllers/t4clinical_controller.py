import openerp.addons.web.http as http
import openerp.modules.registry
from openerp.service.http_server import OpenERPAuthProvider
from openerp import SUPERUSER_ID
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.service import web_services
import re
import json


class T4clinicalController(http.Controller):
    _cp_path = '/api'

    @http.httprequest
    def index(self, req, s_action=None, **kw):
        SIMPLE_TEMPLATE = """
            <html>
                <head>
                    <title>T4Clinical API</title>
                </head>
                <body>
                    <p>T4Clinical API:</p>
                    <p>GET /api/activities/activity_id/ = get activity/ies</p>
                    <p>DELETE /api/activities/activity_id/ = cancel activity</p>
                    <p>POST /api/activities/activity_id/ = submit activity</p>
                </body>
            </html>
        """
        return SIMPLE_TEMPLATE

    def get_dbname(self, req):
        dbname = filter(lambda x: x is not False, [req.httprequest.session[k]._db for k in req.httprequest.session.keys()])[0]
        return dbname

    def get_uid(self, req):
        uid = filter(lambda x: x is not False, [req.httprequest.session[k]._uid for k in req.httprequest.session.keys()])[0]
        return uid

    # @http.httprequest
    # def login(self, req, **kw):
    #     if req.httprequest.method != 'POST':
    #         return False
    #     username = kw.get('username')
    #     if not username:
    #         raise osv.except_osv(_('Error!'), 'User not found.')
    #     pw = kw.get('password')
    #     if not pw:
    #         raise osv.except_osv(_('Error!'), 'Incorrect password.')
    #     dbname = kw.get('dbname')
    #     if not dbname:
    #         raise osv.except_osv(_('Error!'), 'Database not found.')
    #     context = req.context
    #
    #     db = web_services.db()
    #     if not db.exp_db_exist('t4clinical_apikeys'):
    #         db.exp_drop('t4clinical_apikeys')
    #         db.exp_create_database('t4clinical_apikeys', False, 'en_GB')
    #         openerp.modules.registry.RegistryManager.get(db)
    #         obj = openerp.osv.osv.object_proxy()
    #         ids = obj.execute(db, 1, 'ir.module.module', 'search', [('name', '=', 't4clinical_api')])
    #         obj.execute(db, 1, 'ir.module.module', 'button_immediate_install', ids)
    #
    #     if not db.exp_db_exist(dbname):
    #         raise osv.except_osv(_('Error!'), 'Database not found.')
    #     registry = openerp.modules.registry.RegistryManager.get(dbname)
    #     cr = registry.db.cursor()
    #     user_pool = registry.get('res.users')
    #     user_ids = user_pool.search(cr, SUPERUSER_ID, [('login', '=', username)], context=context)
    #     if not user_ids:
    #         raise osv.except_osv(_('Error!'), 'User not found.')
    #     uid = user_ids[0]
    #     cr.close()
    #     return True

    @http.httprequest
    def activities(self, req, **kw):
        dbname = self.get_dbname(req)
        registry = openerp.modules.registry.RegistryManager.get(dbname)
        cr = registry.db.cursor()
        uid = self.get_uid(req)
        api = registry.get('t4.clinical.api')
        context = req.context

        regex = re.compile('/api/activities/(\d+)?/?(assign|complete)?/?')
        path = req.httprequest.path
        params = regex.match(path).groups()
        method = req.httprequest.method
        activity_id = int(params[0]) if params[0] else 0
        result = None

        if not params[1]:
            # /api/activities/activity_id/
            if method == 'GET':
                result = api.get_activities(cr, uid, [activity_id] if activity_id else [], context)
            elif method == 'DELETE':
                result = api.cancel(cr, uid, activity_id, context)
            elif method == 'POST':
                result = api.submit(cr, uid, activity_id, kw, context)
        elif params[1] == 'assign':
            # /api/activities/activity_id/assign/
            if method == 'DELETE':
                result = api.unassign(cr, uid, activity_id, context)
            elif method == 'POST':
                result = api.assign(cr, uid, activity_id, kw, context)
        elif params[1] == 'complete':
            # /api/activities/activity_id/complete/
            if method == 'POST':
                result = api.complete(cr, uid, activity_id, kw, context)

        json_result = json.dumps({'params': params, 'method': method, 'result': result})
        cr.close()
        return json_result

    @http.httprequest
    def patients(self, req, **kw):
        dbname = self.get_dbname(req)
        registry = openerp.modules.registry.RegistryManager.get(dbname)
        cr = registry.db.cursor()
        uid = self.get_uid(req)
        api = registry.get('t4.clinical.api')
        context = req.context

        regex = re.compile('/api/patients/(\d+)?/?(admit|discharge|merge|transfer|activities)?/?(\d+|\w+)?/?(view|frequency)?/?')
        path = req.httprequest.path
        params = regex.match(path).groups()
        method = req.httprequest.method
        patient_id = int(params[0]) if params[0] else 0
        activity_type = params[2]
        result = None

        if not params[1]:
            # /api/patients/patient_id/
            if method == 'GET':
                result = api.get_patients(cr, uid, [patient_id] if patient_id else [], context)
            elif method == 'PUT':
                result = api.update(cr, uid, patient_id, kw, context)
            elif method == 'POST':
                result = api.register(cr, uid, kw, context)
        elif params[1] == 'admit':
            # /api/patients/patient_id/admit/
            if method == 'POST':
                result = api.admit(cr, uid, patient_id, kw, context)
            elif method == 'DELETE':
                result = api.cancel_admit(cr, uid, patient_id, context)
        elif params[1] == 'discharge':
            # /api/patients/patient_id/discharge/
            if method == 'POST':
                result = api.discharge(cr, uid, patient_id, context)
            elif method == 'DELETE':
                result = api.cancel_discharge(cr, uid, patient_id, context)
        elif params[1] == 'merge':
            # /api/patients/patient_id/merge/
            if method == 'PUT':
                result = api.merge(cr, uid, patient_id, kw, context)
        elif params[1] == 'transfer':
            # /api/patients/patient_id/transfer/
            if method == 'PUT':
                result = api.transfer(cr, uid, patient_id, kw, context)
            elif method == 'DELETE':
                result = api.cancel_transfer(cr, uid, patient_id, context)
        elif params[1] == 'activities':
            if not params[3]:
                # /api/patients/patient_id/activities/ or /api/patients/patient_id/activities/activity_type/
                if method == 'GET':
                    result = api.get_activities_for_patient(cr, uid, patient_id, activity_type, context=context)
                elif method == 'POST':
                    result = api.create_activity_for_patient(cr, uid, patient_id, activity_type, context)
            elif params[3] == 'view':
                # /api/patients/patient_id/activities/activity_type/view/
                if method == 'GET':
                    # result = api.formDescription(cr, uid, patient_id, activity_type, context)
                    result = 1
            elif params[3] == 'frequency':
                # /api/patients/patient_id/activities/activity_type/frequency/
                if method == 'GET':
                    result = api.get_frequency(cr, uid, patient_id, activity_type, context)
                elif method == 'POST':
                    result = api.set_frequency(cr, uid, patient_id, activity_type, kw, context)

        json_result = json.dumps({'params': params, 'method': method, 'result': result})
        cr.close()
        return json_result