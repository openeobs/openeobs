# -*- coding: utf-8 -*-
__author__ = 'colinwren'
import openerp
from openerp import http
from openerp.http import request

URL_PREFIX = '/mobile/'

class MobileFrontend(openerp.addons.nh_eobs_mobile.controllers.main.MobileFrontend):

    @http.route(URL_PREFIX + 'src/html/pupil_size_chart.html', type="http", auth="none")
    def pupil_size_chart(self, *args, **kw):
        return request.render('neurological_observations.pupil_size_reference', qcontext={})
