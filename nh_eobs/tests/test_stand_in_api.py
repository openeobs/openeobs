from openerp.tests.common import TransactionCase


class TestStandInApi(TransactionCase):
    
    def setUp(self):
        super(TestStandInApi, self).setUp()
        cr, uid = self.cr, self.uid

        self.user_pool = self.registry('res.users')
        self.eobs_api = self.registry('nh.eobs.api')

        self.hca_uid = self.user_pool.search(
            cr, uid, [['name', '=', 'Hca0 Test']])[0]
        self.nurse_uid = self.user_pool.search(
            cr, uid, [['name', '=', 'Nurse0 Test']])[0]

    def test_01_get_share_users_only_returns_same_groups_users(self):
        cr = self.cr

        res = self.eobs_api.get_share_users(cr, self.nurse_uid)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], 'Nurse1 Test')

    def test_02_get_share_users_only_returns_same_ward_users(self):
        cr = self.cr

        res = self.eobs_api.get_share_users(cr, self.hca_uid)
        self.assertEqual(len(res), 0)
