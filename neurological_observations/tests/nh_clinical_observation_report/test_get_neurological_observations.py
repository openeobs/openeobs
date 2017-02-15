# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetNeurologicalObservations(TransactionCase):

    def setUp(self):
        super(TestGetNeurologicalObservations, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.report_wizard_model = self.env[
            'nh.clinical.observation_report_wizard']
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.datetime_start = datetime.now() - timedelta(days=2)
        self.datetime_end = datetime.now() - timedelta(days=1)

        self.report_wizard = self.report_wizard_model.create({
            'start_time': self.datetime_start.strftime(DTF),
            'end_time': self.datetime_end.strftime(DTF)
        })
        self.report_model.spell_activity_id = self.spell_activity.id

    def test_returns_list(self):
        neurological_observations = \
            self.report_model.get_neurological_observations(self.report_wizard)
        self.assertTrue(type(neurological_observations) is list)

