from .location_patient_count_common import LocationPatientCountCommon


class TestCapacityCount(LocationPatientCountCommon):
    """
    Test that the patients on ward SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestCapacityCount, self).setUp()
        self.table = 'capacity'

    def test_returns_correct_number_of_locations(self):
        """
        Test that 30 beds in ward A
        """
        self.returns_correct_number_of_patients(-10)

    def test_returns_correct_number_after_change(self):
        """
        Test that 2 patients are returned after changing a patient's spell
        """
        spell_model = self.env['nh.clinical.spell']
        api_model = self.registry('nh.clinical.api')
        spells_on_ward_a = spell_model.search(
            [
                ['location_id.parent_id.code', '=', 'A'],
                ['obs_stop', '=', False]
            ]
        )
        if spells_on_ward_a:
            spell = spells_on_ward_a[0]
            api_model.discharge(
                self.cr, self.adt_user, spell.patient_id.other_identifier,
                {'location': 'DISL'}, context={})
        else:
            raise ValueError('Could not find any spells to change on Ward A')
        self.returns_correct_number_of_patients(-9)
