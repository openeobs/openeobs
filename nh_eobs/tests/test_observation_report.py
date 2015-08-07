__author__ = 'colinwren'
from openerp.tests.common import TransactionCase
from openerp.tools import test_reports
from datetime import datetime, timedelta
import logging
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from openerp.addons.nh_eobs.report.print_observation_report import ObservationReport as obs_report

_logger = logging.getLogger(__name__)

class TestObservationReport(TransactionCase):

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
        self.group_pool = self.registry('res.groups')
        self.company_pool = self.registry('res.company')
        self.location_pool = self.registry('nh.clinical.location')
        self.pos_pool = self.registry('nh.clinical.pos')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.context_pool = self.registry('nh.clinical.context')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')
        self.api_pool = self.registry('nh.eobs.api')
        self.o2level_pool = self.registry('nh.clinical.o2level')
        self.o2target_pool = self.registry('nh.clinical.patient.o2target')
        self.spell_pool = self.registry('nh.clinical.spell')

        self.hospital_id = self.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        self.pos_id = self.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': self.hospital_id})
        adt_group_ids = self.group_pool.search(cr, uid, [['name', 'in', ['NH Clinical Admin Group', 'Contact Creation']]])
        nurse_group_ids = self.group_pool.search(cr, uid, [['name', 'in', ['NH Clinical Nurse Group']]])
        self.adt_id = self.user_pool.create(cr, uid, {'name': 'Test ADT', 'login': 'testadt',
                                                    'groups_id': [[4, group_id] for group_id in adt_group_ids],
                                                    'pos_id': self.pos_id})
        self.user_pool.write(cr, uid, uid, {'pos_id': self.pos_id})
        eobs_context_id = self.context_pool.search(cr, uid, [['name', '=', 'eobs']])
        self.eobs_ward_id = self.location_pool.create(cr, uid, {'name': 'Test eObs Ward', 'code': 'TESTWEOBS',
                                                              'usage': 'ward', 'parent_id': self.hospital_id,
                                                              'context_ids': [[6, 0, eobs_context_id]]})
        self.bed_ids = [self.location_pool.create(cr, uid, {'name': 'Bed %s' % i, 'code': 'TESTB%s' % i,
                                                          'usage': 'bed', 'parent_id': self.eobs_ward_id,
                                                          'context_ids': [[6, 0, eobs_context_id]]}) for i in range(10)]
        self.nurse_id = self.user_pool.create(cr, uid, {'name': 'Test Nurse', 'login': 'testnurse',
                                                      'groups_id': [[4, group_id] for group_id in nurse_group_ids],
                                                      'pos_id': self.pos_id, 'location_ids': [[6, 0, self.bed_ids]]})
        self.patient_id = self.api_pool.register(cr, self.adt_id, 'TESTHN001', {})
        self.patient = self.patient_pool.write(cr, uid, self.patient_id, {
            'dob': '1988-01-12 06:00:00'
        })

        self.api_pool.admit(cr, self.adt_id, 'TESTHN001', {'location': 'TESTWEOBS'})

        self.spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patient_id, exception='False', context=None)

        placement_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.placement'],
                                                          ['patient_id', '=', self.patient_id],
                                                          ['state', '=', 'scheduled']])
        self.activity_pool.submit(cr, uid, placement_id[0], {'location_id': self.bed_ids[0]})
        self.activity_pool.complete(cr, uid, placement_id[0])

        ews_activity_id = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.ews'],
                                                              ['patient_id', '=', self.patient_id],
                                                              ['state', '=', 'scheduled']])[0]

        data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': 0,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A'
        }

        self.api_pool.assign(cr, uid, ews_activity_id, {'user_id': self.nurse_id})
        self.api_pool.complete(cr, self.nurse_id, ews_activity_id, data)
        self.start_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)
        self.end_time = datetime.strftime(datetime.now() + timedelta(days=5), dtf)


    # def test_01_observation_report_with_spell_without_start_time_without_end_time(self):
    #     report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #     report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #         'spell_id': self.spell_id,
    #         'start_time': None,
    #         'end_time': None
    #     })
    #     self.assertEqual(report_test, True, 'Unable to print Observation Report')
    #
    # def test_02_observation_report_with_spell_with_start_time_without_end_time(self):
    #     report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #     report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #         'spell_id': self.spell_id,
    #         'start_time': self.start_time,
    #         'end_time': None
    #     })
    #     self.assertEqual(report_test, True, 'Unable to print Observation Report')
    #
    # def test_03_observation_report_with_spell_with_start_time_with_end_time(self):
    #     report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #     report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #         'spell_id': self.spell_id,
    #         'start_time': self.start_time,
    #         'end_time': self.end_time
    #     })
    #     self.assertEqual(report_test, True, 'Unable to print Observation Report')
    #
    # def test_04_observation_report_with_spell_without_start_time_with_end_time(self):
    #     report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #     report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #         'spell_id': self.spell_id,
    #         'start_time': None,
    #         'end_time': self.end_time
    #     })
    #     self.assertEqual(report_test, True, 'Unable to print Observation Report')
    #
    # def test_05_observation_report_without_spell_without_start_time_with_end_time(self):
    #     with self.assertRaises(ValueError):
    #         report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #         report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #             'spell_id': None,
    #             'start_time': None,
    #             'end_time': self.end_time
    #         })
    #
    #
    # def test_06_observation_report_without_spell_without_start_time_without_end_time(self):
    #     with self.assertRaises(ValueError):
    #         report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #         report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #             'spell_id': None,
    #             'start_time': None,
    #             'end_time': None
    #         })
    #
    # def test_07_observation_report_without_spell_with_start_time_without_end_time(self):
    #     with self.assertRaises(ValueError):
    #         report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #         report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #             'spell_id': None,
    #             'start_time': self.start_time,
    #             'end_time': None
    #         })
    #
    # def test_08_observation_report_with_spell_with_start_time_with_end_time_with_ews_only(self):
    #     report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
    #     report_test = test_reports.try_report(cr, uid, report_model, [], data={
    #         'spell_id': self.spell_id,
    #         'start_time': self.start_time,
    #         'end_time': self.end_time,
    #         'ews_only': True
    #     })
    #     self.assertEqual(report_test, True, 'Unable to print Observation Report')


    def test_09_convert_db_date_to_context_date_with_format(self):
        test_date = datetime.strptime('1988-01-12 06:00:00', '%Y-%m-%d %H:%M:%S')
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        rep = self.registry(self.report_model)
        convert_date = obs_report.convert_db_date_to_context_date(rep, cr, uid, test_date, '%Y')
        self.assertEqual(convert_date, '1988', 'Converted date is not in the right format')

    def test_10_convert_db_date_to_context_date_without_format(self):
        test_date = datetime.strptime('1988-01-12 06:00:00', '%Y-%m-%d %H:%M:%S')
        report_model, registry, cr, uid = self.report_model, self.registry, self.cr, self.uid
        rep = self.registry(self.report_model)
        convert_date = obs_report.convert_db_date_to_context_date(rep, cr, uid, test_date, None)
        self.assertEqual(str(convert_date), '1988-01-12 06:00:00+00:00', 'Converted date is not in the right format')
