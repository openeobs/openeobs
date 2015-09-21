from openerp.tests.common import SingleTransactionCase
from openerp.tests import DB as DB_NAME
from openerp.tools import config
import logging
import requests
from copy import deepcopy
from mock import MagicMock
import time

_logger = logging.getLogger(__name__)

SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
MOBILE_URL_PREFIX = 'mobile/'
BASE_URL = SERVER_PROTOCOL + '://' + SERVER_ADDRESS + ':' + SERVER_PORT + '/'
BASE_MOBILE_URL = BASE_URL + MOBILE_URL_PREFIX


def create_ews():
    """
    Creates a list of EWS results as used by get_patient_obs.
    :return: a list of dictionaries, each dictionary being a result.
    """

    result = {'blood_pressure_diastolic': 80, 'body_temperature': 37.5,
              'is_partial': False, 'date_terminated': '2015-09-08 17:59:50', # date_terminated
              'display_name': u'False',
              'null_values': u"['niv_epap', 'concentration', 'flow_rate', 'cpap_peep', 'niv_ipap', 'niv_backup']",
              'frequency': 480, 'o2_display': u'No',
              'create_date': '2015-09-08 18:29:50', 'concentration': False, # create_date
              'id': 250, 'create_uid': (1, u'Administrator'),
              'blood_pressure_systolic': 120, 'order_by': False,
              'indirect_oxymetry_spo2': 99, '__last_update': '2015-09-08 18:29:50',
              'state': u'completed', 'avpu_text': u'A', 'oxygen_administration_flag': False,
              'niv_backup': False, 'activity_id': (902, u'NEWS Observation'),
              'mews_score': 0, 'niv_epap': False, 'respiration_rate': 18,
              'write_uid': (1, u'Administrator'), 'bp_display': u'120 / 80', 'flow_rate': False,
              'write_date': '2015-09-08 18:29:50', 'score': 0, 'terminate_uid': (1, u'Administrator'), # write_date
              'date_started': '2015-09-08 18:31:27', 'device_id': False, 'none_values': u'[]', 'name': False, # date_started
              'three_in_one': False, 'score_display': u'0', 'cpap_peep': False,
              'patient_id': (5, u'Pagac, Rosabelle'), 'pulse_rate': 65, 'clinical_risk': u'None',
              'niv_ipap': False, 'partial_reason': False}

    results = []
    # some need to contain - {'date_terminated', 'create_date', 'write_date', 'date_started'})
    for i in range(1000):
        results.append(deepcopy(result))

    return results


class TestPerformanceMain(SingleTransactionCase):

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: A string with the username of the user to be authenticated as
        :return: A Response object
        """
        auth_response = requests.post(BASE_MOBILE_URL + 'login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def setUp(self):
        super(TestPerformanceMain, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        self.auth_response = self._get_authenticated_response('nadine')

    def test_create_ews(self):

        api_pool = self.registry['nh.eobs.api']
        api_pool.get_activities_for_patients = MagicMock(result=create_ews())

         # self.registry['nh.eobs.api']._patch_method('get_activities_for_patients', get_patient_ob)

        started_at = time.time()
        print started_at
        result = requests.get('http://localhost:8069/mobile/patient/ajax_obs/1', cookies=self.auth_response.cookies)
        logging.info(time.time() - started_at)
        print result


