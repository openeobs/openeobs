from openerp import models, fields, api

from openerp.exceptions import ValidationError


class NhClinicalPatientObservationTherapeuticLevel(models.Model):
    """
    Represents the level of therapeutic observations that a patient is intended
    to be on. The level assigned to a patient affects how therapeutic
    observations are to be performed on them.
    """
    _name = 'nh.clinical.therapeutic.level'

    levels = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
        (4, 'Level 4')
    ]
    frequencies = [
        (5, 'Every 5 Minutes'),
        (10, 'Every 10 Minutes'),
        (15, 'Every 15 Minutes'),
        (20, 'Every 20 Minutes'),
        (25, 'Every 25 Minutes'),
        (30, 'Every 30 Minutes'),
        (60, 'Every Hour')
    ]
    staff_to_patient_ratios = [
        (1, '1:1'),
        (2, '2:1'),
        (3, '3:1')
    ]

    patient = fields.Many2one(
        comodel_name='nh.clinical.patient', required=True
    )
    spell = fields.Many2one(
        comodel_name='nh.clinical.spell'
    )
    level = fields.Selection(
        required=True, selection=levels, string='Observation Level'
    )
    frequency = fields.Selection(
        selection=frequencies,
        string='Observation Recording Frequency'
    )
    staff_to_patient_ratio = fields.Selection(
        selection=staff_to_patient_ratios,
        string='Staff to patient ratio'
    )

    @api.model
    def create(self, values):
        """
        Currently frequency should always be 60 for all levels except level 2.
        This is enforced in the UI by making the frequency field read-only.

        Unfortunately Odoo does not send the value of read-only fields to the
        server so records are created with `False` for their frequency. This
        override is necessary to ensure the correct frequency is in the
        database and can therefore be used by other features.

        :param values:
        :return:
        """
        # Have to put validation here because otherwise we set it to 60 and
        # there is no error message for leaving frequency blank on level 2.
        if values['level'] == 2:
            self._validate_frequency_is_given(values['frequency'])
        if 'frequency' not in values or not values['frequency']:
            values['frequency'] = 60

        # If patient supplied then spell reference can be added.
        if 'patient' in values:
            patient_id = values['patient']
            spell_model = self.env['nh.clinical.spell']
            current_spell_activity = \
                spell_model.get_spell_activity_by_patient_id(patient_id)
            spell_id = current_spell_activity.data_ref.id
            values['spell'] = spell_id
        # If created from wardboard spell reference can still be created
        # without a patient ID because it can be retrieved from the
        # wardboard record.
        elif self.env.context.get('active_model') == 'nh.clinical.wardboard':
            wardboard_id = self.env.context['active_id']
            wardboard = self.env['nh.clinical.wardboard'].browse(wardboard_id)
            spell_id = wardboard.spell_activity_id.data_ref.id
            values['spell'] = spell_id
        else:
            raise ValueError(
                "Active model is not wardboard. Currently creation of "
                "therapeutic level records is only supported from a wardboard."
            )

        return super(NhClinicalPatientObservationTherapeuticLevel, self)\
            .create(values)

    @api.onchange('level')
    def _set_fields_based_on_level(self):
        """
        In the UI fields are hidden or shown when the user selects different
        levels, but even when a field is hidden its last value is still
        submitted to the server.

        This onchange method ensures that fields are reset to `False` everytime
        the level is changed so that no unintended values are submitted.
        """
        if self.is_level(1):
            self.frequency = False
            self.staff_to_patient_ratio = False
        elif self.is_level(2):
            self.frequency = False
            self.staff_to_patient_ratio = False
        elif self.is_level(3) or self.is_level(4):
            self.frequency = False

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

            field_defaults_dict['patient'] = patient_id
        return field_defaults_dict

    @api.model
    def fields_view_get(
            self, view_id=None, view_type=False, toolbar=False, submenu=False):
        """
        Remove 'Every 60 minutes' option from frequency dropdown. This is
        because the dropdown is only used when level 2 is selected for which
        'Every 60 minutes' is not a valid value.

        :param view_id:
        :param view_type:
        :param toolbar:
        :param submenu:
        :return:
        """
        field_view = super(NhClinicalPatientObservationTherapeuticLevel, self)\
            .fields_view_get(view_id=view_id, view_type=view_type,
                             toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            del field_view['fields']['frequency']['selection'][-1]
        return field_view

    def save(self, cr, uid, ids, context=None):
        """
        There is a 'Save' button in the 'Set Therapeutic Obs' dialog accessible
        from the patient form. This method exists purely to stop that button
        from blowing up.

        Pressing the button creates the therapeutic level
        record even without calling anything (I think the `oe_form_button_save`
        class on the button triggers an action in Odoo's JavaScript to do this)
        but if there is nothing set on the button to call then it blows up
        during module load so this method exists as a hack purely to stop that
        blow up.

        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """
        pass

    @api.constrains('level', 'frequency')
    def _validate(self):
        """
        This method is called just before the record is persisted, after the
        `create` call to validate all its fields.

        Some of the validation should not be possible to trigger via the UI and
        so exists to cover other inputs such as the API.

        :raises: openerp.exceptions.ValidationError
        """
        if self.is_level(1):
            self._validate_frequency_is_every_hour()
            self._validate_staff_to_patient_ratio_is_false()
        elif self.is_level(2):
            self._validate_staff_to_patient_ratio_is_false()
        elif self.is_level(3) or self.is_level(4):
            self._validate_frequency_is_every_hour()
            self._validate_staff_to_patient_ratio_is_given()

    def _validate_frequency_is_every_hour(self):
        if self.frequency != 60:
            raise ValidationError(
                "Frequency must be every hour for this level."
            )

    def _validate_staff_to_patient_ratio_is_false(self):
        if self.staff_to_patient_ratio is not False:
            raise ValidationError(
                "Staff to patient ratio should not be provided for this level."
            )

    @staticmethod
    def _validate_frequency_is_given(frequency):
        if not frequency:
            raise ValidationError(
                "Please fill out all fields before saving."
            )

    def _validate_staff_to_patient_ratio_is_given(self):
        if not self.staff_to_patient_ratio:
            raise ValidationError(
                "Please fill out all fields before saving."
            )

    @api.model
    def get_current_level_record_for_patient(self, patient_id):
        """
        Get the current therapeutic level record for the patient. Only returns
        level records that were set during the currently open spell. Levels
        from old ones are disregarded.

        :param patient_id:
        :type patient_id: int
        :return:
        :rtype: nh.clinical.therapeutic.level
        """
        spell_model = self.env['nh.clinical.spell']
        current_spell_activity = \
            spell_model.get_spell_activity_by_patient_id(patient_id)
        current_level_record = self.search([
            ('spell', '=', current_spell_activity.data_ref.id)
        ], order='id desc', limit=1)
        return current_level_record

    def is_level(self, level):
        """
        Indicates whether or not the record referenced by `self` has the passed
        level. If the current record represents a level 1 therapeutic obs and
        `1` is passed it will return `True`.

        :param level: A level record.
        :rtype: int
        :return:
        :rtype: bool
        """
        return self.level == self.levels[level - 1][0]

    @api.one
    def serialise(self):
        frequency = self.get_field_value_label('frequency', self.frequency)
        if self.staff_to_patient_ratio:
            staff_to_patient_ratio = self.get_field_value_label(
                'staff_to_patient_ratio', self.staff_to_patient_ratio
            )
        else:
            staff_to_patient_ratio = ''

        level_dict = {
            'id': self.id,
            'date': self.create_date,
            'level': self.level,
            'frequency': frequency,
            'staff_to_patient_ratio': staff_to_patient_ratio,
            'user': self.create_uid.name
        }
        return level_dict

    def get_field_value_label(self, field_name, field_value):
        """
        Lookup the label for the passed field value and return it.

        :param field_name:
        :type field_name: str
        :param field_value:
        :type field_value: str
        :return: Field label.
        :rtype: str
        """
        field = self._fields[field_name]
        selection = field.selection
        valid_value_tuple = \
            [valid_value_tuple for valid_value_tuple in selection
             if valid_value_tuple[0] == field_value][0]
        return valid_value_tuple[1]
