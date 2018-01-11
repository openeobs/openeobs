# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
{
    'name': 'NH eObs',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """
        Adds a slew of features to create a usable observation application:
          - Observations can be scheduled and assigned to users to complete.
          - Patients can refuse observations.
          - Multiple views added.
    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_clinical',
                'nh_ews',
                'nh_gcs',
                'nh_pbp',
                'nh_stools',
                'nh_graphs'],
    'data': [
        'data/master_data.xml',
        'data/nh_clinical_patient_monitoring_exception_reasons.xml',
        'data/nh_cancel_reasons.xml',
        'observation_report_declaration.xml',
        'wizard/cancel_notifications_view.xml',
        'wizard/print_observation_report_view.xml',
        'views/wardboard_view.xml',
        'views/workload_view.xml',
        'views/placement_view.xml',
        'views/overdue_view.xml',
        'views/views.xml',
        'views/ward_dashboard_view.xml',
        'views/locations_view.xml',
        'views/menuitem.xml',
        'views/observation_report_template.xml',
        'security/ir.model.access.csv',
        'views/settings.xml'
    ],
    'qweb': [
        'static/src/xml/nh_eobs.xml',
        'static/src/xml/about_liveobs.xml'
    ],
    'application': True,
    'installable': True,
    'active': False,
}
