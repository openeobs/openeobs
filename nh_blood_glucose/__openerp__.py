# -*- coding: utf-8 -*-
{
    'name': 'Blood Glucose Observations',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': "Allows users to record blood glucose observations.",
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': [
        'nh_eobs'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/wardboard_view.xml',
        'views/static_file_include.xml',
        'views/observation_report_template.xml'
    ],
    'qweb': ['static/src/xml/desktop_chart.xml'],
    'application': True,
    'installable': True,
    'active': False,
}
