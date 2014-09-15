__author__ = 'colin'

import openerp.tests
import helpers

class TestAjaxScoreCalculation(openerp.tests.HttpCase):

    # test score calculation ajax
    def test_ajax_score_calculation(self):
        for dataset in helpers.AJAX_SCORE_CALCULATION_DATA:

            code_string = helpers.AJAX_SCORE_CALCULATION_CODE.format(respiration_rate=dataset['respiration_rate'],
                                                                     pulse_rate=dataset['pulse_rate'],
                                                                     spo2=dataset['indirect_oxymetry_spo2'],
                                                                     body_temp=dataset['body_temperature'],
                                                                     bp=dataset['blood_pressure_systolic'],
                                                                     avpu=dataset['avpu_text'],
                                                                     oxygen_flag=dataset['oxygen_administration_flag'],
                                                                     score=dataset['score'],
                                                                     clinical_risk=dataset['clinical_risk'],
                                                                     three_in_one=dataset['three_in_one'])

            self.phantom_js('/ajax_test/', code_string, 'document', login='admin')