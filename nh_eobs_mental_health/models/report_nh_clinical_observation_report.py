from openerp import models


class MentalHealthObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        """
        Returns a dictionary that will be used to populate the report.
        Most of the values are themselves dictionaries returned by
        `activity.read()`. However they also have an additional key named
        'values' that contains the model record as dictionaries returned by
        `model.read()`.

        :param data:
        :param ews_only:
        :return:
        :rtype: dict
        """
        report_data = super(MentalHealthObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)
        report_data['draw_graph_js'] = \
            '/nh_eobs_mental_health/static/src/js/observation_report.js'
        return report_data