from openerp import models, fields, api

from openerp.addons.nh_observations import frequencies
from openerp.addons.nh_odoo_fixes import validate

from openerp.exceptions import ValidationError


class NhClinicalPatientObservationTherapeuticLevel(models.Model):

    _name = 'nh.clinical.patient.observation.therapeutic.level'

    patient = fields.Many2one(
        comodel_name='nh.clinical.patient', required=True
    )
    level = fields.Selection(
        required=True, selection=[
            'Level 1',
            'Level 2',
            'Level 3'
        ],
        default=1
    )
    frequency = fields.Selection(selection=frequencies.as_list())

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
            field_defaults_dict['patient'] = wardboard.patient_id.id
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
        # self._validate_level_range()
        self._validate_frequency_is_only_set_on_level_2()

    def _validate_level_range(self):
        validate.in_min_max_range(1, 3, self.level)

    def _validate_frequency_is_only_set_on_level_2(self):
        if self.level == 'Level 2' and not self.frequency:
            raise ValidationError("Must have a frequency set for level 2 "
                                  "therapeutic obs.")
