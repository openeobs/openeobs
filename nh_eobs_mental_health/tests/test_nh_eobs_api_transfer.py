from openerp.tests.common import TransactionCase


class TestNHeObsAPITransfer(TransactionCase):
    """
    Test that transferring a patient set's their obs_stop flag to False
    """

    def setUp(self):
        super(TestNHeObsAPITransfer, self).setUp()
        self.api_model = self.registry('nh.eobs.api')
        self.spell_model = self.registry('nh.clinical.spell')
        self.patient_model = self.registry('nh.clinical.patient')
        self.location_model = self.registry('nh.clinical.location')
        self.user_model = self.registry('res.users')
        self.pos_model = self.registry('nh.clinical.pos')
        self.activity_model = self.registry('nh.activity')
        self.wardboard_model = self.registry('nh.clinical.wardboard')
        self.pme_reason = \
            self.registry('nh.clinical.patient_monitoring_exception.reason')

        cr, uid = self.cr, self.uid
        hosp_id_search = self.location_model.search(
            cr, uid, [['usage', '=', 'hospital']]
        )
        if hosp_id_search:
            self.hospital_id = hosp_id_search[0]
        else:
            raise ValueError('Could not find hospital ID')

        pos_id_search = self.pos_model.search(
            cr, uid, [['location_id', '=', self.hospital_id]]
        )
        if pos_id_search:
            self.pos_id = pos_id_search[0]
        else:
            raise ValueError('Could not find POS with location ID of hospital')

        self.user_model.write(cr, uid, uid, {
            'pos_id': self.pos_id,
            'pos_ids': [[4, self.pos_id]]
        })

        self.location_model.create(
            cr, uid, {
                'name': 'Ward0',
                'code': 'W0',
                'usage': 'ward',
                'parent_id': self.hospital_id,
                'type': 'poc'
            }
        )

        self.location_model.create(
            cr, uid, {
                'name': 'Ward1',
                'code': 'W1',
                'usage': 'ward',
                'parent_id': self.hospital_id,
                'type': 'poc'
            }
        )

        # register, admit and place patient
        self.patient_id = self.api_model.register(cr, uid, 'TESTHN001', {
            'family_name': 'Testersen',
            'given_name': 'Test'
        })

        self.api_model.admit(
            cr, uid, 'TESTHN001', {'location': 'W0'}
        )

        self.spell_id = self.spell_model.search(
            cr, uid, [['patient_id', '=', self.patient_id]])[0]

        self.spell_activity_id = self.spell_model.read(
            cr, uid, self.spell_id, ['activity_id']).get('activity_id')[0]
        
        reason = self.pme_reason.browse(cr, uid, 1)
        self.wardboard_model.browse(
            cr, uid, self.spell_id) \
            .start_patient_monitoring_exception(reason, self.spell_id,
                                                self.spell_activity_id)

    def test_transfer_changes_flag(self):
        """
        TEst that when transferring a patient with a set obs_stop flag the flag
        is changed
        """
        cr, uid = self.cr, self.uid
        self.api_model.transfer(
            cr, uid, 'TESTHN001', {
                'from_location': 'W0',
                'location': 'W1'
            }, context={})
        spell = self.spell_model.read(cr, uid, self.spell_id, ['obs_stop'])
        self.assertFalse(spell.get('obs_stop', True))

    def test_transfer_creates_new_ews(self):
        """
        Test taht when transferring a patient with a set obs_stop flag an EWS
        observation is created due in an hour
        """
        cr, uid = self.cr, self.uid
        self.wardboard_model.cancel_open_ews(
            cr, uid, spell_activity_id=self.spell_activity_id)
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        self.spell_model.write(cr, uid, self.spell_id, {'obs_stop': True})
        self.api_model.transfer(
            cr, uid, 'TESTHN001', {
                'from_location': 'W0',
                'location': 'W1'
            }, context={})
        self.assertEqual(len(self.activity_model.search(cr, uid, domain)), 1)

    def test_transfer_ends_current_patient_montioring_exception(self):
        """
        Test that when the patient is transfered that the currently open
        Patient Monitoring Exception is cancelled
        """
        cr, uid = self.cr, self.uid
        domain = [
            ('data_model', '=', 'nh.clinical.patient_monitoring_exception'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        self.api_model.transfer(
            cr, uid, 'TESTHN001', {
                'from_location': 'W0',
                'location': 'W1'
            }, context={})
        self.assertEqual(len(self.activity_model.search(cr, uid, domain)),0)
