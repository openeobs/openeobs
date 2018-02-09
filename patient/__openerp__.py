# -*- coding: utf-8 -*-
{
    'name': 'Patient',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'This is the summary.',
    'description': """
        This is the description.
    """,
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': [
        'nh_eobs'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/patients_at_a_glance.xml',
        'views/patient_in_detail.xml'
    ],
    'application': True,
    'installable': True,
    'active': False
}
