# -*- coding: utf-8 -*-
from openerp.tests.common import HttpCase


class TestTakePatientObservation(HttpCase):
    def setUp(self):
        super(TestTakePatientObservation, self).setUp()
        with self.cursor() as cr:
            env = self.env(cr)
            self.test_utils = env['nh.clinical.test_utils']
            self.test_utils.admit_and_place_patient()
            self.test_utils.copy_instance_variables(self)

    def test_return(self):
        self.authenticate('nasir', 'nasir')
        url = '/mobile/patient/observation/food_fluid/1'.format(self.patient.id)
        response = self.url_open(url, timeout=60)
        pass
        self.assertEquals(200, response.code)
