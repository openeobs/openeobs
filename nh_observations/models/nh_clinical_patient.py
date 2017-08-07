# -*- coding: utf-8 -*-
from openerp import models, api


class NhClinicalPatient(models.Model):
    """
    Extends :class:`patient<base.nh_clinical_patient>`
    """
    _name = 'nh.clinical.patient'
    _inherit = 'nh.clinical.patient'

    @api.multi
    def write(self, vals):
        """
        Calls :meth:`write<openerp.models.Model.write>` and
        automatically updates the :class:`location<base.nh_clinical_location>`
        of every
        :mod:`observation<observations.nh_clinical_patient_observation>`
        and :mod:`notification<notifications.nh_clinical_notification>`
        related.

        :returns: ``True``
        :rtype: bool
        """
        res = super(NhClinicalPatient, self).write(vals)

        if 'current_location_id' in vals:
            activity_model = self.env['nh.activity']
            patient_ids = self.ids if hasattr(self.ids, '__iter__') \
                else [self.ids]
            obs_and_notifications = activity_model.search(
                [
                    ('patient_id', 'in', patient_ids),
                    ('state', 'not in', ['completed', 'cancelled']),
                    '|',
                    ('data_model', 'ilike', '%observation%'),
                    ('data_model', 'ilike', '%notification%')
                ]
            )
            for record in obs_and_notifications:
                record.location_id = vals['current_location_id']

        return res
