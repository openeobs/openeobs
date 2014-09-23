# -*- encoding: utf-8 -*-
{
    'name': 'T4 Clinical Default Configuration',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Tactix4',
    'website': 'http://www.tactix4.com/',
    'depends': ['t4clinical_ui', 'mobile_frontend'],
    
    
    'data': ['trust.xml',
             'greenford_pos.xml', 'greenford_locations.xml', 'greenford_users.xml','greenford_devices.xml','greenford_params.xml'],
             
             
    'qweb': ['static/src/xml/t4clinical_default_config.xml'],
    'css': ['static/src/css/t4clinical_default_config.css'],
    
    
    'application': True,
    'installable': True,
    'active': False,
}