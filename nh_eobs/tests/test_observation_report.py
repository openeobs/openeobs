# Part of Open eObs. See LICENSE file for full copyright and licensing details.
__author__ = 'colinwren'
from . import observation_report_helpers as helpers
from openerp.tools import test_reports
from datetime import datetime
import logging
from openerp.addons.nh_eobs.report.helpers \
    import convert_db_date_to_context_date
import copy

_logger = logging.getLogger(__name__)


class TestObservationReport(helpers.ObservationReportHelpers):

    def test_01_report_with_spell_wout_start_time_wout_end_time(self):
        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': None
        })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')

    def test_02_report_with_spell_with_start_time_without_end_time(self):
        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': None
        })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')

    def test_03_report_with_spell_with_start_time_with_end_time(self):
        old_triggered_ews_data = copy.deepcopy(self.triggered_ews_data)
        self.triggered_ews_data = {
            'data_model': 'nh.clinical.patient.observation.ews',
        }
        old_move_data = copy.deepcopy(self.move_data)
        self.move_data = False
        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time
        })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')
        self.triggered_ews_data = old_triggered_ews_data
        self.move_data = old_move_data

    def test_04_report_with_spell_without_start_time_with_end_time(self):
        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': None,
            'end_time': self.end_time
        })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')

    def test_05_report_without_spell_without_start_time_with_end_time(self):
        with self.assertRaises(ValueError):
            report_model, cr, uid = self.report_model, self.cr, self.uid
            test_reports.try_report(
                cr, uid, report_model, [],
                data={
                    'spell_id': None,
                    'start_time': None,
                    'end_time': self.end_time
                }
            )

    def test_06_report_without_spell_without_start_time_without_end_time(self):
        with self.assertRaises(ValueError):
            report_model, cr, uid = self.report_model, self.cr, self.uid
            test_reports.try_report(
                cr, uid,
                report_model, [],
                data={
                    'spell_id': None,
                    'start_time': None,
                    'end_time': None
                }
            )

    def test_07_report_without_spell_with_start_time_without_end_time(self):
        with self.assertRaises(ValueError):
            report_model, cr, uid = self.report_model, self.cr, self.uid
            test_reports.try_report(cr, uid, report_model, [], data={
                'spell_id': None,
                'start_time': self.start_time,
                'end_time': None
            })

    def test_08_report_with_spell_w_start_time_w_end_time_with_ews_only(self):
        report_model, cr, uid = self.report_model, self.cr, self.uid
        report_test = test_reports.try_report(cr, uid, report_model, [], data={
            'spell_id': self.spell_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'ews_only': True
        })
        self.assertEqual(report_test, True,
                         'Unable to print Observation Report')

    def test_09_observation_report_without_data(self):
        report_model, cr, uid = self.report_model, self.cr, self.uid
        with self.assertRaises(ValueError):
            test_reports.try_report(cr, uid, report_model, [])

    def test_10_convert_db_date_to_context_date_with_format(self):
        test_date = datetime.strptime(
            '1988-01-12 06:00:00',
            '%Y-%m-%d %H:%M:%S'
        )
        cr, uid = self.cr, self.uid
        convert_date = convert_db_date_to_context_date(
            cr, uid, test_date, '%Y')
        self.assertEqual(
            convert_date,
            '1988',
            'Converted date is not in the right format'
        )

    def test_11_convert_db_date_to_context_date_without_format(self):
        test_date = datetime.strptime(
            '1988-01-12 06:00:00',
            '%Y-%m-%d %H:%M:%S'
        )
        cr, uid = self.cr, self.uid
        # Need to supply the timezone so can ensure will use UTC
        # instead of Odoo default
        convert_date = convert_db_date_to_context_date(
            cr, uid, test_date, None, {'tz': 'UTC'})
        self.assertEqual(
            str(convert_date),
            '1988-01-12 06:00:00+00:00',
            'Converted date is not in the right format'
        )
