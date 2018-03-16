# -*- coding: utf-8 -*-
{
    'name': 'Shift Allocation',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'Allocate users to beds during shift management.',
    'description': """Extends shift creation to include allocation of users to 
    beds which represents their areas of responsibility.""",
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['shift_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/responsibility_allocation_wizard.xml',
        'wizard/user_allocation_view.xml',
        'views/menuitem.xml',
        'views/static_resources.xml'
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
