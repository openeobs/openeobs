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

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    def get_active_observations(self, cr, uid, patient_id, context=None):
        """
        Returns all active observation types supported by eObs, if the
        :class:`patient<base.nh_clinical_patient>` has an active
        :class:`spell<spell.nh_clinical_spell>`.

        :param cr: Odoo Cursor
        :param uid: User doing operation
        :param patient_id: id of patient
        :type patient_id: int
        :param context: Odoo context
        :returns: list of all observation types
        :rtype: list
        """
        spell_model = self.pool['nh.clinical.spell']
        spell_id = spell_model.search(cr, uid, [
            ['patient_id', '=', patient_id],
            ['state', 'not in', ['completed', 'cancelled']]
        ], context=context)
        if spell_id:
            spell_id = spell_id[0]
            obs_stopped = spell_model.read(
                cr, uid, spell_id, ['obs_stop'], context=context)\
                .get('obs_stop')
            if obs_stopped:
                return []
        return super(NHeObsAPI, self)\
            .get_active_observations(cr, uid, patient_id, context=context)

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
        :param data: dictionary parameter that may contain the key
            ``location``
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
                    'activity_id'
                ], context=context)
            obs_stopped = spell.get('obs_stop')
            if obs_stopped:
                spell_model.write(
                    cr, uid, spell_id, {'obs_stop': False}, context=context)
                wardboard_model.browse(
                    cr, uid, spell.get('id'), context=context)\
                    .end_obs_stop(cancellation=True)
        res = super(NHeObsAPI, self).transfer(
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
