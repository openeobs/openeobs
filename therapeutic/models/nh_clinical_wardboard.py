from openerp import models, fields, api


class NhClinicalWardboard(models.Model):

    _inherit = 'nh.clinical.wardboard'

    therapeutic_level = fields.Integer(
        compute='_get_current_therapeutic_level')
    therapeutic_frequency = fields.Char(
        compute='_get_current_therapeutic_frequency')

    @api.depends('patient_id')
    def _get_current_therapeutic_level(self):
        for record in self:
            current_therapeutic_level = \
                record._get_latest_therapeutic_level_record()
            record.therapeutic_level = current_therapeutic_level.level

    @api.depends('patient_id')
    def _get_current_therapeutic_frequency(self):
        for record in self:
            current_therapeutic_level = \
                record._get_latest_therapeutic_level_record()
            frequency_display = '{} min(s)'.format(
                current_therapeutic_level.frequency)
            record.therapeutic_frequency = frequency_display

    def _get_latest_therapeutic_level_record(self):
        domain = [
            ('patient', '=', self.patient_id.id)
        ]
        therapeutic_level_model = \
            self.env['nh.clinical.patient.observation.therapeutic.level']
        current_therapeutic_level = therapeutic_level_model.search(
            domain, order='id desc', limit=1)
        return current_therapeutic_level
