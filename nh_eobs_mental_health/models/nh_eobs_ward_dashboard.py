# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""
Gives an overview of the current state of ward and bed
:class:`locations<base.nh_clinical_location>`.
"""
from openerp import api
from openerp.osv import orm, fields


class NHClinicalWardDashboard(orm.Model):
    """
    Extends :class:`location<base.nh_clinical_location>`, providing
    an overall state of a ward location.

    It shows number of related :class:`users<base.res_users>` by type,
    number of free beds, number of
    :class:`patients<base.nh_clinical_patient>` by risk, number of
    waiting patients, etc.
    """

    _inherit = 'nh.eobs.ward.dashboard'
    _name = 'nh.eobs.ward.dashboard'

    _columns = {
        'awol_count': fields.integer('Patient Monitoring Exception - AWOL'),
        'acute_hospital_ed_count': fields.integer(
            'Patient Monitoring Exception - Acute hospital ED'),
        'extended_leave_count': fields.integer(
            'Patient Monitoring Exception - Extended leave'),
        'capacity_count': fields.integer('Free Beds'),
        'workload_count': fields.integer('All patients associated with ward'),
        'on_ward_count': fields.integer(
            'All patients in bed and not on Patient Monitoring Exception'),
        'refused_obs_count': fields.integer(
            'All patients currently refusing observations')
    }

    @api.multi
    def patient_board(self):
        """
        Return the view dict for showing the Acuity Board for the selecte
        ward
        """
        view_dict = super(NHClinicalWardDashboard, self).patient_board()
        view_dict['context']['search_default_acuity_index'] = 1
        del view_dict['context']['search_default_clinical_risk']
        return view_dict

    def init(self, cr):
        """
        Init the module - set up SQL views to help with pulling together ward
        dashboard
        :param cr: Odoo cursor
        """
        super(NHClinicalWardDashboard, self).init(cr)
        sql_statements = self.pool['nh.clinical.sql']
        awol = sql_statements.get_ward_dashboard_reason_count(cr, 'AWOL')
        extended_leave = sql_statements.get_ward_dashboard_reason_count(
            cr, 'Extended leave')
        acute_ed = sql_statements.get_ward_dashboard_reason_count(
            cr, 'Acute hospital ED')
        cr.execute(
            """
            -- Create Helper Views
            CREATE OR REPLACE VIEW wdb_transfer_ranked AS ({transfer_ranked});
            CREATE OR REPLACE VIEW wdb_reasons AS ({reasons_view});
            CREATE OR REPLACE VIEW wdb_awol_count AS ({awol_count});
            CREATE OR REPLACE VIEW wdb_extended_leave_count
            AS ({extended_leave_count});
            CREATE OR REPLACE VIEW wdb_acute_hospital_ed_count
            AS ({acute_ed_count});
            CREATE OR REPLACE VIEW wdb_workload_count AS ({pt_on_ward});
            CREATE OR REPLACE VIEW wdb_bed_count AS ({bed_count});
            CREATE OR REPLACE VIEW wdb_capacity_count AS ({capacity});
            CREATE OR REPLACE VIEW wdb_obs_stop_count AS ({obs_stop});
            CREATE OR REPLACE VIEW wdb_on_ward_count AS ({on_ward});
            CREATE OR REPLACE VIEW wdb_refused_obs_count
            AS ({ref_obs});

            -- Create Ward Dashboard
            CREATE OR REPLACE VIEW nh_eobs_ward_dashboard AS ({dashboard});
            """
            .format(
                reasons_view=sql_statements.get_ward_dashboard_reason_view(),
                awol_count=awol,
                extended_leave_count=extended_leave,
                acute_ed_count=acute_ed,
                pt_on_ward=sql_statements.get_ward_dashboard_workload(),
                bed_count=sql_statements.get_ward_dashboard_bed_count(),
                capacity=sql_statements.get_ward_dashboard_capacity_count(),
                obs_stop=sql_statements.get_ward_dashboard_obs_stop_count(),
                on_ward=sql_statements.get_ward_dashboard_on_ward_count(),
                ref_obs=sql_statements.get_ward_dashboard_refused_obs_count(),
                dashboard=sql_statements.get_ward_dashboard(),
                transfer_ranked=sql_statements.get_wb_transfer_ranked_sql()
            )
        )
