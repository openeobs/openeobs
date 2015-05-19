__author__ = 'colinwren'
from openerp import api, models

class ObservationReport(models.AbstractModel):
    _name = 'report.nh.clinical.observation_report'

    @api.multi
    def render_html(self, data=None):
        cr, uid = self._cr, self._uid
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh.clinical.observation_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('nh_eobs.observation_report', docargs)