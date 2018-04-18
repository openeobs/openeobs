from openerp import models, fields, api

from openerp.addons.nh_observations import frequencies

from openerp.exceptions import ValidationError


class NhClinicalPatientObservationTherapeuticLevel(models.Model):

    _name = 'nh.clinical.patient.observation.therapeutic.level'

    levels = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4')
    ]
    staff_to_patient_ratios = [
        (1, '1:1'),
        (1, '2:1'),
        (1, '3:1')
    ]

    patient = fields.Many2one(
        comodel_name='nh.clinical.patient', required=True
    )
    level = fields.Selection(
        required=True, selection=levels
    )
    frequency = fields.Selection(selection=frequencies.as_list())
    staff_to_patient_ratio = fields.Selection(
        selection=staff_to_patient_ratios
    )

    @api.onchange('level')
    def _update_other_fields(self):
        if self.level == self.levels[0][0]:
            self.frequency = 60
            self.staff_to_patient_ratio = False
        elif self.level == self.levels[1][0]:
            current_level_record = self.get_current_level_record_for_patient(
                self.patient.id
            )
            self.frequency = current_level_record.frequency \
                if current_level_record else False
            self.staff_to_patient_ratio = False
        elif self.level == self.levels[2][0] \
                or self.level == self.levels[3][0]:
            self.frequency = False
            current_level_record = self.get_current_level_record_for_patient(
                self.patient.id
            )
            self.staff_to_patient_ratio = \
                current_level_record.staff_to_patient_ratio \
                if current_level_record else False

    def default_get(self, cr, uid, fields, context=None):
        """
        Ensure that the patient field is pre-populated on the form view when
        creating a new level record from the wardboard view.

        :param cr:
        :param uid:
        :param fields:
        :param context:
        :return:
        """
        field_defaults_dict = \
            super(NhClinicalPatientObservationTherapeuticLevel, self)\
            .default_get(cr, uid, fields, context=None)

        if 'active_id' in context \
                and 'active_model' in context \
                and context['active_model'] == 'nh.clinical.wardboard':
            wardboard_model = self.pool['nh.clinical.wardboard']
            wardboard = wardboard_model.browse(cr, uid, context['active_id'])
            patient_id = wardboard.patient_id.id

            current_level_record = \
                self.get_current_level_record_for_patient(
                    cr, uid, patient_id, context=context)
            default_level = current_level_record.level \
                if current_level_record else self.levels[0][0]

            field_defaults_dict['level'] = default_level
            field_defaults_dict['patient'] = patient_id
        return field_defaults_dict

    def save(self, cr, uid, ids, context=None):
        """
        There is a 'Save' button in the 'Set Therapeutic Obs' dialog accessible
        from the patient form. This method exists purely to stop that button
        from blowing up.

        Pressing the button creates the therapeutic level
        record even without calling anything (I think the `oe_form_button_save`
        class on the button triggers an action in Odoo's JavaScript) but if
        there is nothing set on the button to call then it blows up during
        module load.

        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        pass

    @api.constrains('level', 'frequency')
    def _validate(self):
        self._validate_frequency_is_every_hour_on_level_1()
        self._validate_frequency_is_not_set_for_level_3_or_4()

    def _validate_frequency_is_every_hour_on_level_1(self):
        every_hour = 60
        if self.level == self.levels[0][0] \
                and self.frequency != every_hour:
            raise ValidationError(
                "Frequency must be {} when setting level 1.".format(every_hour)
            )

    def _validate_frequency_is_not_set_for_level_3_or_4(self):
        if self.level == self.levels[2][0] or self.level == self.levels[3][0] \
                and self.frequency:
            raise ValidationError(
                "No frequency should be set for level 3 or 4."
            )

    @api.model
    def get_current_level_record_for_patient(self, patient_id):
        current_level_record = self.search([
            ('patient', '=', patient_id)
        ], order='id desc', limit=1)
        return current_level_record
