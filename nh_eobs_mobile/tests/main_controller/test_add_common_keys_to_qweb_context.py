# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs_mobile.controllers import urls
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.tests.common import TransactionCase

URLS = urls.URLS


class TestAddCommonKeysToQWebContext(TransactionCase):
    """
    Tests the `add_common_keys_to_qweb_context` method on the `nh_eobs_mobile`
    controller.
    """
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
        """
        Calls the method under test.
        """
        MobileFrontend.add_common_keys_to_qweb_context(self.qcontext,
                                                       self.request_obj)

    def test_adds_username_from_request_session_object(self):
        """
        The username found in the request object is set on the QWeb context.
        """
        self.call_test()

        self.assertTrue('username' in self.qcontext)
        expected = self.username
        actual = self.qcontext['username']
        self.assertEqual(expected, actual)

    def test_adds_urls_from_global_scope(self):
        """
        The URLS are set on the QWeb context.
        """
        self.call_test()

        self.assertTrue('urls' in self.qcontext)
        expected = URLS
        actual = self.qcontext['urls']
        self.assertEqual(expected, actual)

    def test_adds_version_environment_variable_value(self):
        """
        The version environment variable value is set on the QWeb context.
        """
        self.call_test()

        self.assertTrue('version' in self.qcontext)
        # `None` is expected because there is no `version` environment
        # variable setup for this test.
        expected = None
        actual = self.qcontext['version']
        self.assertEqual(expected, actual)
