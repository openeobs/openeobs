# -*- coding: utf-8 -*-
{
    'name': 'Shift Management',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Create shifts with times and the employees who are on them.',
    'description': """Creating shifts allows the system to know which users
    are working and when. This information enables other useful features.""",
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': ['liveobs_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/menuitem.xml'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}
