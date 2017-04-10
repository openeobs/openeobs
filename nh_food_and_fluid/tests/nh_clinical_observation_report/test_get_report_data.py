# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetReportData(TransactionCase):
    """Test the `get_report_data` method override for food and fluid."""
    def setUp(self):
        super(TestGetReportData, self).setUp()
        test_utils = self.env['nh.clinical.test_utils']
        test_utils.admit_and_place_patient()
        test_utils.copy_instance_variables(self)

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']

        datetime_start = datetime.now() - timedelta(days=2)
        datetime_end = datetime.now()
        self.report_wizard = self.report_wizard_model.create({
            'start_time': datetime_start.strftime(DTF),
            'end_time': datetime_end.strftime(DTF),
        })
        self.report_wizard.spell_id = self.spell.id

        test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=100,
            completion_datetime=datetime.now() - timedelta(days=1)
        )
        self.report_data = \
            self.report_model.get_report_data(self.report_wizard)

    def test_has_food_and_fluid_key(self):
        """The report data dictionary has a `food_and_fluid` key."""
        self.assertTrue(isinstance(self.report_data, dict))
        self.assertTrue('food_and_fluid' in self.report_data)

    def test_food_and_fluid_key_has_list_value(self):
        """Food and fluid key has a list value."""
        food_and_fluid_data = self.report_data['food_and_fluid']
        self.assertTrue(isinstance(food_and_fluid_data, list))
