# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import openerp
from openerp import http
from openerp.http import request

class WebSocketTest(openerp.addons.web.controllers.main.Home):

    @http.route('/websocket', type='http', auth='none')
    def websocket_home(self, *args, **kw):
        meh = open("/opt/deploy/nhclinical/deps/nh_eobs/nh_eobs_dev/plot_graph.html", 'r').read()
        return request.make_response(meh)