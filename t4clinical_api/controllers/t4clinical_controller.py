import openerp.addons.web.http as http
import openerp.modules.registry
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
                    <p>meh!</p>
                </body>
            </html>
        """
        return SIMPLE_TEMPLATE

    def get_dbname(self, req):
        dbname = 't4clinical_default_config'
        return dbname

    def get_uid(self, req, registry):
        uid = 1
        return uid

    @http.httprequest
    def activities(self, req, **kw):
        dbname = self.get_dbname(req)
        registry = openerp.modules.registry.RegistryManager.get(dbname)
        cr = registry.db.cursor()
        uid = self.get_uid(req, registry)
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
                result = api.getActivities(cr, uid, [activity_id] if activity_id else [], context)
            elif method == 'DELETE':
                result = api.cancel(cr, uid, activity_id, context)
            elif method == 'POST':
                # result = api.submit(cr, uid, activity_id, kw, context)
                dummy = 1
        elif params[1] == 'assign':
            # /api/activities/activity_id/assign/
            if method == 'DELETE':
                # result = api.unassign(cr, uid, activity_id, context)
                dummy = 1
            elif method == 'POST':
                # result = api.assign(cr, uid, activity_id, kw, context)
                dummy = 1
        elif params[1] == 'complete':
            # /api/activities/activity_id/complete/
            if method == 'POST':
                # result = api.complete(cr, uid, activity_id, kw, context)
                dummy = 1

        json_result = json.dumps({'params': params, 'method': method, 'result': result})
        return json_result

    @http.httprequest
    def patients(self, req, **kw):
        dbname = self.get_dbname(req)
        registry = openerp.modules.registry.RegistryManager.get(dbname)
        cr = registry.cursor()
        uid = self.get_uid(req, registry)
        api = registry.get('t4.clinical.api')
        context = req.context

        regex = re.compile('/api/patients/(\d+)?/?(admit|merge|transfer|activities)?/?(\d+|\w+)?/?(view|frequency)?/?')
        path = req.httprequest.path
        params = regex.match(path).groups()
        method = req.httprequest.method
        patient_id = int(params[0]) if params[0] else 0
        activity_type = params[2]

        if not params[1]:
            # /api/patients/patient_id/
            if method == 'GET':
                # result = api.getPatients(cr, uid, [patient_id] if patient_id else [], context)
                dummy = 1
            elif method == 'PUT':
                # result = api.update(cr, uid, patient_id, kw, context)
                dummy = 1
            elif method == 'POST':
                # result = api.register(cr, uid, kw, context)
                dummy = 1
        elif params[1] == 'admit':
            if method == 'POST':
                # result = api.admit(cr, uid, patient_id, kw, context)
                dummy = 1
            elif method == 'DELETE':
                # result = api.discharge(cr, uid, patient_id, context)
                dummy = 1
        elif params[1] == 'merge':
            if method == 'PUT':
                # result = api.merge(cr, uid, patient_id, kw, context)
                dummy = 1
        elif params[1] == 'transfer':
            if method == 'PUT':
                # result = api.transfer(cr, uid, patient_id, kw, context)
                dummy = 1
        elif params[1] == 'activities':
            if not params[3]:
                if method == 'GET':
                    # result = api.getActivitiesForPatient(cr, uid, patient_id, activity_type, context)
                    dummy = 1
                elif method == 'POST':
                    # result = api.createActivity(cr, uid, patient_id, activity_type, context)
                    dummy = 1
            elif params[3] == 'view':
                if method == 'GET':
                    # result = api.formDescription(cr, uid, patient_id, activity_type, context)
                    dummy = 1
            elif params[3] == 'frequency':
                if method == 'GET':
                    # result = api.getFrequency(cr, uid, patient_id, activity_type, context)
                    dummy = 1
                elif method == 'POST':
                    # result = api.setFrequency(cr, uid, patient_id, activity_type, kw, context)
                    dummy = 1

        json_result = json.dumps({'params': params, 'method': method})
        return json_result