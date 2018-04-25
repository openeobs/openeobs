from openerp.tests.common import SavepointCase


class TestSpellManagementPatientUpdate(SavepointCase):
    """
    Test that updating the name of a patient record for a spell then updates
    the spell management board.
    """
    def setUp(self):
        super(TestSpellManagementPatientUpdate, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.setup_ward()
        self.test_utils_model.create_patient()
        self.adt_user = self.test_utils_model.create_adt_user()
        self.test_utils_model.copy_instance_variables(self)

        self.spellboard_model = self.env['nh.clinical.spellboard']
        self.spell_activity = self.spellboard_model.sudo(self.adt_user)\
            .create({
                'patient_id': self.patient.id,
                'location_id': self.ward.id,
                'code': 'TESTPATIENTSPELL',
                'start_date': '2016-07-18 00:00:00'
            })

    def test_updates_patient_name(self):
        """
        Check that on updating the patient name on the patient object the
        spellboard object has the correct name.
        """
        self.patient.given_name = 'Updated-Test'
        self.patient.family_name = 'Patient'

        self.spellboard_pool = self.registry('nh.clinical.spellboard')
        cr, uid = self.cr, self.uid
        # Test only works with spellboard's override of read,
        # cannot use browse.
        spellboard = self.spellboard_pool.read(cr, uid, [self.spell_activity.id])[0]
        self.assertEqual(
            spellboard.get('patient_id', [0, ''])[1],
            'Patient, Updated-Test'
        )
