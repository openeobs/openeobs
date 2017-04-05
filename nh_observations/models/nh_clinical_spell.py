# -*- coding: utf-8 -*-
from openerp import models, api


class NHClinicalSpell(models.Model):
    """Add patient monitoring exception methods."""
    _name = 'nh.clinical.spell'
    _inherit = 'nh.clinical.spell'

    @api.multi
    def obs_stop_in_effect(self):
        """
        Checks if a patient monitoring exception is currently in effect for
        this spell.

        :return:
        :rtype: bool
        """
        domain = [
            ('data_model', '=', 'nh.clinical.pme.obs_stop'),
            ('state', 'not in', ['completed', 'cancelled']),
            ('spell_activity_id', '=', self.activity_id.id)
        ]
        activity_model = self.env['nh.activity']
        open_pmes = activity_model.search(domain)
        return True if len(open_pmes) > 0 else False
