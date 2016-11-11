from openerp.osv import orm


class ClinicalReviewNotification(orm.Model):
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
            'groups': ['doctor', 'nurse']
        }
    ]
