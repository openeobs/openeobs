from openerp.tests.common import SingleTransactionCase


class TestPlacementPatientNameGet(SingleTransactionCase):
    """
    Test that on updating patient name that the patient's without a bed
    view is updated to reflect this
    """

    @classmethod
    def setUpClass(cls):
        super(TestPlacementPatientNameGet, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.user_pool = cls.registry('res.users')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.placement_pool = cls.registry('nh.clinical.patient.placement')

        wards = cls.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        ward = wards[0]
        cls.ward = ward

        shift_coordinators = cls.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', [ward]]
        ])
        if not shift_coordinators:
            raise ValueError('Could not find shift coordinator for test')

        placements = cls.placement_pool.search(cr, uid, [
            ['state', 'not in', ['cancelled', 'completed']],
            ['suggested_location_id', 'in', [ward]]])
        if not placements:
            raise ValueError('Could not find placements for test')
        cls.placement = placements[0]

        placement_patient = cls.placement_pool.read(
            cr, uid, cls.placement, ['patient_id'])
        cls.patient = cls.patient_pool.read(
            cr, uid, placement_patient.get('patient_id', [0, ''])[0])

    def test_patients_without_bed_name_update(self):
        """
        TEst that the patients without bed shows updated patient name
        """
        cr, uid = self.cr, self.uid
        before_placement = self.placement_pool.read(
            cr, uid, self.placement, ['patient_id'])
        self.assertEqual(before_placement.get('patient_id', [0, ''])[1],
                         self.patient.get('display_name'))
        self.patient_pool.write(cr, uid, self.patient.get('id'), {
            'given_name': 'Colin',
            'middle_names': False,
            'family_name': 'Wren'
        })
        after_placement = self.placement_pool.read(
            cr, uid, self.placement, ['patient_id'])
        self.assertEqual(after_placement.get('patient_id', [0, ''])[1],
                         'Wren, Colin')
