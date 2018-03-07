# -*- coding: utf-8 -*-
{
    'name': 'LiveObs Core',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': 'The core module that all other LiveObs modules depend on.',
    'description': """
    LiveObs Core serves 2 purposes:
      - Creates the root LiveObs menu which other modules can add entries too \
      in order to provide access to their own views and functionality.
      - Acts as a bundle for all the lower-level modules from the nhclinical \
      and odoo projects that LiveObs modules depend on.
    """,
    'author': 'BJSS',
    'website': 'http://www.liveobs.com/',
    'depends': ['nh_clinical'],
    'data': [
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