# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
from datetime import datetime
import base64
from openerp.osv import osv, fields
import logging
_logger = logging.getLogger(__name__)
from openerp.exceptions import AccessError


class print_observation_report_wizard(osv.TransientModel):

    _name = 'nh.clinical.observation_report_wizard'
    _columns = {
        'start_time': fields.datetime('Start Time'),
        'end_time': fields.datetime('End Time'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)
        data.spell_id = context['active_id']

        spell_pool = self.pool['nh.clinical.spell']
        patient_pool = self.pool['nh.clinical.patient']
        # get PDF version of the report
        report_pool = self.pool['report']
        report_pdf = report_pool.get_pdf(
            cr, uid, ids, 'nh.clinical.observation_report',
            data=data, context=context)
        attachment_id = None
        #
        # save it as an attachment in the Database
        # Use the spell ID to find the patient's NHS number
        spell = spell_pool.read(cr, uid, [data.spell_id])[0]
        patient_id = spell['patient_id'][0]
        patient = patient_pool.read(cr, uid, patient_id)
        patient_nhs = patient['patient_identifier']
        attachment = {
            'name': 'nh.clinical.observation_report',
            'datas': base64.encodestring(report_pdf),
            'datas_fname': '{nhs}_{date}_observation_report.pdf'.format(
                nhs=patient_nhs, date=datetime.strftime(
                    datetime.now(), '%Y%m%d')),
            'res_model': 'nh.clinical.observation_report_wizard',
            'res_id': ids[0],
        }
        try:
            attachment_id = self.pool['ir.attachment'].create(
                cr, uid, attachment)
        except AccessError:
            _logger.warning(
                'Cannot save PDF report %r as attachment', attachment['name'])
        else:
            _logger.info(
                'The PDF document %s is now saved in the database',
                attachment['name'])
        return {
            'type': 'ir_actions_action_nh_clinical_download_report',
            'id': attachment_id,
        }
