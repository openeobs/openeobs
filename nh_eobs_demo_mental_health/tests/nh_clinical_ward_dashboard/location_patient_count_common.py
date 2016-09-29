from openerp.tests.common import TransactionCase


class LocationPatientCountCommon(TransactionCase):
    """
    Test that the patients on ward SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(LocationPatientCountCommon, self).setUp()
        location_model = self.env['nh.clinical.location']
        users_model = self.env['res.users']
        self.ward = location_model.search([['code', '=', 'A']]).ids[0]
        self.adt_user = users_model.search([['login', '=', 'adt']]).ids[0]

    def get_count_sql(self):
        return """
        SELECT wc.count::INTEGER FROM wdb_{table}_count AS wc
        JOIN nh_clinical_location AS loc
        ON wc.location_id = loc.id
        WHERE loc.id = {ward};
        """.format(ward=self.ward, table=self.table)

    def returns_correct_number_of_patients(self, count):
        """
        Test that 1 patient per ward is returned as standard
        """
        self.cr.execute(self.get_count_sql())
        sql_result = self.cr.dictfetchall()
        self.assertEqual(len(sql_result), 1)
        self.assertEqual(sql_result[0].get('count'), count)
