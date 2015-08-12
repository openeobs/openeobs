__author__ = 'colinwren'
from openerp.tests.common import TransactionCase
from openerp.tools import test_reports
from datetime import datetime, timedelta
import logging
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_eobs.report.print_observation_report import ObservationReport as obs_report
import copy

_logger = logging.getLogger(__name__)

class TestObservationReport(TransactionCase):

    ews_values = {
        'respiration_rate': 18,
        'indirect_oxymetry_spo2': 99,
        'oxygen_administration_flag': 0,
        'body_temperature': 37.5,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'pulse_rate': 65,
        'avpu_text': 'A',
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'create_date': '1988-01-12 06:00:00',
        'write_date': '1988-01-12 06:00:00',
        'score': '1',
        'clinical_risk': 'Medium'
    }

    ews_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'EWS,1',
        'terminate_uid': [1, 'Test'],
    }

    height_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'HEIGHT,1',
        'terminate_uid': [1, 'Test'],
    }

    weight_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'WEIGHT,1',
        'terminate_uid': [1, 'Test'],
    }

    pain_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'PAIN,1',
        'terminate_uid': [1, 'Test'],
    }

    blood_product_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'BLOODPRODUCT,1',
        'terminate_uid': [1, 'Test'],
    }

    stools_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'STOOLS,1',
        'terminate_uid': [1, 'Test'],
    }

    pbp_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'PBP,1',
        'terminate_uid': [1, 'Test'],
    }

    gcs_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'GCS,1',
        'terminate_uid': [1, 'Test'],
    }

    blood_sugar_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'BLOODSUGAR,1',
        'terminate_uid': [1, 'Test'],
    }

    o2target_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'O2TARGET,1',
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    mrsa_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'MRSA,1',
        'terminate_uid': [1, 'Test'],
    }

    diabetes_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'DIABETES,1',
        'terminate_uid': [1, 'Test'],
    }

    palliative_care_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'PALLIATIVECARE,1',
        'terminate_uid': [1, 'Test'],
    }

    post_surgery_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'POSTSURGERY,1',
        'terminate_uid': [1, 'Test'],
    }

    critical_care_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'CRITICALCARE,1',
        'terminate_uid': [1, 'Test'],
    }

    move_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'MOVE,1',
        'terminate_uid': [1, 'Test'],
    }

    triggered_ews_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_model': 'nh.clinical.patient.notification.test',
        'summary': 'Test Policy Notification',
        'notes': 'Test Notes',
        'user_id': [1, 'Test User']
    }

    height_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'height': 1.2
    }

    weight_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'weight': 1.2
    }

    pain_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'rest_score': 1,
        'movement_score': 9
    }

    blood_product_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'vol': 1,
        'product': 'rbc'
    }

    stools_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'bowel_open': False,
        'nausea': False,
        'vomiting': False,
        'quantity': 'large',
        'colour': 'yellow',
        'bristol_type': '7',
        'offensive': True,
        'strain': False,
        'laxatives': False,
        'samples': 'micro',
        'rectal_exam': True,
    }

    pbp_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'systolic_sitting': 120,
        'systolic_standing': 80,
        'diastolic_sitting': 120,
        'diastolic_standing': 80,
        'result': False
    }

    gcs_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'eyes': 'C',
        'verbal': 'T',
        'motor': '6',
        'score': 1
    }

    blood_sugar_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'blood_sugar': 1.2
    }

    o2target_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'level_id': [1, 'Test Level'],
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    mrsa_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'mrsa': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    diabetes_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'diabetes': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    palliative_care_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'status': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    post_surgery_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'status': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    critical_care_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'status': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    device_session_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'device_type_id': [1, 'Test Device'],
        'device_category_id': [1, 'Test Device Category'],
        'location': 'Test Location',
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test'],
        'planned': True,
        'removal_reason': 'Test Reason'
    }

    move_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'location_id': [1, 'Test Location']
    }

    location_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'name': 'Test Location',
        'parent_id': [2, 'Test Location Parent']
    }

    def setUp(self):
        super(TestObservationReport, self).setUp()
        registry, cr, uid = self.registry, self.cr, self.uid

        # Set up the report
        r_model = registry('ir.actions.report.xml')
        domain = [('report_name', 'like', 'observation_report')]
        r = r_model.browse(cr, uid, r_model.search(cr, uid, domain))
        self.report_model = 'report.%s' % r.report_name
        try:
            registry(self.report_model)
        except KeyError:
            self.failureException('Unable to load Observation Report')

        # Create demo data
        self.activity_pool = self.registry('nh.activity')
        self.user_pool = self.registry('res.users')
        self.partner_pool = self.registry('res.partner')
        self.group_pool = self.registry('res.groups')
        self.company_pool = self.registry('res.company')
        self.location_pool = self.registry('nh.clinical.location')
        self.pos_pool = self.registry('nh.clinical.pos')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.context_pool = self.registry('nh.clinical.context')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')
        self.height_pool = self.registry('nh.clinical.patient.observation.height')
        self.weight_pool = self.registry('nh.clinical.patient.observation.weight')
        self.api_pool = self.registry('nh.eobs.api')
        self.o2level_pool = self.registry('nh.clinical.o2level')
        self.o2target_pool = self.registry('nh.clinical.patient.o2target')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.pain_pool = self.registry('nh.clinical.patient.observation.pain')
        self.blood_product_pool = self.registry('nh.clinical.patient.observation.blood_product')
        self.stools_pool = self.registry('nh.clinical.patient.observation.stools')
        self.pbp_pool = self.registry('nh.clinical.patient.observation.pbp')
        self.gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
        self.blood_sugar_pool = self.registry('nh.clinical.patient.observation.blood_sugar')
        self.mrsa_pool = self.registry('nh.clinical.patient.mrsa')
        self.diabetes_pool = self.registry('nh.clinical.patient.diabetes')
        self.palliative_care_pool = self.registry('nh.clinical.patient.palliative_care')
        self.post_surgery_pool = self.registry('nh.clinical.patient.post_surgery')
        self.critical_care_pool = self.registry('nh.clinical.patient.critical_care')
        self.move_pool = self.registry('nh.clinical.patient.move')
        self.device_session_pool = self.registry('nh.clinical.device.session')

        def spell_pool_mock_spell(*args, **kwargs):
            return [{
                'date_started': '1987-12-26 06:00:00',
                'date_terminated': '1988-01-12 07:00:00',
                'activity_id': [1],
                'con_doctor_ids': [],
                'patient_id': [1],
                'id': 1,
                'code': '666'
            }]

        def patient_pool_mock_patient(*args, **kwargs):
            return [{
                'dob': '1988-01-12 06:00:00',
                'id': 1,
                'other_identifier': '1234123412',
                'gender': 'Male',
                'full_name': 'Test Patient',
                'patient_identifier': '1234123412'
            }]

        def activity_pool_mock_search(*args, **kwargs):
            search_filter = args[3] if len(args) > 3 else False
            model = search_filter[1][2] if len(search_filter) > 1 else False
            if not model:
                # If no model defined then we should be using a creator_id search
                if search_filter[0][0] == 'creator_id':
                    creator_id = search_filter[0][2]
                    ids = [
                        None,
                        [18]
                    ]
                    return ids[creator_id]
                else:
                    raise ValueError('Odd search filter passed')

            models = {
                'nh.clinical.patient.observation.ews': [1],
                'nh.clinical.patient.observation.height': [2],
                'nh.clinical.patient.observation.weight': [3],
                'nh.clinical.patient.observation.pain': [4],
                'nh.clinical.patient.observation.blood_product': [5],
                'nh.clinical.patient.observation.stools': [6],
                'nh.clinical.patient.observation.pbp': [7],
                'nh.clinical.patient.observation.gcs': [8],
                'nh.clinical.patient.observation.blood_sugar': [9],
                'nh.clinical.patient.observation.o2target': [10],
                'nh.clinical.patient.mrsa': [11],
                'nh.clinical.patient.diabetes': [12],
                'nh.clinical.patient.palliative_care': [13],
                'nh.clinical.patient.post_surgery': [14],
                'nh.clinical.patient.critical_care': [15],
                'nh.clinical.patient.move': [16],
                'nh.clinical.patient.o2target': [17]
            }
            return models.get(model)

        def activity_pool_mock_read(*args, **kwargs):
            id = args[3][0] if len(args) > 3 else False
            if not id:
                raise ValueError('No IDs passed')
            resps = [
                {},
                self.ews_data,
                self.height_data,
                self.weight_data,
                self.pain_data,
                self.blood_product_data,
                self.stools_data,
                self.pbp_data,
                self.gcs_data,
                self.blood_sugar_data,
                self.o2target_data,
                self.mrsa_data,
                self.diabetes_data,
                self.palliative_care_data,
                self.post_surgery_data,
                self.critical_care_data,
                self.move_data,
                self.o2target_data,
                self.triggered_ews_data
            ]
            return [copy.deepcopy(resps[id])]

        def ews_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.ews_values)

        def o2target_pool_mock_get_last(*args, **kwargs):
            return []

        def height_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.height_values)

        def weight_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.weight_values)

        def pain_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.pain_values)

        def blood_product_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.blood_product_values)

        def stools_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.stools_values)

        def pbp_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.pbp_values)

        def gcs_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.gcs_values)

        def blood_sugar_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.blood_sugar_values)

        def o2target_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.o2target_values)

        def mrsa_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.mrsa_values)

        def diabetes_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.diabetes_values)

        def palliative_care_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.palliative_care_values)

        def post_surgery_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.post_surgery_values)

        def critical_care_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.critical_care_values)

        def device_session_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.device_session_values)

        def move_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.move_values)

        def location_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.location_values)

        self.spell_pool._patch_method('read', spell_pool_mock_spell)
        self.patient_pool._patch_method('read', patient_pool_mock_patient)
        self.activity_pool._patch_method('search', activity_pool_mock_search)
        self.activity_pool._patch_method('read', activity_pool_mock_read)
        self.ews_pool._patch_method('read', ews_pool_mock_read)
        self.o2target_pool._patch_method('get_last', o2target_pool_mock_get_last)
        self.height_pool._patch_method('read', height_pool_mock_read)
        self.weight_pool._patch_method('read', weight_pool_mock_read)
        self.pain_pool._patch_method('read', pain_pool_mock_read)
        self.blood_product_pool._patch_method('read', blood_product_pool_mock_read)
        self.stools_pool._patch_method('read', stools_pool_mock_read)
        self.pbp_pool._patch_method('read', pbp_pool_mock_read)
        self.gcs_pool._patch_method('read', gcs_pool_mock_read)
        self.blood_sugar_pool._patch_method('read', blood_sugar_pool_mock_read)
        self.o2target_pool._patch_method('read', o2target_pool_mock_read)
        self.mrsa_pool._patch_method('read', mrsa_pool_mock_read)
        self.diabetes_pool._patch_method('read', diabetes_pool_mock_read)
        self.palliative_care_pool._patch_method('read', palliative_care_pool_mock_read)
        self.post_surgery_pool._patch_method('read', post_surgery_pool_mock_read)
        self.critical_care_pool._patch_method('read', critical_care_pool_mock_read)
        self.move_pool._patch_method('read', move_pool_mock_read)
        self.device_session_pool._patch_method('read', device_session_pool_mock_read)
        self.location_pool._patch_method('read', location_pool_mock_read)
        self.spell_id = 1

        self.start_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)
        self.end_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)

    def tearDown(self):
        self.spell_pool._revert_method('read')
        self.patient_pool._revert_method('read')
        self.activity_pool._revert_method('search')
        self.activity_pool._revert_method('read')
        self.ews_pool._revert_method('read')
        self.o2target_pool._revert_method('get_last')
        self.height_pool._revert_method('read')
        self.weight_pool._revert_method('read')
        self.pain_pool._revert_method('read')
        self.blood_product_pool._revert_method('read')
        self.stools_pool._revert_method('read')
        self.pbp_pool._revert_method('read')
        self.gcs_pool._revert_method('read')
        self.blood_sugar_pool._revert_method('read')
        self.o2target_pool._revert_method('read')
        self.mrsa_pool._revert_method('read')
        self.diabetes_pool._revert_method('read')
        self.palliative_care_pool._revert_method('read')
        self.post_surgery_pool._revert_method('read')
        self.critical_care_pool._revert_method('read')
        self.move_pool._revert_method('read')
        self.device_session_pool._revert_method('read')
        self.location_pool._revert_method('read')

    def test_01_observation_report_with_spell_without_start_time_without_end_time(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None
        })
        self.assertEqual(report_test, True, 'Unable to print Observation Report')

    def test_02_observation_report_with_spell_with_start_time_without_end_time(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None
        })
        self.assertEqual(report_test, True, 'Unable to print Observation Report')

    def test_03_observation_report_with_spell_with_start_time_with_end_time(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time
        })
        self.assertEqual(report_test, True, 'Unable to print Observation Report')

    def test_04_observation_report_with_spell_without_start_time_with_end_time(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time
        })
        self.assertEqual(report_test, True, 'Unable to print Observation Report')

    def test_05_observation_report_without_spell_without_start_time_with_end_time(self):
        with self.assertRaises(ValueError):
            report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
            report_test = test_reports.try_report(cr, uid, report_model, [], data={
                'spell_id': None,
                'start_time': None,
                'end_time': self.end_time
            })

    def test_06_observation_report_without_spell_without_start_time_without_end_time(self):
        with self.assertRaises(ValueError):
            report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
            report_test = test_reports.try_report(cr, uid, report_model, [], data={
                'spell_id': None,
                'start_time': None,
                'end_time': None
            })

    def test_07_observation_report_without_spell_with_start_time_without_end_time(self):
        with self.assertRaises(ValueError):
            report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
            report_test = test_reports.try_report(cr, uid, report_model, [], data={
                'spell_id': None,
                'start_time': self.start_time,
                'end_time': None
            })

    def test_08_observation_report_with_spell_with_start_time_with_end_time_with_ews_only(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        })
        self.assertEqual(report_test, True, 'Unable to print Observation Report')

    def test_09_observation_report_without_data(self):
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        with self.assertRaises(ValueError):
            test_reports.try_report(cr, uid, report_model, [])

    def test_10_convert_db_date_to_context_date_with_format(self):
        test_date = datetime.strptime('1988-01-12 06:00:00', '%Y-%m-%d %H:%M:%S')
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        rep = self.registry(self.report_model)
        convert_date = obs_report.convert_db_date_to_context_date(rep, cr, uid, test_date, '%Y')
        self.assertEqual(convert_date, '1988', 'Converted date is not in the right format')

    def test_11_convert_db_date_to_context_date_without_format(self):
        test_date = datetime.strptime('1988-01-12 06:00:00', '%Y-%m-%d %H:%M:%S')
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        rep = self.registry(self.report_model)
        convert_date = obs_report.convert_db_date_to_context_date(rep, cr, uid, test_date, None)
        self.assertEqual(str(convert_date), '1988-01-12 06:00:00+00:00', 'Converted date is not in the right format')
