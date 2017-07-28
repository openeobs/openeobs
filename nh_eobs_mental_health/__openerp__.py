# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
{
    'name': 'NH eObs Mental Health Defaults',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """     """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': [
        'nh_eobs',
        'nh_eobs_mobile',
        # TODO EOBS-1089: nh_eobs_mental_health_depends on nh_weight.
        'nh_weight',
        # 'nh_food_and_fluid',
        'nh_blood_glucose'
    ],
    'data': [
        'data/master_data.xml',
        'views/wardboard_view.xml',
        'views/ward_dashboard_view.xml',
        'views/static_include.xml',
        'views/mobile_override.xml',
        'views/observation_report_template.xml',
        'views/bed_availability.xml',
        'security/ir.model.access.csv'
    ],
    'qweb': ['static/src/xml/widgets.xml'],
    'application': True,
    'installable': True,
    'active': False,
}
