# -*- coding: utf-8 -*-
import json

from openerp.exceptions import except_orm
from openerp.tests.common import HttpCase


class TestRapidTranq(HttpCase):

    def setUp(self):
        super(TestRapidTranq, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']

        self.authenticate('nasir', 'nasir')

    def call_test(self, patient_id=1, method='POST',
                  rapid_tranq_set_value=True, rapid_tranq_existing_value=False,
                  timeout=1000000, no_spell_activity=False):

        def mock_get_spell_activity_by_patient(*args, **kwargs):
            if no_spell_activity:
                return self.activity_model

            spell_activity = self.activity_model.new({})
            spell = self.spell_model.new({})
            spell.rapid_tranq = rapid_tranq_existing_value
            spell_activity.data_ref = spell

            return spell_activity
        self.spell_model._patch_method('get_spell_activity_by_patient',
                                       mock_get_spell_activity_by_patient)

        def mock_toggle_rapid_tranq(*args, **kwargs):
            return not rapid_tranq_existing_value
        self.rapid_tranq_model._patch_method('toggle_rapid_tranq',
                                             mock_toggle_rapid_tranq)

        self.patient_given_name = 'Jon'
        self.patient_family_name = 'Snow'
        self.patient_name = '{}, {}'.format(
            self.patient_family_name, self.patient_given_name
        )
        patient = self.patient_model.new({})
        patient.given_name = self.patient_given_name
        patient.family_name = self.patient_family_name

        def mock_patient_browse(*args, **kwargs):
            return patient
        self.patient_model._patch_method('browse', mock_patient_browse)

        url = '/mobile/patient/{}/rapid_tranq'.format(patient_id)

        if method == 'GET':
            rapid_tranq_set_value_str = str(rapid_tranq_set_value).lower()
            url = '{}?check={}'.format(url, rapid_tranq_set_value_str)
            data = None  # No data makes request a GET instead of a POST.
        else:
            if rapid_tranq_set_value:
                data = 'rapid_tranq=true'
            else:
                data = 'rapid_tranq=false'

        response = self.url_open(url, data, timeout=timeout)
        return response

    @staticmethod
    def convert_response_to_dictionary(response):
        json_str = response.readlines()[0]
        dictionary = json.loads(json_str)
        return dictionary

    @staticmethod
    def get_rapid_tranq_from_response(response):
        dictionary = TestRapidTranq.convert_response_to_dictionary(
            response)
        rapid_tranq = dictionary.get('data', {}).get('rapid_tranq')
        return rapid_tranq

    @staticmethod
    def get_description_from_response(response):
        dictionary = TestRapidTranq.convert_response_to_dictionary(
            response)
        description = dictionary.get('description')
        return description

    @staticmethod
    def get_status_from_response(response):
        dictionary = TestRapidTranq.convert_response_to_dictionary(
            response)
        description = dictionary.get('status')
        return description

    @staticmethod
    def get_title_from_response(response):
        dictionary = TestRapidTranq.convert_response_to_dictionary(
            response)
        description = dictionary.get('title')
        return description

    def test_valid_patient_id_returns_200(self):
        response = self.call_test()
        self.assertEqual(200, response.code)

    def test_returns_json_content_type(self):
        response = self.call_test()
        headers = response.headers
        self.assertTrue('Content-Type' in headers)
        content_type = headers['Content-Type']
        self.assertEqual('application/json', content_type)

    def test_post_returns_rapid_tranq_boolean_in_response_body(self):
        response = self.call_test()
        rapid_tranq = self.get_rapid_tranq_from_response(response)
        self.assertTrue(isinstance(rapid_tranq, bool))

    def test_rapid_tranq_already_started_popup_description(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=True, rapid_tranq_existing_value=True
        )
        actual = self.get_description_from_response(response)
        expected = "You attempted to start Rapid Tranquilisation but it " \
                   "has already been started. That means the page is " \
                   "currently out of date, please reload the page."

        self.assertEqual(expected, actual)

    def test_rapid_tranq_already_stopped_popup_description(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=False, rapid_tranq_existing_value=False
        )
        actual = self.get_description_from_response(response)
        expected = "You attempted to stop Rapid Tranquilisation but it " \
                   "has already been stopped. That means the page is " \
                   "currently out of date, please reload the page."

        self.assertEqual(expected, actual)

    def test_starting_rapid_tranq_popup_title(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=True, rapid_tranq_existing_value=False
        )
        actual = self.get_title_from_response(response)
        expected = "Activate Rapid Tranquilisation Status for {}?".format(
            self.patient_name)

        self.assertEqual(expected, actual)

    def test_stopping_rapid_tranq_popup_title(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=False, rapid_tranq_existing_value=True
        )
        actual = self.get_title_from_response(response)
        expected = "Deactivate Rapid Tranquilisation Status for {}?".format(
            self.patient_name)

        self.assertEqual(expected, actual)

    def test_starting_rapid_tranq_popup_description(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=True, rapid_tranq_existing_value=False
        )
        actual = self.get_description_from_response(response)
        expected = "Please confirm you are setting the patient's Rapid " \
                   "Tranquilisation status to Active."

        self.assertEqual(expected, actual)

    def test_stopping_rapid_tranq_popup_description(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=False, rapid_tranq_existing_value=True
        )
        actual = self.get_description_from_response(response)
        expected = "Please confirm you are setting the patient's Rapid " \
                   "Tranquilisation status to Not Active."

        self.assertEqual(expected, actual)

    def test_get_returns_rapid_tranq_boolean_in_response_body(self):
        response = self.call_test(method='GET')
        rapid_tranq = self.get_rapid_tranq_from_response(response)
        self.assertTrue(isinstance(rapid_tranq, bool))

    def test_404_returned_when_no_spell_activity_for_patient_id(self):
        response = self.call_test(no_spell_activity=True)
        self.assertEqual(404, response.code)

    def test_404_returned_when_non_int_for_patient_id(self):
        def mock_get_spell_activity_by_patient(*args, **kwargs):
            raise except_orm("Spell Not Found Exception",
                             "No spell found for patient with that ID.")

        self.spell_model._patch_method('get_spell_activity_by_patient',
                                       mock_get_spell_activity_by_patient)

        response = self.call_test(patient_id='foo')
        self.assertEqual(404, response.code)

    def test_success_status_when_check_shows_change_for_passed_value(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=True, rapid_tranq_existing_value=False
        )
        status = self.get_status_from_response(response)

        self.assertEqual('success', status)

    def test_fail_status_when_check_shows_no_change_for_passed_value(self):
        response = self.call_test(
            method='GET',
            rapid_tranq_set_value=True, rapid_tranq_existing_value=True
        )
        status = self.get_status_from_response(response)

        self.assertEqual('fail', status)

    def tearDown(self):
        self.spell_model._revert_method('get_spell_activity_by_patient')
        self.rapid_tranq_model._revert_method('toggle_rapid_tranq')
        self.patient_model._revert_method('browse')
        super(TestRapidTranq, self).tearDown()
