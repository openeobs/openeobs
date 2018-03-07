# -*- coding: utf-8 -*-
{
    'name': 'User Management',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'The summary.',
    'description': """The description.""",
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_clinical', 'shift_allocation'],
    'data': [
        'security/ir.model.access.csv',
        'data/change_ward_manager_to_shift_coordinator.xml',
        'views/user_management_view.xml',
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
