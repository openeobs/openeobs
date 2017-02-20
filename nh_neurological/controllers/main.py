# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.http import request

URL_PREFIX = '/mobile/'


class NeuroMobileFrontend(MobileFrontend):

    @http.route(
        URL_PREFIX + 'src/html/pupil_size_chart.html',
        type="http", auth="none")
    def pupil_size_chart(self, *args, **kwargs):
        """
        URL to render the pupil size chart HTML so it can be displayed in an
        iframe for the Pupil Size Reference Chart

        :param args: URL arguments
        :param kwargs: query string arguments for route
        :return: HTTP Response
        """
        return request.render('nh_neurological.pupil_size_reference',
                              qcontext={})
