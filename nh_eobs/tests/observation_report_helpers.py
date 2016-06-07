from openerp.tests.common import TransactionCase
from datetime import timedelta
from datetime import datetime
import copy


class OxygenLevel(object):
    def __init__(self, name, omin, omax, active):
        self.name = name
        self.min = omin
        self.max = omax
        self.active = active


class ObservationReportHelpers(TransactionCase):

    pretty_date_format = '%H:%M %d/%m/%y'
    wkhtmltopdf_format = "%a %b %d %Y %H:%M:%S GMT"
    odoo_date_format = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def boolean_to_text(value):
        value_as_text = 'No'
        if value:
            value_as_text = 'Yes'
        return value_as_text

    ews_values = {
        'respiration_rate': 18,
        'indirect_oxymetry_spo2': 99,
        'oxygen_administration_flag': True,
        'body_temperature': 37.5,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'pulse_rate': 65,
        'avpu_text': 'A',
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:01:00',
        'create_date': '1988-01-12 06:00:00',
        'write_date': '1988-01-12 06:00:00',
        'score': '1',
        'clinical_risk': 'Medium',
        'is_partial': False,
        'device_id': [1, 'Test Device'],
        'flow_rate': 5,
        'concentration': 0,
        'cpap_peep': 0,
        'niv_backup': 0,
        'niv_ipap': 0,
        'niv_epap': 0
    }

    ews_data = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:01:00',
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

    o2level_data = {
        'data_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'data_ref': 'O2LEVEL,1',
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

    o2level_values = OxygenLevel('0-100', 0, 100, True)

    mrsa_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'status': True,
        'terminate_uid': [1, 'Test'],
        'write_uid': [1, 'Test']
    }

    diabetes_values = {
        'date_started': '1988-01-12 06:00:00',
        'date_terminated': '1988-01-12 06:00:01',
        'id': 1,
        'status': True,
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
        'planned': 'planned',
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

    test_logo = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAACXBIWXMAAAs' \
                'TAAALEwEAmpwYAAAAB3RJTUUH3wwRCyIdyggcuQAAAFZJREFUKM/dkksKAD' \
                'EIQ5PB+185XRREWjPQTRfNTp8/VEoCQBIAgGlWLSimK+MSpyqSFA47hRvAl' \
                'Tju8OFQLyRwP82+6BpweaTl3q0/JDnclvj70/ZlBnbIORjQZ6obAAAAAElF' \
                'TkSuQmCC'

    company_logo_values = {
        'id': 1,
        'image': test_logo
    }

    company_name_values = {
        'id': 1,
        'name': 'Test Hospital'
    }

    o2target_id = [1]

    def setUp(self):
        super(ObservationReportHelpers, self).setUp()
        registry, cr, uid = self.registry, self.cr, self.uid

        # Set up the report
        r_model = registry('ir.actions.report.xml')
        domain = [('report_name', 'like', 'observation_report')]
        r = r_model.browse(cr, uid, r_model.search(cr, uid, domain))
        self.report_model = 'report.%s' % r.report_name
        try:
            self.report_pool = registry(self.report_model)
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
        self.height_pool = \
            self.registry('nh.clinical.patient.observation.height')
        self.weight_pool = \
            self.registry('nh.clinical.patient.observation.weight')
        self.api_pool = self.registry('nh.eobs.api')
        self.o2level_pool = self.registry('nh.clinical.o2level')
        self.o2target_pool = self.registry('nh.clinical.patient.o2target')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.pain_pool = self.registry('nh.clinical.patient.observation.pain')
        self.blood_product_pool = \
            self.registry('nh.clinical.patient.observation.blood_product')
        self.stools_pool = \
            self.registry('nh.clinical.patient.observation.stools')
        self.pbp_pool = self.registry('nh.clinical.patient.observation.pbp')
        self.gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
        self.blood_sugar_pool = \
            self.registry('nh.clinical.patient.observation.blood_sugar')
        self.mrsa_pool = self.registry('nh.clinical.patient.mrsa')
        self.diabetes_pool = self.registry('nh.clinical.patient.diabetes')
        self.palliative_care_pool = \
            self.registry('nh.clinical.patient.palliative_care')
        self.post_surgery_pool = \
            self.registry('nh.clinical.patient.post_surgery')
        self.critical_care_pool = \
            self.registry('nh.clinical.patient.critical_care')
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
                'other_identifier': 'NHS1234123',
                'gender': 'Male',
                'full_name': 'Test Patient',
                'patient_identifier': 'HOS1234123'
            }]

        def activity_pool_mock_search(*args, **kwargs):
            search_filter = args[3] if len(args) > 3 else False
            model = search_filter[1][2] if len(search_filter) > 1 else False
            if not model:
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
            aid = args[3][0] if len(args) > 3 else False
            if not aid:
                raise ValueError('No IDs passed')
            resps = [
                False,
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
                self.move_data if self.move_data else False,
                self.o2target_data,
                self.triggered_ews_data
            ]
            return [copy.deepcopy(resps[aid])] if resps[aid] else []

        def ews_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.ews_values)

        def o2target_pool_mock_get_last(*args, **kwargs):
            return self.o2target_id

        def o2level_pool_mock_browse(*args, **kwargs):
            return copy.deepcopy(self.o2level_values)

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

        def partner_pool_mock_read(*args, **kwargs):
            if len(args) == 2:
                return partner_pool_mock_read.origin(
                    args[0],
                    args[1],
                    kwargs
                )
            return copy.deepcopy(self.company_logo_values)

        def company_pool_mock_read(*args, **kwargs):
            return copy.deepcopy(self.company_name_values)

        def mock_triggered_actions(*args, **kwargs):
            return [18]

        self.report_pool._patch_method('get_triggered_actions',
                                       mock_triggered_actions)
        self.spell_pool._patch_method('read', spell_pool_mock_spell)
        self.patient_pool._patch_method('read', patient_pool_mock_patient)
        self.activity_pool._patch_method('search', activity_pool_mock_search)
        self.activity_pool._patch_method('read', activity_pool_mock_read)
        self.ews_pool._patch_method('read', ews_pool_mock_read)
        self.o2target_pool._patch_method('get_last',
                                         o2target_pool_mock_get_last)
        self.height_pool._patch_method('read', height_pool_mock_read)
        self.weight_pool._patch_method('read', weight_pool_mock_read)
        self.pain_pool._patch_method('read', pain_pool_mock_read)
        self.blood_product_pool._patch_method('read',
                                              blood_product_pool_mock_read)
        self.stools_pool._patch_method('read', stools_pool_mock_read)
        self.pbp_pool._patch_method('read', pbp_pool_mock_read)
        self.gcs_pool._patch_method('read', gcs_pool_mock_read)
        self.blood_sugar_pool._patch_method('read',
                                            blood_sugar_pool_mock_read)
        self.o2target_pool._patch_method('read', o2target_pool_mock_read)
        self.o2level_pool._patch_method('browse', o2level_pool_mock_browse)
        self.mrsa_pool._patch_method('read', mrsa_pool_mock_read)
        self.diabetes_pool._patch_method('read', diabetes_pool_mock_read)
        self.palliative_care_pool._patch_method('read',
                                                palliative_care_pool_mock_read)
        self.post_surgery_pool._patch_method('read',
                                             post_surgery_pool_mock_read)
        self.critical_care_pool._patch_method('read',
                                              critical_care_pool_mock_read)
        self.move_pool._patch_method('read', move_pool_mock_read)
        self.device_session_pool._patch_method('read',
                                               device_session_pool_mock_read)
        self.location_pool._patch_method('read', location_pool_mock_read)
        self.partner_pool._patch_method('read', partner_pool_mock_read)
        self.company_pool._patch_method('read', company_pool_mock_read)
        self.spell_id = 1
        self.start_time = datetime.now() + timedelta(days=5)
        self.end_time = datetime.now() + timedelta(days=5)

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
        self.partner_pool._revert_method('read')
        self.company_pool._revert_method('read')
        self.o2level_pool._revert_method('browse')
        self.report_pool._revert_method('get_triggered_actions')
        super(ObservationReportHelpers, self).tearDown()
