# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp import models, fields, osv, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhClinicalObsStop(models.Model):

    _name = 'nh.clinical.pme.obs_stop'
    _inherit = 'nh.clinical.patient_monitoring_exception'

    # Adding required.
    reason = fields.Many2one(
        'nh.clinical.patient_monitoring_exception.reason',
        required=True
    )

    start_message = 'Stop Observations'
    stop_message = 'Restart Observations'

    def get_start_message(self):
        return self.start_message

    def get_stop_message(self):
        return self.stop_message

    def start(self, activity_id):
        super_return = super(NhClinicalObsStop, self).start(activity_id)

        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)

        cancel_reason_pme = \
            self.env['ir.model.data'].get_object(
                'nh_eobs', 'cancel_reason_patient_monitoring_exception'
            )
        cancel_open_ews = self.cancel_open_ews(activity.parent_id.id,
                                               cancel_reason_pme.id)
        self._cancel_open_food_and_fluid_review_tasks()
        if not cancel_open_ews:
            raise osv.except_osv(
                'Error', 'There was an issue cancelling '
                         'all open NEWS activities'
            )

        self.set_obs_stop_flag(True)
        return super_return

    def _cancel_open_food_and_fluid_review_tasks(self):
        """
        Cancels open food and fluid review tasks for the current spell.
        The current spell is determined by looking at `self` which should be
        an ob stop record with a poplated `spell_id` field.
        :return:
        """
        spell_activity_id = self.spell.activity_id.id
        cancel_reason_pme = \
            self.env['ir.model.data'].get_object(
                'nh_eobs', 'cancel_reason_patient_monitoring_exception')

        food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        food_and_fluid_review_model.cancel_review_tasks(cancel_reason_pme,
                                                        spell_activity_id)

    def complete(self, activity_id):
        super_return = super(NhClinicalObsStop, self).complete(activity_id)

        self.set_obs_stop_flag(False)
        self.create_new_ews()
        return super_return

    @api.model
    def cancel(self, activity_id):
        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)

        ir_model_data_model = self.env['ir.model.data']
        cancel_reason = ir_model_data_model.get_object(
            'nh_clinical', 'cancel_reason_transfer')

        super(NhClinicalObsStop, self).cancel(activity_id)
        activity.cancel_reason_id = cancel_reason
        self.set_obs_stop_flag(False)

        self.create_new_ews()

    @api.multi
    def set_obs_stop_flag(self, value):
        """
        Toggle the obs_stop flag on the spell object.

        :param value:
        :type value: bool
        :return: True
        """
        self.spell.obs_stop = value

    @api.model
    def cancel_open_ews(self, spell_activity_id, cancel_reason_id=None):
        """
        Cancel all open EWS observations.

        :param spell_activity_id: ID of the spell activity
        :param cancel_reason_id:
        :return: True is successful, False if not
        """
        activity_model = self.env['nh.activity']
        return activity_model.cancel_open_activities(
            spell_activity_id,
            model='nh.clinical.patient.observation.ews',
            cancel_reason_id=cancel_reason_id
        )

    @api.multi
    def create_new_ews(self):
        """
        Create a new EWS task an hour in the future. Used when patient is
        taken off obs_stop.

        :return: ID of created EWS
        """
        ews_model = self.env['nh.clinical.patient.observation.ews']
        activity_model = self.env['nh.activity']
        api_model = self.env['nh.clinical.api']

        activity_obs_stop = self.get_activity()
        activity_spell = self.spell.get_activity()

        new_ews_id = ews_model.create_activity(
            {'parent_id': activity_spell.id,
             'creator_id': activity_obs_stop.id},
            {'patient_id': activity_spell.patient_id.id}
        )
        one_hour_time = datetime.now() + timedelta(hours=1)
        one_hour_time_str = one_hour_time.strftime(DTF)

        self.force_v7_api(activity_model)

        activity_model.schedule(self.env.cr, self.env.uid, new_ews_id,
                                date_scheduled=one_hour_time_str)
        patient_id = activity_spell.patient_id.id
        api_model.change_activity_frequency(
            patient_id, 'nh.clinical.patient.observation.ews', 60)
        return new_ews_id

    # TODO Refactor the activity method decorator and remove this method.
    @classmethod
    def force_v7_api(cls, obj):
        """
        Trick Odoo into thinking this is a 7.0 ORM API style method before
        the `complete` method is called on the activity. I believe there may
        be a problem in the decorator that is used on all activity data methods
        which specifically looks for all args.
        :param obj:
        :return:
        """
        if '_ids' in obj.__dict__:
            obj.__dict__.pop('_ids')
