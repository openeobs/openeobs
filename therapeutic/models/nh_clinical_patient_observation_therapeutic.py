from openerp import models, api, fields

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
    # Only has to be redefined because the super model is V7 API and therefore
    # has a hard link to the compute method.
    is_partial = fields.Boolean(
        compute='_is_partial',
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
    _required = [
        'patient_status',
        'one_to_one_intervention_needed'
    ]

    @api.model
    def get_form_description(self, patient_id):
        """
        See `nh.clinical.patient.observation` method docstring.
        """
        form_description_model = self.env['nh.clinical.form_description']
        form_description = form_description_model.to_dict(self)
        return form_description

    def _is_partial(self):
        """
        This override is a hack to disable partials entirely for this
        observation. The `_required` attribute affects the population of the
        `none_values` and validation for partials which makes it difficult to
        achieve the same by just declaring attributes on the model.
        """
        return False
