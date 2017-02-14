# -*- coding: utf-8 -*-
from openerp.tests.common import HttpCase


class TestPupilReferenceChart(HttpCase):

    def setUp(self):
        super(TestPupilReferenceChart, self).setUp()
        self.authenticate('nasir', 'nasir')
        self.url = '/mobile/src/html/pupil_size_chart.html'

    def test_returns_200(self):
        response = self.url_open(self.url)
        self.assertEqual(200, response.code)

    def test_returns_html(self):
        response = self.url_open(self.url)
        self.assertEqual('text/html', response.header.type)
