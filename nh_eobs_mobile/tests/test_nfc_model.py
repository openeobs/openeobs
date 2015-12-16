# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp import tests


class TestNFCModel(tests.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestNFCModel, cls).setUpClass()
        cls.user_pool = cls.registry['res.users']
        cls.user_values = {
            'name': 'Test User',
            'login': 'testuser',
            'password': 'testuser',
            'card_pin': '987654'
        }
        cls.test_user_id = cls.user_pool.create(
            cls.cr, cls.uid, cls.user_values, context=None)

    def test_get_user_id_from_card_pin(self):
        retrieved_user_id = self.user_pool.get_user_id_from_card_pin(
            self.cr, self.uid, '987654')
        self.assertEqual(self.test_user_id, retrieved_user_id)

    def test_get_user_login_from_user_id(self):
        retrieved_user_login = self.user_pool.get_user_login_from_user_id(
            self.cr, self.uid, self.test_user_id)
        self.assertEqual(self.user_values['login'], retrieved_user_login)
