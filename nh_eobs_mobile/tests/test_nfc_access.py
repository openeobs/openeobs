__author__ = 'lorenzo'
import logging
import requests
from openerp import tests

test_logger = logging.getLogger(__name__)


class TestNFCModel(tests.HttpCase):

    def test_nfc_access_using_only_card_pin(self):
        resp = requests.post('http://localhost:8069/mobile/login/',
                             {'card_pin': '444555',
                              'database': 'nhclinical_test'})
        test_logger.debug(resp.text)
        self.assertIn('class="tasklist"', resp.text)