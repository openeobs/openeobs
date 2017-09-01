# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.addons.nh_eobs_api.routing import Route
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.http import request

route_toggle_rapid_tranq = Route(
    'rapid_tranq',
    '/patient/<patient_id>/rapid_tranq',
    methods=['GET', 'POST'],
    url_prefix='/mobile'
)
route_manager.add_route(route_toggle_rapid_tranq)


class MobileFrontendMentalHealth(MobileFrontend):

    @http.route(**route_manager.expose_route('rapid_tranq'))
    def rapid_tranq(self, *args, **kwargs):
        """
        Endpoint for reading and writing the `rapid_tranq` field on a patient's
        spell.

        Let's the API model create the JSON encoded response and simply wraps
        it in a response object to be returned to the client.

        :param args:
        :param kwargs:
        :return:
        """
        api_model = request.registry('nh.eobs.api')
        response = api_model.set_rapid_tranq(request.cr, request.uid, request,
                                             **kwargs)
        return request.make_response(response,
                                     headers=ResponseJSON.HEADER_CONTENT_TYPE)
