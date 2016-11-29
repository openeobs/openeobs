from openerp import models, api


class ClinicalReviewNotification(models.Model):
    """
    Clinical Review notification triggered after 1/7 days (depending on
    clinical risk) of patient refusing to have observation taken
    """

    _name = 'nh.clinical.notification.clinical_review'
    _inherit = ['nh.clinical.notification']
    _description = 'Clinical Review'
    _notifications = [
        {
            'model': 'clinical_review_frequency',
            'summary': 'Set Clinical Review Frequency',
            'groups': ['nurse', 'doctor']
        }
    ]

    @api.model
    def complete(self, activity_id):
        super(ClinicalReviewNotification, self).complete(activity_id)

        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)

        api_model = self.env['nh.clinical.api']
        api_model.trigger_notifications({
            'notifications': self._notifications,
            'parent_id': activity.spell_activity_id.id,
            'creator_id': activity.id,
            'patient_id': activity.patient_id.id,
            'model': 'nh.clinical.patient.observation.ews',
            'group': 'nurse'
        })
