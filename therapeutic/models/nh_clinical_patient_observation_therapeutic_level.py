from openerp import models, fields, api


class NhClinicalPatientObservationTherapeuticLevel(models.Model):

    _name = 'nh.clinical.patient.observation.therapeutic.level'

    patient = fields.Many2one(comodel_name='nh.clinical.patient',
                              required=True)
    level = fields.Integer(required=True, default=1)
    # frequency = fields.Selection()

    def default_get(self, cr, uid, fields, context=None):
        """
        Ensure that the patient field is pre-populated on the form view when
        creating a new level record from the wardboard view.

        :param cr:
        :param uid:
        :param fields:
        :param context:
        :return:
        """
        field_defaults_dict = \
            super(NhClinicalPatientObservationTherapeuticLevel, self)\
            .default_get(cr, uid, fields, context=None)
        if 'active_id' in context \
                and 'active_model' in context \
                and context['active_model'] == 'nh.clinical.wardboard':
            wardboard_model = self.pool['nh.clinical.wardboard']
            wardboard = wardboard_model.browse(cr, uid, context['active_id'])
            field_defaults_dict['patient'] = wardboard.patient_id.id
        return field_defaults_dict

    def save(self, cr, uid, ids, context=None):
        pass
