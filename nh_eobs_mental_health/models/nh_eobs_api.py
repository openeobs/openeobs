# -*- coding: utf-8 -*-
import logging

from openerp import api
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.osv import orm
from werkzeug import exceptions

_logger = logging.getLogger(__name__)


class NHeObsAPI(orm.AbstractModel):
    """
    Defines attributes and methods used by `Open eObs` in the making of
    patient observations.

    ``_active_observations`` are the observation types supported by
    eObs.
    """

    _inherit = 'nh.eobs.api'

    @api.model
    def get_active_observations(self, patient_id):
        """
        Override to remove observations from list if the patient is on obs
        stop.

        :param patient_id: id of patient
        :type patient_id: int
        :returns: list of all observation types
        :rtype: list
        """
        if self._patient_on_obs_stop(patient_id):
            return []
        active_observations = super(NHeObsAPI, self).get_active_observations(
            patient_id)
        return active_observations

    @api.model
    def _patient_on_obs_stop(self, patient_id):
        """
        :param patient_id:
        :type patient_id: int
        :return:
        :rtype: bool
        """
        spell_model = self.env['nh.clinical.spell']
        spell_activity = spell_model.get_spell_activity_by_patient_id(
            patient_id)
        return spell_activity.data_ref.obs_stop

    def transfer(self, cr, uid, hospital_number, data, context=None):
        """
        Extends
        :meth:`transfer()<api.nh_clinical_api.transfer>`, transferring
        a :class:`patient<base.nh_clinical_patient>` to a
        :class:`location<base.nh_clinical_location>`.

        - Set transferred patients to not have obs_stop flag set

        :param cr: Odoo cursor
        :param uid: User doing the operation
        :param hospital_number: `hospital number` of the patient
        :type hospital_number: str
        :param data: dictionary parameter that may contain the key ``location``
        :param context: Odoo Context
        :returns: ``True``
        :rtype: bool
        """
        spell_model = self.pool['nh.clinical.spell']
        patient_model = self.pool['nh.clinical.patient']
        wardboard_model = self.pool['nh.clinical.wardboard']
        patient_id = patient_model.search(cr, uid, [
            ['other_identifier', '=', hospital_number]
        ])
        spell_id = spell_model.search(cr, uid, [
            ['patient_id', 'in', patient_id],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        if spell_id:
            spell_id = spell_id[0]
            spell = spell_model.read(
                cr, uid, spell_id, [
                    'obs_stop',
                    'refusing_obs',
                    'activity_id'
                ], context=context)
            obs_stopped = spell.get('obs_stop')
            if obs_stopped:
                spell_model.write(
                    cr, uid, spell_id, {'obs_stop': False}, context=context)
                wardboard_model.browse(
                    cr, uid, spell.get('id'), context=context)\
                    .end_obs_stop(cancellation=True)
            if spell.get('refusing_obs'):
                spell_model.write(
                    cr, uid, spell_id,
                    {'refusing_obs': False}, context=context)
        res = super(NHeObsAPI, self).transfer(
            cr, uid, hospital_number, data, context=None)
        return res

    def discharge(self, cr, uid, hospital_number, data, context=None):
        """
        Extends
        :meth:`discharge()<api.nh_clinical_api.discharge>`,
        closing the :class:`spell<spell.nh_clinical_spell>` of a
        :class:`patient<base.nh_clinical_patient>`.

        :param hospital_number: `hospital number` of the patient
        :type hospital_number: str
        :param data: may contain the key ``discharge_date``
        :type data: dict
        :returns: ``True``
        :rtype: bool
        """
        spell_model = self.pool['nh.clinical.spell']
        patient_model = self.pool['nh.clinical.patient']
        patient_id = patient_model.search(cr, uid, [
            ['other_identifier', '=', hospital_number]
        ])
        spell_id = spell_model.search(cr, uid, [
            ['patient_id', 'in', patient_id],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        if spell_id:
            spell_id = spell_id[0]
            spell = spell_model.read(
                cr, uid, spell_id, [
                    'refusing_obs',
                    'activity_id'
                ], context=context)
            if spell.get('refusing_obs'):
                spell_model.write(
                    cr, uid, spell_id,
                    {'refusing_obs': False}, context=context)
        res = super(NHeObsAPI, self).discharge(
            cr, uid, hospital_number, data, context=None)
        return res

    @api.model
    def set_rapid_tranq(self, request, **kwargs):
        """
        Handles requests to the `rapid_tranq` endpoint for the controller.

        When called with a 'GET' method a `rapid_tranq` parameter is returned
        in the body of the response with the current value.

        When called with a 'POST' method a `rapid_tranq` parameter is expected
        in the body of the request with the new value to be set on the field.
        A `rapid_tranq` parameter is also returned in the body of the response
        with the new, updated `rapid_tranq` value.

        Additionally a GET message can pass a `check` parameter with a boolean
        value ('true' or 'false') to test what the effect of a POST would be.
        The response will be the same as for the POST, but additionally will
        return a title and description with appropriate messages. If there will
        be no change in the state of the resource then the messages advise the
        user to reload their page, as of writing this that is the only known
        scenario a case where the user attempts to update the `rapid_tranq`
        field to a value it already has. Otherwise if the POST would result in
        an update, confirmation messages are returned.

        :param request: Request object passed from a controller.
        :param kwargs: Keyword arguments passed from a controller.
        :return: JSON encoded string.
        :rtype: str
        """
        # Validate patient ID.
        patient_id = kwargs.get('patient_id')
        try:
            patient_id = int(patient_id)
        except ValueError:
            exceptions.abort(404, "Invalid patient ID.")

        spell_model = self.env['nh.clinical.spell']
        spell_activity = spell_model.get_spell_activity_by_patient_id(
            patient_id)
        if not spell_activity:
            exceptions.abort(404, "No spell found for patient with that ID.")

        existing_value = spell_activity.data_ref.rapid_tranq

        def parse_set_value(kwargs):
            set_value = kwargs.get('rapid_tranq')
            if not set_value:
                set_value = kwargs.get('check')
            if set_value == 'true':
                set_value = True
            elif set_value == 'false':
                set_value = False
            else:
                message = "New rapid tranq value should be either 'true' or " \
                          "'false'."
                exceptions.abort(400, message)
            return set_value

        status = ResponseJSON.STATUS_SUCCESS
        title = False
        description = False

        rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']

        # Handle differently depending on HTTP method.
        method = request.httprequest.method

        if method == 'GET' and 'check' in kwargs:
            set_value = parse_set_value(kwargs)
            spell = spell_activity.data_ref
            check_response = rapid_tranq_model.check_set_rapid_tranq(
                set_value, spell)

            try:
                status = check_response['status']
                title = check_response['title']
                description = check_response['description']
            except KeyError:
                raise ValueError(
                    "Dictionary returned from check_set_rapid_tranq method did"
                    " not contain the keys needed to form a complete response."
                )
        elif method == 'POST':
            existing_value = rapid_tranq_model.toggle_rapid_tranq(
                spell_activity)
        else:
            exceptions.abort(405)

        response_data = {
            'rapid_tranq': existing_value
        }
        response_json = ResponseJSON.get_json_data(
            status=status,
            data=response_data,
            title=title,
            description=description
        )
        return response_json

    @api.model
    def get_patients(self, ids=None):
        """
        Return a list of patients that the user has access to.

        :param ids: ids of the patients. If empty, then all patients are
        returned
        :type ids: list
        :returns: List of patient dictionaries
        :rtype: list of dict
        """
        patient_model = self.env['nh.clinical.patient']

        # For shift coordinators or doctors just check location_ids for wards
        # and return all patients on those wards.
        if self.env.user.is_doctor() \
                or self.env.user.is_shift_coordinator() \
                or self.env.user.is_senior_manager() \
                or self.env.user.is_system_admin():
            wards = self.env.user.location_ids.filtered(
                lambda location: location.usage == 'ward')
            # Patient model serves as an empty recordset to be appended to in
            # the loop below.
            patients = patient_model
            for ward in wards:
                patients += patient_model.get_patients_on_ward(ward.id, ids)
        # For other staff like nurses and HCAs, ward is not in location_ids
        # so check the current shift for each ward and see if they are assigned
        # to it.
        else:
            ward = self._get_user_ward()
            if not ward:
                # If no ward then user is not on a shift so empty list of
                # patients is expected.
                return []
            patients = patient_model.get_patients_on_ward(ward.id, ids)

        # Filter out patients who are not placed.
        patients = patients.filtered(
            lambda patient: patient.current_location_id.usage == 'bed')

        patient_dict_list = self._create_patient_dict_list(patients)
        return patient_dict_list

    def user_allocated_to_patient(self, patient_id):
        patient_model = self.env['nh.clinical.patient']
        patient = patient_model.browse(patient_id)
        return self.env.user in patient.current_location_id.user_ids
