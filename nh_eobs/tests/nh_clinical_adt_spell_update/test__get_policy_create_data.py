from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method of the nh.clinical.adt.spell.update
    model
    """

    def setUp(self):
        super(TestGetPolicyCreateData, self).setUp()

    def test_suggested_location_id(self):
        """
        Test that the suggested location id is returned by
        _get_policy_create_data
        """
        self.assertTrue(False)
