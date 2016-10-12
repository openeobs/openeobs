from openerp.tests.common import TransactionCase


class ReasonCountCommon(TransactionCase):
    """
    Test that the reason count SQL Views on ward dashboard are correct
    """

    def setUp(self):
        super(ReasonCountCommon, self).setUp()
        location_model = self.env['nh.clinical.location']
        self.spell_model = self.env['nh.clinical.spell']
        self.ward = location_model.search([['code', '=', 'A']]).ids[0]

    def get_reason_sql(self):
        return """
        SELECT rc.count::INTEGER FROM wdb_{table}_count AS rc
        JOIN nh_clinical_location AS loc
        ON rc.location_id = loc.id
        WHERE loc.id = {ward};
        """.format(ward=self.ward, table=self.reason.lower().replace(' ', '_'))

    def get_reason_id(self):
        reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        return reason_model.search([
            ['display_text', '=', self.reason]
        ]).id

    def returns_correct_number_of_patients(self, count=1):
        """
        Test that 1 patient per ward is returned as standard
        """
        self.cr.execute(self.get_reason_sql())
        sql_result = self.cr.dictfetchall()
        self.assertEqual(len(sql_result), 1)
        self.assertEqual(sql_result[0].get('count'), count)

    def returns_no_patients(self):
        """ Test that no patients are returned """
        self.cr.execute(self.get_reason_sql())
        sql_result = self.cr.dictfetchall()
        self.assertEqual(len(sql_result), 0)

    def returns_correct_number_after_change(self, count=2):
        """
        Test that 2 patients are returned after changing a patient's spell
        """
        spells_on_ward_a = self.spell_model.search(
            [
                ['location_id.parent_id.code', '=', 'A'],
                ['obs_stop', '=', False]
            ]
        )
        if spells_on_ward_a:
            spell = spells_on_ward_a[0]
            spell.write({'obs_stop': True})
            pme_model = self.env['nh.clinical.patient_monitoring_exception']
            activity_id = pme_model.create_activity(
                {},
                {'reason': self.get_reason_id(), 'spell': spell.id}
            )
            activity_model = self.env['nh.activity']
            pme_activity = activity_model.browse(activity_id)
            pme_activity.spell_activity_id = spell.activity_id
            pme_model.start(activity_id)
        else:
            raise ValueError('Could not find any spells to change on Ward A')
        self.returns_correct_number_of_patients(count=count)

    def returns_correct_number_of_patients_when_no_pme(self, count=0):
        spells_on_ward_a = self.spell_model.search(
            [
                ['location_id.parent_id.code', '=', 'A'],
                ['obs_stop', '=', True]
            ]
        )
        wardboard_model = self.env['nh.clinical.wardboard']
        for spell in spells_on_ward_a:
            wardboard = wardboard_model.browse(spell.id)
            wardboard.end_patient_monitoring_exception()
        self.returns_correct_number_of_patients(count=count)

    def returns_no_patients_when_no_pme(self):
        spells_on_ward_a = self.spell_model.search(
            [
                ['location_id.parent_id.code', '=', 'A'],
                ['obs_stop', '=', True]
            ]
        )
        wardboard_model = self.env['nh.clinical.wardboard']
        for spell in spells_on_ward_a:
            wardboard = wardboard_model.browse(spell.id)
            wardboard.end_patient_monitoring_exception()
        self.returns_no_patients()
