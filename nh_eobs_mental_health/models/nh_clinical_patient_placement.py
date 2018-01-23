from openerp.osv import orm


class NhClinicalPatientPlacement(orm.Model):
    """
    Extends :class:`placement<operations.nh_clinical_patient_placement>`
    to update ``_POLICY``.

    When a :class:`patient<base.nh_clinical_patient>` is placed in a bed
    :class:`location<base.nh_clinical_location>` then a recurring
    :class:`EWS<ews.nh_clinical_patient_observation_ews>` will be
    `scheduled`. All existing EWS will be cancelled.
    """

    _name = 'nh.clinical.patient.placement'
    _inherit = 'nh.clinical.patient.placement'

    def _get_policy_create_data(self, case=None):
        """
        Override _get_policy_create_data to return a dict with the frequency
        for the new EWS so that if patient was on obs stop before placement it
        applies a frequency of 60 minutes

        :return: Dictionary with frequency
        :rtype: dict
        """
        activity_model = self.env['nh.activity']
        domain = [
            ['data_model', '=', 'nh.clinical.patient.observation.ews'],
            ['state', '=', 'cancelled'],
            ['patient_id', '=', self.patient_id.id],
            ['creator_id.data_model', '=', 'nh.clinical.pme.obs_stop'],
            ['creator_id.cancel_reason_id.name', '=', 'Transfer']
        ]
        obs_stop = activity_model.search(domain)
        from_transfer = self.activity_id.creator_id.data_model \
                        == 'nh.clinical.patient.transfer'
        if from_transfer and obs_stop:
            return {
                'frequency': obs_stop[0].data_ref.frequency
            }
        return super(NhClinicalPatientPlacement, self)\
            ._get_policy_create_data(case=case)
