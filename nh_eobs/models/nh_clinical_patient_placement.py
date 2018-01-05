# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Adds the policy for placement and refreshes the materialised view
"""
from openerp.osv import orm
from openerp.addons.nh_eobs.helpers import refresh_materialized_views


class NHClinicalPatientPlacement(orm.Model):
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

    _POLICY = {
        'activities': [
            {
                'model': 'nh.clinical.patient.observation.ews',
                'type': 'recurring',
                'cancel_others': True,
                'context': 'eobs'
            }
        ]
    }

    @refresh_materialized_views('ews0')
    def complete(self, *args, **kwargs):
        """
        Override the complete method purely so we can refresh the materialised
        views

        :return: Result of super().complete()
        """
        return super(NHClinicalPatientPlacement, self) \
            .complete(*args, **kwargs)
