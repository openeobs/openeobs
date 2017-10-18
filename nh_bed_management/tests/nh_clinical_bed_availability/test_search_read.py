# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestSearchRead(TransactionCase):
    """
    Test search_read as that is the method called by the client to populate
    views.
    """
    def setUp(self):
        super(TestSearchRead, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.ward = self.test_utils.ward
        self.hospital = self.test_utils.hospital

        self.bed_availability_model = self.env['nh.clinical.bed_availability']
        self.location_model = self.env['nh.clinical.location']

        self.available = 'Available'
        self.occupied = 'Occupied'

    def call_test(self, order=None):
        return self.bed_availability_model.search_read([], order=order)

    def test_returns_a_list(self):
        return_value = self.call_test()
        self.assertTrue(isinstance(return_value, list))

    def test_returns_correct_number_of_records(self):
        all_beds = self.location_model.search([
            ('usage', '=', 'bed')
        ])
        expected = len(all_beds)
        bed_availability_records = self.call_test()
        # 2 locations created in this test that were not present when the
        # bed availability records where created during model initialisation.
        actual = len(bed_availability_records) + 2

        self.assertEqual(expected, actual)

    def test_can_be_sorted_on_one_field(self):
        order = 'ward_name desc'

        beds = []
        colours = ['Yellow', 'Red', 'Blue']
        ward_names = ['The {} Ward'.format(colour) for colour in colours]
        sizes = ['Small', 'Medium', 'Large']
        bed_names = ['The {} Bed'.format(size) for size in sizes]
        for ward_name in ward_names:
            ward = self.test_utils.create_location(
                usage='ward',
                parent=self.hospital.id,
                name=ward_name
            )

            for bed_name in bed_names:
                bed = self.test_utils.create_location(
                    usage='bed',
                    parent=ward.id,
                    name=bed_name
                )
                beds.append(bed)

        expected_order = [
            'The Yellow Ward',
            'The Yellow Ward',
            'The Yellow Ward',
            'The Red Ward',
            'The Red Ward',
            'The Red Ward',
            'The Blue Ward',
            'The Blue Ward',
            'The Blue Ward'
        ]

        bed_availability_records = []
        for bed in beds:
            record = self.bed_availability_model.create({
                'location': bed.id
            })
            bed_availability_records.append(record)

        bed_availability_records = self.call_test(order=order)

        # Could be demo data in the LiveObs instance running this test so
        # filter to only the bed availability records created in this test.
        bed_availability_records = filter(
            lambda ba_record: ba_record['ward_name'] in ward_names,
            bed_availability_records)

        # Map to ward and bed names only so can easily compare.
        bed_names_only = map(
            lambda ba_record: ba_record['ward_name'],
            bed_availability_records)

        actual_order = bed_names_only
        self.assertEqual(expected_order, actual_order)

    def test_can_be_sorted_on_two_fields(self):
        order = 'ward_name desc, bed_name asc'

        beds = []
        colours = ['Yellow', 'Red', 'Blue']
        ward_names = ['The {} Ward'.format(colour) for colour in colours]
        sizes = ['Small', 'Medium', 'Large']
        bed_names = ['The {} Bed'.format(size) for size in sizes]
        for ward_name in ward_names:
            ward = self.test_utils.create_location(
                usage='ward',
                parent=self.hospital.id,
                name=ward_name
            )

            for bed_name in bed_names:
                bed = self.test_utils.create_location(
                    usage='bed',
                    parent=ward.id,
                    name=bed_name
                )
                beds.append(bed)

        expected_order = [
            ('The Yellow Ward', 'The Large Bed'),
            ('The Yellow Ward', 'The Medium Bed'),
            ('The Yellow Ward', 'The Small Bed'),
            ('The Red Ward', 'The Large Bed'),
            ('The Red Ward', 'The Medium Bed'),
            ('The Red Ward', 'The Small Bed'),
            ('The Blue Ward', 'The Large Bed'),
            ('The Blue Ward', 'The Medium Bed'),
            ('The Blue Ward', 'The Small Bed')
        ]

        bed_availability_records = []
        for bed in beds:
            record = self.bed_availability_model.create({
                'location': bed.id
            })
            bed_availability_records.append(record)

        # Call `search_read` to get an ordered recordset.
        bed_availability_records = self.call_test(order=order)

        # Could be demo data in the LiveObs instance running this test so
        # filter to only the bed availability records created in this test.
        bed_availability_records = filter(
            lambda record: record['ward_name'] in ward_names,
            bed_availability_records)

        # Map to ward and bed names only so can easily compare.
        ward_and_bed_names_only = map(
            lambda record: (record['ward_name'], record['bed_name']),
            bed_availability_records)

        actual_order = ward_and_bed_names_only
        self.assertEqual(expected_order, actual_order)

    def test_field_strings(self):
        """
        These strings are used as the headers for list views.
        """
        expected_hospital_name_string = 'Hospital Name'
        expected_ward_name_string = 'Ward Name'
        expected_bed_name_string = 'Bed Name'
        expected_bed_status_string = 'Bed Status'

        bed_availability_fields = self.bed_availability_model._fields
        actual_hospital_name_string = \
            bed_availability_fields['hospital_name'].string
        actual_ward_name_string = bed_availability_fields['ward_name'].string
        actual_bed_name_string = bed_availability_fields['bed_name'].string
        actual_bed_status_string = bed_availability_fields['bed_status'].string

        self.assertEqual(expected_hospital_name_string,
                         actual_hospital_name_string)
        self.assertEqual(expected_ward_name_string,
                         actual_ward_name_string)
        self.assertEqual(expected_bed_name_string,
                         actual_bed_name_string)
        self.assertEqual(expected_bed_status_string,
                         actual_bed_status_string)
