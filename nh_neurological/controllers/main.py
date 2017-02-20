# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.http import request

URL_PREFIX = '/mobile/'


class NeuroMobileFrontend(MobileFrontend):

    @staticmethod
    @http.route(
        URL_PREFIX + 'src/html/pupil_size_chart.html',
        type="http", auth="none")
    def pupil_size_chart():
        return request.render('nh_neurological.pupil_size_reference',
                              qcontext={})
