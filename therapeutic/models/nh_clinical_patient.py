from openerp import models, api


class NhClinicalPatient(models.Model):

    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        patient_dict = super(NhClinicalPatient, self).serialise()[0]

        deadline = self.get_therapeutic_deadline()
        patient_dict['deadlines'].append(deadline)

        return patient_dict

    def get_therapeutic_deadline(self):
        deadline = {
            'label': 'Therapeutic',
            'datetime': '00:45 hours'
        }
        return deadline
