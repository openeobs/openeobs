# -*- encoding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
{
    'name': 'NH Food and Fluid Observation',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'BJSS',
    'website': 'http://www.bjss.com/',
    'depends': [
        'nh_observations',
        'nh_eobs'
    ],
    'data': [
        'data/review_task_user.xml',
        'security/ir.model.access.csv',
        'data/recorded_concerns.xml',
        'data/dietary_needs.xml',
        'views/observation_report_template.xml',
        'views/acuity_board_buttons.xml',
        'views/static_file_include.xml',
        'data/review_task_cron.xml'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': ['static/src/xml/chart.xml'],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}
