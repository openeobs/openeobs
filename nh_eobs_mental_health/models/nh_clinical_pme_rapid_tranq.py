# -*- coding: utf-8 -*-
from openerp import models, api

from openerp.addons.nh_eobs_api.routing import ResponseJSON


class NhClinicalRapidTranq(models.Model):

    _name = 'nh.clinical.pme.rapid_tranq'
    _inherit = 'nh.clinical.patient_monitoring_exception'

    start_message = 'Start Rapid Tranq.'
    stop_message = 'Stop Rapid Tranq.'

    def get_start_message(self):
        return self.start_message

    def get_stop_message(self):
        return self.stop_message

    def start(self, activity_id):
        super_return = super(NhClinicalRapidTranq, self).start(activity_id)
        self.set_rapid_tranq(True)
        return super_return

    def complete(self, activity_id):
        super_return = super(NhClinicalRapidTranq, self).complete(activity_id)
        self.set_rapid_tranq(False)
        return super_return

    def cancel(self, activity_id):
        super_return = super(NhClinicalRapidTranq, self).cancel(activity_id)
        self.set_rapid_tranq(False)
        return super_return

    @api.model
    def check_set_rapid_tranq(self, set_value, spell):
        """
        Check what the effect of setting the rapid tranq status would be and
        return a dictionary with user-friendly messages which the caller can
        use for things such as raising exceptions and creating popups.

        :param set_value:
        :type set_value: bool
        :return:
        :rtype: dict
        """
        existing_value = spell.rapid_tranq
        rapid_tranq_changed = self.changed(set_value, existing_value)

        if rapid_tranq_changed:
            activate = 'Activate' if set_value else 'Deactivate'

            patient_id = spell.patient_id.id
            patient_model = self.env['nh.clinical.patient']
            patient = patient_model.browse(patient_id)
            patient_name = "{}, {}".format(patient.family_name,
                                           patient.given_name)

            status = ResponseJSON.STATUS_SUCCESS
            title = "{activation} Rapid Tranquilisation Status for " \
                    "{patient_name}?".format(activation=activate,
                                             patient_name=patient_name)

            active = 'Active' if set_value else 'Not Active'
            description = \
                "Please confirm you are setting the patient's Rapid " \
                "Tranquilisation status to {}.".format(active)
        else:
            start = 'start' if set_value else 'stop'
            started = 'started' if set_value else 'stopped'

            status = ResponseJSON.STATUS_FAIL
            title = "Page Reload Required"
            description = "You attempted to {start} Rapid Tranquilisation " \
                          "but it has already been {started}. That means " \
                          "the page is currently out of date, please reload " \
                          "the page." \
                .format(start=start, started=started)
        return {
            'status': status,
            'title': title,
            'description': description
        }

    def set_rapid_tranq(self, value):
        """
        Toggle the obs_stop flag on the spell object.

        :param value:
        :type value: bool
        :return: True
        """
        self.spell.rapid_tranq = value

    @api.model
    def toggle_rapid_tranq(self, spell_activity):
        """
        Toggles rapid tranquilisation status on or off for a given spell.

        :param spell_activity:
        :return: The new value after the toggle.
        :rtype: bool
        """
        activity_model = self.env['nh.activity']
        spell = spell_activity.data_ref

        if spell.rapid_tranq:
            activity_rapid_tranq = self.get_open_activity(spell_activity.id)
            rapid_tranq = activity_rapid_tranq.data_ref

            rapid_tranq.complete(activity_rapid_tranq.id)
            new_rapid_tranq_value = False
        else:
            rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']
            activity_rapid_tranq_id = rapid_tranq_model.create_activity(
                {'parent_id': spell_activity.id},
                {'spell': spell.id}
            )
            activity_rapid_tranq = \
                activity_model.browse(activity_rapid_tranq_id)
            rapid_tranq = activity_rapid_tranq.data_ref

            rapid_tranq.start(activity_rapid_tranq_id)
            new_rapid_tranq_value = True
        return new_rapid_tranq_value

    @staticmethod
    def changed(set_value, existing_value):
        """
        Indicates whether or not the 2 passed booleans are different from one
        another.

        :param set_value:
        :param existing_value:
        :return:
        :rtype: bool
        """
        return set_value ^ existing_value
