from openerp import models, fields


class NhClinicalPatientObservationTherapeuticLevel(models.Model):

    _name = 'nh.clinical.patient.observation.therapeutic.level'

    level = fields.Integer()
