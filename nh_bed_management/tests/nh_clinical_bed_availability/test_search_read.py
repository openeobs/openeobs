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

    def test_returns_correct_number_of_hospitals(self):
        all_hospitals = self.location_model.search([
            ('usage', '=', 'hospital')
        ])
        expected = len(all_hospitals)

        bed_availability_records = self.call_test()

        def is_hospital(bed_availability_record):
            if bed_availability_record['hospital_name'] \
                    and not bed_availability_record['ward_name'] \
                    and not bed_availability_record['bed_name']:
                return True
            return False

        bed_availability_records_hospitals_only = \
            filter(is_hospital, bed_availability_records)
        actual = len(bed_availability_records_hospitals_only)

        self.assertEqual(expected, actual)

    def test_returns_correct_number_of_wards(self):
        all_hospitals = self.location_model.search([
            ('usage', '=', 'ward')
        ])
        expected = len(all_hospitals)

        bed_availability_records = self.call_test()

        def is_ward(bed_availability_record):
            if bed_availability_record['hospital_name'] \
                    and bed_availability_record['ward_name'] \
                    and not bed_availability_record['bed_name']:
                return True
            return False

        bed_availability_records_hospitals_only = \
            filter(is_ward, bed_availability_records)
        actual = len(bed_availability_records_hospitals_only)

        self.assertEqual(expected, actual)

    def test_returns_correct_number_of_beds(self):
        all_hospitals = self.location_model.search([
            ('usage', '=', 'bed')
        ])
        expected = len(all_hospitals)

        bed_availability_records = self.call_test()

        def is_bed(bed_availability_record):
            if bed_availability_record['hospital_name'] \
                    and bed_availability_record['ward_name'] \
                    and bed_availability_record['bed_name']:
                return True
            return False

        bed_availability_records_hospitals_only = \
            filter(is_bed, bed_availability_records)
        actual = len(bed_availability_records_hospitals_only)

        self.assertEqual(expected, actual)

    def test_can_be_sorted_on_one_field(self):
        order = 'bed_status asc'
        expected_order = [None, 'Available', 'Occupied']

        bed_availability_records = self.call_test(order=order)
        bed_statuses_only = map(lambda i: i['bed_status'],
                                bed_availability_records)

        actual_order = []
        # Using a wacky string because `None` and `False` are possible values.
        last_bed_status = 'a value that the bed status should not be'
        for bed_status in bed_statuses_only:
            if bed_status != last_bed_status:
                actual_order.append(bed_status)
                last_bed_status = bed_status

        self.assertEqual(expected_order, actual_order)

    def test_can_be_sorted_on_two_fields(self):
        order = 'ward_name desc, bed_status asc'

        locations = []
        for colour in ['Yellow', 'Red', 'Blue']:
            ward = self.test_utils.create_location(
                usage='ward',
                parent=self.hospital.id,
                name='The {} Ward'.format(colour)
            )
            locations.append(ward)
            for size in ['Small', 'Medium', 'Large']:
                bed = self.test_utils.create_location(
                    usage='bed',
                    parent=self.hospital.id,
                    name='The {} Bed'.format(size)
                )
                locations.append(bed)

        expected_order = [
            ('The Yellow Ward', 'The Large Bed'),
            ('The Red Ward', 'The Medium Bed'),
            ('The Blue Ward', 'The Small Bed'),
        ]

        bed_availability_records = self.call_test(order=order)
        # Could be demo data in this instance so filter the records down to
        # just those created in this test.
        bed_availability_records = filter(
            lambda i: i in locations,
            bed_availability_records
        )
        # Now filter down to ward and bed names only so can easily compare.
        ward_and_bed_names_only = map(
            lambda i: (i['ward_name'], i['bed_name']),
            bed_availability_records
        )

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
        actual_hospital_name_string = bed_availability_fields['hospital_name'].string
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
