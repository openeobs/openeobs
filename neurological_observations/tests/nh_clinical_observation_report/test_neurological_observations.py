# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report.helpers import DataObj
from openerp.tests.common import TransactionCase


class TestGetNeurologicalObservations(TransactionCase):

    def setUp(self):
        super(TestGetNeurologicalObservations, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.report_model = self.env['report.nh.clinical.observation_report']

        self.datetime_start = datetime.now() + timedelta(days=1)
        self.datetime_end = datetime.now() + timedelta(days=2)
        self.data = DataObj(self.spell_activity.id,
                            self.datetime_start, self.datetime_end)

    def test_returns_list(self):
        neurological_observations = self.report_model.get_neurological_observations()
        self.assertTrue(type(neurological_observations) is list)

    def test_no_start_or_end_datetime(self):
        pass

    def test_start_datetime(self):
        pass

    def test_end_date_time(self):
        pass

    def test_start_and_end_datetime(self):
        pass
