from openerp import models, api

from openerp.addons.nh_observations import fields as obs_fields


class NhClinicalPatientObservationTherapeutic(models.Model):
    """
    Model for the therapeutic observation.
    """
    _name = 'nh.clinical.patient.observation.therapeutic'
    _inherit = 'nh.clinical.patient.observation'

    _patient_status_selection = [
        ('AW', 'Awake'),
        ('CO', 'Consultation'),
        ('ED', 'Education'),
        ('GT', 'Group Therapy'),
        ('LE', 'Leave'),
        ('OU', 'Out (With Permission)'),
        ('MI', 'Missing (Inform S/N)'),
        ('SL', 'Sleeping'),
        ('TR', 'Transfer'),
        ('DI', 'Discharge')
    ]

    patient_status = obs_fields.Selection(
        selection=_patient_status_selection,
        string="Patient Status",
        required=True
    )
    location = obs_fields.Char(
        size=100,
        necessary=False
    )
    areas_of_concern = obs_fields.Char(
        size=100,
        string="Areas of Concern",
        necessary=False
    )
    one_to_one_intervention_needed = obs_fields.Boolean(
        string="Intervention Needed?",
        necessary=False
    )
    other_staff_during_intervention = obs_fields.Char(
        size=200,
        string="Other Staff During Intervention",
        necessary=False
    )
    other_notes = obs_fields.Text(
        string="Other Notes",
        necessary=False
    )

    _description = 'Therapeutic'
    # TODO Remove when EOBS-982 complete.
    # Also decides the order fields are displayed in the mobile view.
    fields_order = [
        'patient_level',
        'patient_status',
        'location',
        'areas_of_concern',
        'one_to_one_intervention_needed',
        'other_staff_during_intervention',
        'other_notes'
    ]

    @api.model
    def get_form_description(self, patient_id):
        """
        See `nh.clinical.patient.observation` method docstring.
        """
        form_description_model = self.env['nh.clinical.form_description']
        form_description = form_description_model.to_dict(self)
        return form_description
