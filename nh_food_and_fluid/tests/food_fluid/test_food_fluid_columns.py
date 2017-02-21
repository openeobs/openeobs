from openerp.tests.common import TransactionCase


class TestFoodFluidColumns(TransactionCase):
    """
    Test the food and fluid model structure
    """

    def setUp(self):
        super(TestFoodFluidColumns, self).setUp()
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.food_fluid_ob = food_fluid_model.new({
            'recorded_concerns': [[6, 0, [1]]],
            'dietary_needs': [[6, 0, [1]]],
            'fluid_taken': 1000,
            'fluid_description': 'A print of the black stuff - Bovril',
            'food_taken': 'A slice of fried gold',
            'food_fluid_rejected': 'I can\'t believe you\'ve done this',
            'passed_urine': 'yes',
            'bowels_open': 'type_1'
        })

    def test_recorded_concern_column(self):
        """
        Test has recorded concern column that takes a list of recorded concern
        options
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'recorded_concerns'))

    def test_dietary_needs_column(self):
        """
        Test has dietary needs column that takes a list of dietary need options
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'dietary_needs'))

    def test_fluid_taken_column(self):
        """
        Test has fluid taken column that takes integer of fluid taken
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'fluid_taken'))

    def test_fluid_description_column(self):
        """
        Test has fluid description column that takes free text of fluid taken
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'fluid_description'))

    def test_food_taken_column(self):
        """
        Test has food taken column that takes free text of food eaten
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'food_taken'))

    def test_food_fluid_rejected_column(self):
        """
        Test has food and fluid offered but rejected column that takes free
        text so user can document which food and fluid was rejected by patient
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'food_fluid_rejected'))

    def test_passed_urine_column(self):
        """
        Test has mandatory passed urine column that takes 3 options:
        - Yes
        - No
        - Unknown
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'passed_urine'))

    def test_bowels_open_column(self):
        """
        Test has mandatory bowels open column that takes 9 options:
        - No
        - Unknown
        - Type 1
        - Type 2
        - Type 3
        - Type 4
        - Type 5
        - Type 6
        - Type 7
        """
        self.assertTrue(hasattr(self.food_fluid_ob, 'bowels_open'))
