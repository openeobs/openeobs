from openerp import models, api, fields

from openerp.addons.nh_observations import fields as obs_fields


class NhClinicalPatientObservationTherapeutic(models.Model):
    """
    Model representing a therapeutic observation.
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

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return '/therapeutic/static/src/js/chart.js'

    @api.multi
    def get_formatted_obs(self, replace_zeros=False,
                          convert_datetimes_to_client_timezone=False):
        """
        Override to ensure that the boolean field
        `one_to_one_intervention_needed` is correctly displayed in the mobile
        front-end when 'No' was selected during obs submission.

        :return:
        :rtype: list
        """
        convert = convert_datetimes_to_client_timezone
        obs_dict_list = super(NhClinicalPatientObservationTherapeutic, self)\
            .get_formatted_obs(replace_zeros=replace_zeros,
                               convert_datetimes_to_client_timezone=convert)
        key = 'one_to_one_intervention_needed'
        obs_with_one_to_one_submitted_as_no = [
            obs_dict for obs_dict in obs_dict_list
            if key not in obs_dict['none_values'] and obs_dict[key] is None
        ]
        for obs in obs_with_one_to_one_submitted_as_no:
            obs['one_to_one_intervention_needed'] = False
        return obs_dict_list

    @api.one
    def serialise(self):
        patient_status = self.get_field_value_label(
            'patient_status', self.patient_status
        )
        intervention = self._convert_bool_to_yes_no_string(
            'one_to_one_intervention_needed',
            self.one_to_one_intervention_needed
        )
        obs_dict = {
            'id': self.id,
            'date': self.create_date,
            'patient_status': patient_status,
            'location': self.location,
            'areas_of_concern': self.areas_of_concern,
            'intervention': intervention,
            'other_staff_during_intervention':
                self.other_staff_during_intervention,
            'other_notes': self.other_notes,
            'user': self.terminate_uid.name
        }
        return obs_dict

    def _convert_bool_to_yes_no_string(self, field_name, field_value):
        if field_value:
            return 'Yes'
        elif field_name in self.none_values:
            return ''
        else:
            return 'No'
