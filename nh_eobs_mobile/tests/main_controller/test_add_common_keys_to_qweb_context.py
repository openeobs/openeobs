# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.addons.nh_eobs_mobile.controllers import urls


URLS = urls.URLS


class TestAddCommonKeysToQWebContext(TransactionCase):
    def setUp(self):
        super(TestAddCommonKeysToQWebContext, self).setUp()
        self.qcontext = {}

        class FakeRequest(object):
            pass
        self.request_obj = FakeRequest()

        self.request_obj = self.env

        self.username = 'blah bloobahdee'
        request_session = {'login': self.username}
        self.request_obj.session = request_session

    def call_test(self):
        MobileFrontend.add_common_keys_to_qweb_context(self.qcontext,
                                                       self.request_obj)

    def test_adds_username_from_request_session_object(self):
        self.call_test()

        self.assertTrue('username' in self.qcontext)
        expected = self.username
        actual = self.qcontext['username']
        self.assertEqual(expected, actual)

    def test_adds_urls_from_global_scope(self):
        self.call_test()

        self.assertTrue('urls' in self.qcontext)
        expected = URLS
        actual = self.qcontext['urls']
        self.assertEqual(expected, actual)

    def test_adds_eobs_version(self):
        self.call_test()

        self.assertTrue('eobs_version' in self.qcontext)
        # `None` is expected because there is no `eobs_version` environment
        # variable setup for this test.
        expected = None
        actual = self.qcontext['eobs_version']
        self.assertEqual(expected, actual)
