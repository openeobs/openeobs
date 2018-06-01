from BeautifulSoup import BeautifulSoup

from openerp.tests.common import SavepointCase


fake_timedelta = None


class TestRenderHtmlBase(SavepointCase):

    def setUp(self):
        super(TestRenderHtmlBase, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']
        self.therapeutic_level_model = \
            self.env['nh.clinical.therapeutic.level']
        self.therapeutic_obs_model = \
            self.env['nh.clinical.patient.observation.therapeutic']
        self.datetime_utils_model = self.env['datetime_utils']

        self.report_wizard = self.report_wizard_model.create({})
        self.report_wizard.spell_id = self.spell.id

    def call_test(self):
        self.report_html = \
            self.report_model.render_html(data=self.report_wizard)
        self.soup = BeautifulSoup(self.report_html, isHTML=True)


class TestRenderHtmlTherapeuticLevel(TestRenderHtmlBase):

    def setUp(self):
        super(TestRenderHtmlTherapeuticLevel, self).setUp()
        self.shift_coordinator = \
            self.test_utils_model.create_shift_coordinator()

    def _create_level(self, obs_data=None):
        if not obs_data:
            obs_data = {
                'patient': self.patient.id,
                'level': 3,
                'staff_to_patient_ratio': 3
            }
        return self.therapeutic_level_model.sudo(self.shift_coordinator)\
            .create(obs_data)

    def _get_table_cells(self, field_name):
        section = self.soup.find(id='therapeutic-level-history')
        all_table_cells = section.find('tbody').findAll('td')

        class_name = 'therapeutic-level-{}'.format(field_name)
        all_date_cells = filter(
            lambda cell: class_name in cell['class'],
            all_table_cells
        )

        return all_date_cells

    def test_no_therapeutic_level_history_section_when_no_level_set(self):
        self.call_test()
        section = self.soup.find(id='therapeutic-level-history')
        self.assertFalse(section)

    def test_therapeutic_level_history_section_exists_when_level_set(self):
        self._create_level()
        self.call_test()
        section = self.soup.find(id='therapeutic-level-history')
        self.assertTrue(section)

    def test_therapeutic_levels_are_in_chronological_order(self):
        level_1 = self._create_level()
        level_2 = self._create_level()
        level_3 = self._create_level()

        expected = [level_1.id, level_2.id, level_3.id]
        report_data = self.report_model.get_report_data(self.report_wizard)
        actual = map(
            lambda level: level['id'], report_data['therapeutic_level_history']
        )

        self.assertEqual(expected, actual)

    def test_table_has_date(self):
        level = self._create_level()
        expected = self.datetime_utils_model \
            .reformat_server_datetime_for_frontend(
                level.create_date, two_character_year=True
            )

        self.call_test()

        actual = self._get_table_cells('date')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_level(self):
        level = self._create_level()
        expected = str(level.level)

        self.call_test()

        actual = self._get_table_cells('level')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_frequency(self):
        self._create_level()
        expected = 'Every Hour'

        self.call_test()

        actual = self._get_table_cells('frequency')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_staff_to_patient_ratio(self):
        self._create_level()
        expected = '3:1'

        self.call_test()

        actual = self._get_table_cells('staff-to-patient-ratio')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_blank_staff_to_patient_ratio_on_level_1(self):
        self._create_level(obs_data={
            'patient': self.patient.id,
            'level': 1
        })
        expected = ''

        self.call_test()

        actual = self._get_table_cells('staff-to-patient-ratio')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_user(self):
        self._create_level()
        expected = self.shift_coordinator.name

        self.call_test()

        actual = self._get_table_cells('user')[0].text
        self.assertEqual(expected, actual)


class TestRenderHtmlTherapeuticObservations(TestRenderHtmlBase):

    def _create_obs(self):
        obs_activity_id = self.therapeutic_obs_model.create_activity(
            {},
            {
                'patient_id': self.patient.id,
                'patient_status': 'AW',
                'location': 'Over there.',
                'areas_of_concern': 'The frontal area.',
                'one_to_one_intervention_needed': True,
                'other_staff_during_intervention': 'Dave.',
                'other_notes': 'And it was good.'
            }
        )
        activity_model = self.env['nh.activity']
        obs_activity = activity_model.browse(obs_activity_id)
        obs_activity.sudo(self.nurse).complete()
        obs = obs_activity.data_ref
        return obs

    def _get_table_cells(self, field_name):
        section = self.soup.find(id='therapeutic-observations')
        all_table_cells = section.find('tbody').findAll('td')

        class_name = 'therapeutic-observation-{}'.format(field_name)
        all_date_cells = filter(
            lambda cell: class_name in cell['class'],
            all_table_cells
        )

        return all_date_cells

    def test_no_therapeutic_observations_section_when_no_obs_taken(self):
        self.call_test()
        section = self.soup.find(id='therapeutic-observations')
        self.assertFalse(section)

    def test_therapeutic_observations_section_exists_obs_taken(self):
        self._create_obs()
        self.call_test()
        section = self.soup.find(id='therapeutic-observations')
        self.assertTrue(section)

    def test_therapeutic_observations_are_in_chronological_order(self):
        obs_1 = self._create_obs()
        obs_2 = self._create_obs()
        obs_3 = self._create_obs()
        expected = [obs_1.id, obs_2.id, obs_3.id]

        self.call_test()

        report_data = self.report_model.get_report_data(self.report_wizard)
        actual = map(
            lambda obs: obs['id'], report_data['therapeutic_observations']
        )
        self.assertEqual(expected, actual)

    def test_table_has_date(self):
        obs = self._create_obs()
        expected = self.datetime_utils_model\
            .reformat_server_datetime_for_frontend(
                obs.create_date, two_character_year=True
            )

        self.call_test()

        actual = self._get_table_cells('date')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_patient_status(self):
        self._create_obs()
        expected = 'Awake'

        self.call_test()

        actual = self._get_table_cells('patient-status')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_location(self):
        self._create_obs()
        expected = 'Over there.'

        self.call_test()

        actual = self._get_table_cells('location')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_areas_of_concern(self):
        self._create_obs()
        expected = 'The frontal area.'

        self.call_test()

        actual = self._get_table_cells('areas-of-concern')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_intervention(self):
        self._create_obs()
        expected = 'Yes'

        self.call_test()

        actual = self._get_table_cells('intervention')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_other_staff(self):
        self._create_obs()
        expected = 'Dave.'

        self.call_test()

        actual = self._get_table_cells('other-staff-during-intervention')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_other_notes(self):
        self._create_obs()
        expected = 'And it was good.'

        self.call_test()

        actual = self._get_table_cells('other-notes')[0].text
        self.assertEqual(expected, actual)

    def test_table_has_user(self):
        self._create_obs()
        expected = self.nurse.name

        self.call_test()

        actual = self._get_table_cells('user')[0].text
        self.assertEqual(expected, actual)
