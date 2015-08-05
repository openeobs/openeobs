__author__ = 'lorenzo'
import logging
import mock
from lxml import etree
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestTaskDetailHTML(MobileHTMLRenderingCase):
    """
    Test case collecting all the tests relating to the RENDERING of the 'task detail' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """

    def test_task_detail_page_with_no_form_fields_data(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute

        but WITHOUT:
            - data about the fields of the form
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_detail_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = {
            'task_id': 1337,
            'task_type': 'test',
            'patient_id': 1,
            'patient_name': 'Wren, Colin',
            'ajax_action': 'calculate_obs_score',
            'startTimestamp': 0,
            'fields': []
        }
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_task(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_task_detail_page_with_data(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute
            - data about a field for each type of input that a form can have
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_detail_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = {
            'task_id': 1337,
            'task_type': 'test',
            'patient_id': 1,
            'patient_name': 'Wren, Colin',
            'ajax_action': 'calculate_obs_score',
            'startTimestamp': 0,
            'fields': [
                {
                    'name': 'int',
                    'type': 'integer',
                    'label': 'Integer',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False
                },
                {
                    'name': 'int_validation',
                    'type': 'integer',
                    'label': 'Integer Validation',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'int_validation',
                                'operator': '<',
                                'value': 'int'
                            },
                            'message': {
                                'target': 'Validation field must be more than normal field',
                                'value': 'Normal field must be less than validation field'
                            }
                        },
                    ]
                },
                {
                    'name': 'int_onchange',
                    'type': 'integer',
                    'label': 'Integer On Change',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['int'],
                            'condition': [
                                [
                                    'int_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['int'],
                            'condition': [
                                [
                                    'int_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'int_exclude',
                    'type': 'integer',
                    'label': 'Integer Hidden',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': True
                },
                {
                    'name': 'int_reference',
                    'type': 'integer',
                    'label': 'Integer Reference',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'int_target',
                    'type': 'integer',
                    'label': 'Integer Target',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'target': 'Target Text'
                },

                {
                    'name': 'float',
                    'type': 'float',
                    'label': 'Float',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False
                },
                {
                    'name': 'float_validation',
                    'type': 'float',
                    'label': 'Float Validation',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'float_validation',
                                'operator': '<',
                                'value': 'float'
                            },
                            'message': {
                                'target': 'Validation field must be more than normal field',
                                'value': 'Normal field must be less than validation field'
                            }
                        },
                    ]
                },
                {
                    'name': 'float_onchange',
                    'type': 'float',
                    'label': 'Float On Change',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['float'],
                            'condition': [
                                [
                                    'float_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['float'],
                            'condition': [
                                [
                                    'float_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'float_exclude',
                    'type': 'float',
                    'label': 'Float Hidden',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': True
                },
                {
                    'name': 'float_reference',
                    'type': 'float',
                    'label': 'Float Reference',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'float_target',
                    'type': 'float',
                    'label': 'Float Target',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'target': 'Target Text'
                },
                {
                    'name': 'text',
                    'type': 'text',
                    'label': 'Text',
                    'initially_hidden': False
                },
                {
                    'name': 'text_validation',
                    'type': 'text',
                    'label': 'Text Validation',
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'text_validation',
                                'operator': '!==',
                                'value': ''
                            },
                            'message': {
                                'target': 'Validation field must contain a value',
                                'value': ''
                            }
                        },
                    ]
                },
                {
                    'name': 'text_onchange',
                    'type': 'text',
                    'label': 'Text On Change',
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['text'],
                            'condition': [
                                [
                                    'text_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['text'],
                            'condition': [
                                [
                                    'text_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'text_exclude',
                    'type': 'text',
                    'label': 'Text Hidden',
                    'initially_hidden': True
                },
                {
                    'name': 'text_reference',
                    'type': 'text',
                    'label': 'Text Reference',
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'text_target',
                    'type': 'text',
                    'label': 'Text Target',
                    'initially_hidden': False,
                    'target': 'Target Text'
                },
                {
                    'name': 'select',
                    'type': 'select',
                    'label': 'Select',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False
                },
                {
                    'name': 'select_exclude',
                    'type': 'select',
                    'label': 'Select Hidden',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': True
                },
                {
                    'name': 'select_onchange',
                    'type': 'select',
                    'label': 'Select On Change',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['select'],
                            'condition': [
                                [
                                    'select_onchange',
                                    '!=',
                                    'an'
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['select'],
                            'condition': [
                                [
                                    'select_onchange',
                                    '==',
                                    'an'
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'select_reference',
                    'type': 'select',
                    'label': 'Select Reference',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
            ]
        }
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_task(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_task_detail_page_with_data_and_notification(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute
            - data about a field for each type of input that a form can have
            - a notification counter
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_detail_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_tasks_data = {
            'task_id': 1337,
            'task_type': 'test',
            'patient_id': 1,
            'patient_name': 'Wren, Colin',
            'ajax_action': 'calculate_obs_score',
            'startTimestamp': 0,
            'fields': [
                {
                    'name': 'int',
                    'type': 'integer',
                    'label': 'Integer',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False
                },
                {
                    'name': 'int_validation',
                    'type': 'integer',
                    'label': 'Integer Validation',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'int_validation',
                                'operator': '<',
                                'value': 'int'
                            },
                            'message': {
                                'target': 'Validation field must be more than normal field',
                                'value': 'Normal field must be less than validation field'
                            }
                        },
                    ]
                },
                {
                    'name': 'int_onchange',
                    'type': 'integer',
                    'label': 'Integer On Change',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['int'],
                            'condition': [
                                [
                                    'int_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['int'],
                            'condition': [
                                [
                                    'int_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'int_exclude',
                    'type': 'integer',
                    'label': 'Integer Hidden',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': True
                },
                {
                    'name': 'int_reference',
                    'type': 'integer',
                    'label': 'Integer Reference',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'int_target',
                    'type': 'integer',
                    'label': 'Integer Target',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False,
                    'target': 'Target Text'
                },

                {
                    'name': 'float',
                    'type': 'float',
                    'label': 'Float',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False
                },
                {
                    'name': 'float_validation',
                    'type': 'float',
                    'label': 'Float Validation',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'float_validation',
                                'operator': '<',
                                'value': 'float'
                            },
                            'message': {
                                'target': 'Validation field must be more than normal field',
                                'value': 'Normal field must be less than validation field'
                            }
                        },
                    ]
                },
                {
                    'name': 'float_onchange',
                    'type': 'float',
                    'label': 'Float On Change',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['float'],
                            'condition': [
                                [
                                    'float_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['float'],
                            'condition': [
                                [
                                    'float_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'float_exclude',
                    'type': 'float',
                    'label': 'Float Hidden',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': True
                },
                {
                    'name': 'float_reference',
                    'type': 'float',
                    'label': 'Float Reference',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'float_target',
                    'type': 'float',
                    'label': 'Float Target',
                    'min': 1,
                    'max': 35.9,
                    'initially_hidden': False,
                    'target': 'Target Text'
                },
                {
                    'name': 'text',
                    'type': 'text',
                    'label': 'Text',
                    'initially_hidden': False
                },
                {
                    'name': 'text_validation',
                    'type': 'text',
                    'label': 'Text Validation',
                    'initially_hidden': False,
                    'validation': [
                        {
                            'condition': {
                                'target': 'text_validation',
                                'operator': '!==',
                                'value': ''
                            },
                            'message': {
                                'target': 'Validation field must contain a value',
                                'value': ''
                            }
                        },
                    ]
                },
                {
                    'name': 'text_onchange',
                    'type': 'text',
                    'label': 'Text On Change',
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['text'],
                            'condition': [
                                [
                                    'text_onchange',
                                    '!=',
                                    ''
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['text'],
                            'condition': [
                                [
                                    'text_onchange',
                                    '==',
                                    ''
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'text_exclude',
                    'type': 'text',
                    'label': 'Text Hidden',
                    'initially_hidden': True
                },
                {
                    'name': 'text_reference',
                    'type': 'text',
                    'label': 'Text Reference',
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
                {
                    'name': 'text_target',
                    'type': 'text',
                    'label': 'Text Target',
                    'initially_hidden': False,
                    'target': 'Target Text'
                },
                {
                    'name': 'select',
                    'type': 'select',
                    'label': 'Select',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False
                },
                {
                    'name': 'select_exclude',
                    'type': 'select',
                    'label': 'Select Hidden',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': True
                },
                {
                    'name': 'select_onchange',
                    'type': 'select',
                    'label': 'Select On Change',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False,
                    'on_change': [
                        {
                            'action': 'disable',
                            'fields': ['select'],
                            'condition': [
                                [
                                    'select_onchange',
                                    '!=',
                                    'an'
                                ]
                            ]
                        },
                        {
                            'action': 'enable',
                            'fields': ['select'],
                            'condition': [
                                [
                                    'select_onchange',
                                    '==',
                                    'an'
                                ]
                            ]
                        }
                    ]
                },
                {
                    'name': 'select_reference',
                    'type': 'select',
                    'label': 'Select Reference',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False,
                    'reference': {
                        'type': 'image',
                        'url': '/mobile/src/reference.jpg',
                        'title': 'Reference Image',
                        'label': 'Reference'
                    }
                },
            ]
        }
        api_notification_counter_data = 666

        api_tasks = mock.Mock(return_value=api_tasks_data)
        api_notifications = mock.Mock(return_value=api_notification_counter_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_task(mobile_frontend, api_tasks(), api_notifications())
        self.assertEqual(rendered_template, expected_output)