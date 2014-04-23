import openerp.addons.web.http as http
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

    @http.httprequest
    def activities(self, req, **kw):
        regex = re.compile('/api/activities/(\d+)?/?(assign|complete)?/?')
        path = req.httprequest.path
        result = regex.match(path).groups()
        method = req.httprequest.method
        json_result = json.dumps({'params': result, 'method': method})
        return json_result

    @http.httprequest
    def patients(self, req, **kw):
        regex = re.compile('/api/patients/(\d+)?/?(admit|merge|transfer|activities)?/?(\d+|\w+)?/?(view|frequency)?/?')
        path = req.httprequest.path
        result = regex.match(path).groups()
        method = req.httprequest.method
        json_result = json.dumps({'params': result, 'method': method})
        return json_result