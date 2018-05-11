from openerp import models, fields, api


class NhClinicalWardboard(models.Model):
    """
    Override to add information about the patient's current therapeutic level.
    """
    _inherit = 'nh.clinical.wardboard'

    therapeutic_level = fields.Char(
        size=20,
        compute='_set_therapeutic_fields'
    )
    therapeutic_frequency = fields.Char(
        size=50,
        compute='_set_therapeutic_fields'
    )
    therapeutic_staff_to_patient_ratio = fields.Char(
        size=20,
        compute='_set_therapeutic_fields'
    )

    @api.depends('patient_id')
    def _set_therapeutic_fields(self):
        for record in self:
            current_therapeutic_level = \
                record._get_latest_therapeutic_level_record()
            if not current_therapeutic_level:
                record.therapeutic_level = 'Not set'
                return

            self._set_therapeutic_level(record, current_therapeutic_level)
            self._set_therapeutic_frequency(record, current_therapeutic_level)
            self._set_therapeutic_staff_to_patient_ratio(
                record, current_therapeutic_level
            )

    def _get_latest_therapeutic_level_record(self):
        therapeutic_level_model = self.env['nh.clinical.therapeutic.level']
        current_therapeutic_level = \
            therapeutic_level_model.get_current_level_record_for_patient(
                self.patient_id.id
            )
        return current_therapeutic_level

    @staticmethod
    def _set_therapeutic_level(record, current_therapeutic_level):
        therapeutic_level = current_therapeutic_level.level
        record.therapeutic_level = therapeutic_level

    def _set_therapeutic_frequency(self, record, current_therapeutic_level):
        therapeutic_level_model = self.env['nh.clinical.therapeutic.level']
        frequency_int = current_therapeutic_level.frequency
        frequencies = therapeutic_level_model.frequencies

        # Lookup display string using integer.
        frequency_selection = filter(
            lambda frequency: frequency[0] == frequency_int, frequencies
        )[0]
        frequency_str = frequency_selection[1]
        record.therapeutic_frequency = frequency_str

    def _set_therapeutic_staff_to_patient_ratio(
            self, record, current_therapeutic_level):
        if not current_therapeutic_level.staff_to_patient_ratio:
            return

        therapeutic_level_model = self.env['nh.clinical.therapeutic.level']
        staff_to_patient_ratio_int = \
            current_therapeutic_level.staff_to_patient_ratio
        staff_to_patient_ratios = \
            therapeutic_level_model.staff_to_patient_ratios

        # Lookup display string using integer.
        staff_to_patient_ratio_selection = filter(
            lambda staff_to_patient_ratio:
            staff_to_patient_ratio[0] == staff_to_patient_ratio_int,
            staff_to_patient_ratios
        )[0]
        staff_to_patient_ratio_str = staff_to_patient_ratio_selection[1]
        record.therapeutic_staff_to_patient_ratio = staff_to_patient_ratio_str
