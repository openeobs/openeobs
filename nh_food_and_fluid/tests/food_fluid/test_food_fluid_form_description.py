from openerp.tests.common import TransactionCase


class TestFoodFluidFormDescription(TransactionCase):
    """
    Test that the form_description for food and fluid is returning the correct
    information
    """

    def setUp(self):
        super(TestFoodFluidFormDescription, self).setUp()
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.form_desc = food_fluid_model.get_form_description(1)

    def test_recorded_concerns_dict(self):
        """
        Test that the recorded concerns dict show that the field should be a
        set of tickboxes for each nh.clinical.recorded_concern option
        """
        entry = self.form_desc[0]
        options = [
            'Dehydrated',
            'Underweight / Malnourished',
            'Refeeding Syndrome Risk',
            'Medical Reason',
            'Swallowing Risk - Modified Texture',
            'Eating and Drinking Poorly'
        ]
        self.assertEqual(entry.get('name'), 'recorded_concerns')
        self.assertEqual(entry.get('type'), 'multiselect')
        self.assertEqual(entry.get('label'), 'Recorded Concerns')
        self.assertEqual([rec[1] for rec in entry.get('selection')], options)

    def test_dietary_needs_dict(self):
        """
        Test that the dietary needs dict shows that the field should be a set
        of tickboxes for each nh.clinical.dietary_need option
        """
        entry = self.form_desc[1]
        options = [
            'Religious / Cultural',
            'Vegan / Vegetarian',
            'Food Sensitivity / Allergy'
        ]
        self.assertEqual(entry.get('name'), 'dietary_needs')
        self.assertEqual(entry.get('type'), 'multiselect')
        self.assertEqual(entry.get('label'), 'Consider Special Dietary Needs')
        self.assertEqual([rec[1] for rec in entry.get('selection')], options)

    def test_fluid_taken_dict(self):
        """
        Test that the fluid taken dict shows that the field should be a number
        input with a step of 0, a min of 0 and a max of 5000
        """
        entry = self.form_desc[2]
        self.assertEqual(entry.get('name'), 'fluid_taken')
        self.assertEqual(entry.get('type'), 'integer')
        self.assertEqual(entry.get('min'), 0)
        self.assertEqual(entry.get('max'), 5000)
        self.assertEqual(
            entry.get('label'), 'Fluid Taken (ml) - Include IV / NG')
        reference = entry.get('reference')
        self.assertIsNotNone(reference)
        self.assertEqual(reference.get('type'), 'iframe')
        self.assertEqual(reference.get('url'),
                         '/nh_food_and_fluid/static/src/html/fluid_taken.html')
        self.assertEqual(reference.get('title'),
                         'Fluid Taken Guidelines')
        self.assertEqual(reference.get('label'),
                         'Fluid Taken Guidelines')

    def test_fluid_description_dict(self):
        """
        Test that the fluid description dict shows that the field should be a
        textarea
        """
        entry = self.form_desc[3]
        self.assertEqual(entry.get('name'), 'fluid_description')
        self.assertEqual(entry.get('type'), 'text')
        self.assertEqual(entry.get('label'), 'Fluid Description')

    def test_food_taken_dict(self):
        """
        Test that the food taken dict shows that the field should be a textarea
        """
        entry = self.form_desc[4]
        self.assertEqual(entry.get('name'), 'food_taken')
        self.assertEqual(entry.get('type'), 'text')
        self.assertEqual(entry.get('label'), 'Food Taken')

    def test_food_fluid_rejected_dict(self):
        """
        Test that the food and fluid offered but rejected dict shows that the
        field should be a textarea
        """
        entry = self.form_desc[5]
        self.assertEqual(entry.get('name'), 'food_fluid_rejected')
        self.assertEqual(entry.get('type'), 'text')
        self.assertEqual(
            entry.get('label'), 'Food and Fluid Offered but Rejected')

    def test_passed_urine_dict(self):
        """
        Test that the passed urine dict shows that the field should be a select
        input with the following options:
        - Yes
        - No
        - Unknown
        """
        entry = self.form_desc[6]
        options = [
            'Yes',
            'No',
            'Unknown'
        ]
        self.assertEqual(entry.get('name'), 'passed_urine')
        self.assertEqual(entry.get('type'), 'selection')
        self.assertEqual(entry.get('label'), 'Passed Urine')
        self.assertTrue(entry.get('mandatory'))
        self.assertEqual([rec[1] for rec in entry.get('selection')], options)

    def test_bowels_open_dict(self):
        """
        Test that the bowels open dict shows that the field should be a select
        input with the following options:
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
        entry = self.form_desc[7]
        options = [
            'No',
            'Unknown',
            'Type 1',
            'Type 2',
            'Type 3',
            'Type 4',
            'Type 5',
            'Type 6',
            'Type 7'
        ]
        self.assertEqual(entry.get('name'), 'bowels_open')
        self.assertEqual(entry.get('type'), 'selection')
        self.assertEqual(entry.get('label'), 'Bowels Open')
        self.assertTrue(entry.get('mandatory'))
        self.assertEqual([rec[1] for rec in entry.get('selection')], options)
        reference = entry.get('reference')
        self.assertIsNotNone(reference)
        self.assertEqual(reference.get('type'), 'image')
        self.assertEqual(reference.get('url'),
            '/nh_stools/static/src/img/bristol_stools.png')
        self.assertEqual(reference.get('title'),
                         'Bristol Stools Reference Chart')
        self.assertEqual(reference.get('label'),
                         'Bristol Stools Reference Chart')
