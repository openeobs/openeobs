from openerp import api
from openerp.addons.nh_observations import frequencies
from openerp.models import Model


class ClinicalReviewFrequencyNotification(Model):
    """
    Clinical Review Frequency notification triggered upon completion of
    the Clinical Review notification.
    """

    _name = 'nh.clinical.notification.clinical_review_frequency'
    _inherit = ['nh.clinical.notification.frequency']
    _description = 'Clinical Review Frequency'

    _FREQUENCIES = [
        frequencies.EVERY_15_MINUTES,
        frequencies.EVERY_30_MINUTES,
        frequencies.EVERY_HOUR,
        frequencies.EVERY_2_HOURS,
        frequencies.EVERY_4_HOURS,
        frequencies.EVERY_6_HOURS,
        frequencies.EVERY_12_HOURS,
        frequencies.EVERY_DAY
    ]

    @api.model
    def get_form_description(self, patient_id):
        """
        Get form description showing different values depending on
        duration of patient's spell and clinical risk.

        :param patient_id: ID of the patient the form is for
        :return: List of fields for form
        """
        if not self.is_valid():
            return []

        notification_model = self.pool['nh.clinical.notification.frequency']
        notification_model.set_form_description_frequencies(self._FREQUENCIES)
        return list(self._form_description)
