from openerp import models, api

from openerp.addons.nh_observations import fields as obs_fields


class NhClinicalPatientObservationTherapeutic(models.Model):

    _name = 'nh.clinical.patient.observation.therapeutic'
    _inherit = 'nh.clinical.patient.observation'

    _patient_status_selection = [
        ('AW', 'Awake'),
        ('CO', 'Consultation'),
        ('ED', 'Education'),
        ('GT', 'Group Therapy'),
        ('LE', 'Leave'),
        ('OU', 'Out (with permission)'),
        ('MI', 'Missing (Inform S/N'),
        ('SL', 'Sleeping'),
        ('TR', 'Transfer'),
        ('DI', 'Discharge')
    ]

    # This field is left out of the form description because its type is not
    # currently supported. This is a good thing as we do not want to display
    # this field at the moment. It is maintained for use of future features.
    patient_level = obs_fields.Many2one(
        comodel_name='nh.clinical.therapeutic.level',
        help="The therapeutic level assigned to the patient at the time of "
             "the observation being completed."
    )
    patient_status = obs_fields.Selection(
        selection=_patient_status_selection,
        required=True
    )
    location = obs_fields.Char(
        size=100,
        necessary=False
    )
    areas_of_concern = obs_fields.Char(
        size=100,
        necessary=False
    )
    one_to_one_intervention_needed = obs_fields.Boolean()
    other_staff_during_intervention = obs_fields.Char(
        size=200,
        necessary=False
    )
    other_notes = obs_fields.Text(
        necessary=False
    )

    _description = 'Therapeutic'
    # TODO Remove when EOBS-982 complete.
    # Also decides the order fields are displayed in the mobile view.
    _required = [
        'patient_status'
    ]

    @api.model
    def get_form_description(self, patient_id):
        """
        See `nh.clinical.patient.observation` method docstring.
        """
        form_description_model = self.env['nh.clinical.form_description']
        form_description = form_description_model.to_dict(self)
        return form_description
