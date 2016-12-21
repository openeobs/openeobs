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

    def get_refusal_episodes(self, spell_activity_id):
        """
        Collect the refusal episodes for the spell provided

        :param spell_id: Spell Id for the patient
        :return: list of dicts
        :rtype: list
        """
        self._cr.execute("""
        SELECT * FROM refused_review_chain WHERE spell_activity_id = {0};
        """.format(spell_activity_id))
        return self._cr.dictfetchall()

    def init(self, cr):
        """
        Create or replace the refused_chain_count table for use in
        get_refusal_episodes

        :param cr: Odoo cursor
        """
        sql_model = self.pool['nh.clinical.sql']
        cr.execute("""
        CREATE OR REPLACE VIEW refused_chain_count AS ({refused_chain_sql});
        CREATE OR REPLACE VIEW refused_review_chain AS ({refused_review});
        """.format(
            refused_chain_sql=sql_model.get_refused_chain_count_sql(),
            refused_review=sql_model.get_refused_review_chain_sql()
        ))
