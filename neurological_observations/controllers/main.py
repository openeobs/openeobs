# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend

URL_PREFIX = '/mobile/'


class NeuroMobileFrontend(MobileFrontend):

    @http.route(
        URL_PREFIX + 'src/html/pupil_size_chart.html',
        type="http", auth="none")
    def pupil_size_chart(self, *args, **kw):
        return request.render(
            'neurological_observations.pupil_size_reference', qcontext={})
