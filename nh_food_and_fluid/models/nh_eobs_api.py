# -*- coding: utf-8 -*-
from openerp import api
from openerp.models import AbstractModel


class NhEobsApi(AbstractModel):

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    @api.model
    def transfer(self, hospital_number, data):
        """
        Override of transfer to cancel open food and fluid review tasks for
        the current spell of the patient who is being transferred.
        :param hospital_number:
        :type hospital_number: str
        :param data: dictionary parameter that may contain the key
        ``location``.
        :type data: dict
        :return: ``True``
        :rtype: bool
        """
        super_return = super(NhEobsApi, self).transfer(hospital_number, data)
        cancel_reason_transfer = self.env['ir.model.data'].get_object(
            'nh_clinical', 'cancel_reason_transfer')
        self._cancel_food_and_fluid_review_tasks(hospital_number,
                                                 cancel_reason_transfer)
        return super_return

    @api.model
    def discharge(self, hospital_number, data):
        """
        Override of discharge to cancel open food and fluid review tasks for
        the current spell of the patient who is being discharged.
        :param hospital_number:
        :type hospital_number: str
        :param data: Dictionary parameter that may contain the key
        ``discharge_date``.
        :type data: dict
        :return: ``True``
        :rtype: bool
        """
        super_return = super(NhEobsApi, self).discharge(hospital_number, data)
        cancel_reason_discharge = self.env['ir.model.data'].get_object(
            'nh_clinical', 'cancel_reason_discharge')
        self._cancel_food_and_fluid_review_tasks(hospital_number,
                                                 cancel_reason_discharge)
        return super_return

    def _cancel_food_and_fluid_review_tasks(self, hospital_number,
                                            cancel_reason):
        """
        Cancel food and fluid review tasks for the patient with the passed
        hospital number and using the passed cancel reason.
        :param hospital_number:
        :param cancel_reason:
        :return:
        """
        spell_activity_id = self.get_spell_activity_id(hospital_number)

        food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        food_and_fluid_review_model.cancel_review_tasks(
            cancel_reason, spell_activity_id=spell_activity_id)
