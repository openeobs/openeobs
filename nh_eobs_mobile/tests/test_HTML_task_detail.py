# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from lxml import etree
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering \
    import MobileHTMLRenderingCase
import logging

_logger = logging.getLogger(__name__)


class TestTaskDetailHTML(MobileHTMLRenderingCase):
    """Test case collecting all the tests relating to the
    RENDERING of the 'task detail' page.
    Compare the actual rendered HTML pages against fixtures
    (i.e. 'fake' HTML files) specially built.
    """
    template_id = 'nh_eobs_mobile.data_input_screen'

    def setUp(self):
        super(TestTaskDetailHTML, self).setUp()
        self.patient_fixture = {
            'url': '/mobile/patient/1',
            'name': 'Wren, Colin'
        }
        self.form_fixture = {
            'action': '/mobile/task/submit/1337',
            'task-id': 1337,
            'type': 'test',
            'patient-id': 1,
            'source': 'task',
            'obs_needs_score': True,
            'task_valid': True,
            'start': '0',
            'view_description': [
                {
                    'type': 'form',
                    'inputs': []
                }
            ]
        }
        self.form_inputs_fixture = [
            {
                'name': 'int',
                'type': 'number',
                'label': 'Integer',
                'min': 1,
                'max': 59,
                'step': 1,
                'initially_hidden': False
            },
            {
                'name': 'int_validation',
                'type': 'number',
                'label': 'Integer Validation',
                'min': 1,
                'max': 59,
                'step': 1,
                'initially_hidden': False,
                'validation': [
                    {
                        'condition': {
                            'target': 'int_validation',
                            'operator': '<',
                            'value': 'int'
                        },
                        'message': {
                            'target': 'Validation field must be '
                                      'more than normal field',
                            'value': 'Normal field must be less '
                                     'than validation field'
                        }
                    },
                ]
            },
            {
                'name': 'int_onchange',
                'type': 'number',
                'label': 'Integer On Change',
                'min': 1,
                'max': 59,
                'step': 1,
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
                'type': 'number',
                'label': 'Integer Hidden',
                'min': 1,
                'max': 59,
                'step': 1,
                'initially_hidden': True
            },
            {
                'name': 'int_reference',
                'type': 'number',
                'label': 'Integer Reference',
                'min': 1,
                'max': 59,
                'step': 1,
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
                'type': 'number',
                'label': 'Integer Target',
                'min': 1,
                'max': 59,
                'step': 1,
                'initially_hidden': False,
                'secondary_label': 'Target Text'
            },

            {
                'name': 'float',
                'type': 'number',
                'label': 'Float',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
                'initially_hidden': False
            },
            {
                'name': 'float_validation',
                'type': 'number',
                'label': 'Float Validation',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
                'initially_hidden': False,
                'validation': [
                    {
                        'condition': {
                            'target': 'float_validation',
                            'operator': '<',
                            'value': 'float'
                        },
                        'message': {
                            'target': 'Validation field must be '
                                      'more than normal field',
                            'value': 'Normal field must be less '
                                     'than validation field'
                        }
                    },
                ]
            },
            {
                'name': 'float_onchange',
                'type': 'number',
                'label': 'Float On Change',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
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
                'type': 'number',
                'label': 'Float Hidden',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
                'initially_hidden': True
            },
            {
                'name': 'float_reference',
                'type': 'number',
                'label': 'Float Reference',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
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
                'type': 'number',
                'label': 'Float Target',
                'min': 1,
                'max': 35.9,
                'step': 0.1,
                'initially_hidden': False,
                'secondary_label': 'Target Text'
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
                'secondary_label': 'Target Text'
            },
            {
                'name': 'select',
                'type': 'selection',
                'label': 'Select',
                'selection_type': 'text',
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ],
                'initially_hidden': False
            },
            {
                'name': 'select_exclude',
                'type': 'selection',
                'label': 'Select Hidden',
                'selection_type': 'text',
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ],
                'initially_hidden': True
            },
            {
                'name': 'select_onchange',
                'type': 'selection',
                'label': 'Select On Change',
                'selection_type': 'text',
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ],
                'initially_hidden': False,
                'on_change': [
                    {
                        'action': 'show',
                        'fields': ['select'],
                        'condition': [
                            [
                                'select_onchange',
                                '==',
                                'an'
                            ]
                        ]
                    },
                    {
                        'action': 'hide',
                        'fields': ['select'],
                        'condition': [
                            [
                                'select_onchange',
                                '!=',
                                'an'
                            ]
                        ]
                    }
                ]
            },
            {
                'name': 'select_reference',
                'type': 'selection',
                'label': 'Select Reference',
                'selection_type': 'text',
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ],
                'initially_hidden': False,
                'reference': {
                    'type': 'image',
                    'url': '/mobile/src/reference.jpg',
                    'title': 'Reference Image',
                    'label': 'Reference'
                }
            }
        ]

    def test_task_detail_page_with_no_form_fields_data(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute

        but WITHOUT:
            - data about the fields of the form
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        # controller's method's result against
        fixture_name = 'task_detail_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". Hence, '
                'this test has not been actually executed'.format(
                    fixture_name
                )
            )

        # Set up specific data to provide the template the data it
        # needs for the rendering
        api_data = {
            'patient': self.patient_fixture,
            'form': self.form_fixture,
            'notification_count': 0,
            'section': 'task',
            'task_valid': True,
            'username': 'norah',
            'urls': self.controller_urls,
            'view_description': [
                {
                    'type': 'form',
                    'inputs': []
                }
            ]
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and
        # convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for
        # the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )

    def test_task_detail_page_with_data(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute
            - data about a field for each type of input that a form can have
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        # controller's method's result against
        fixture_name = 'task_detail_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". '
                'Hence, this test has not been actually executed'.format(
                    fixture_name
                )
            )

        # Small fix for the form's inputs data
        form_inputs = self.form_inputs_fixture[:]
        for i in form_inputs:
            if 'errors' not in i:
                i['errors'] = False
            if 'info' not in i:
                i['info'] = False

        # Set up specific data to provide the template the data
        # it needs for the rendering
        api_data = {
            'patient': self.patient_fixture,
            'form': self.form_fixture,
            'notification_count': 0,
            'section': 'task',
            'username': 'norah',
            'task_valid': True,
            'urls': self.controller_urls,
            'view_description': [
                {
                    'type': 'form',
                    'inputs': form_inputs
                }
            ]
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and convert
        # it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix
        # for the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )

    def test_task_detail_page_with_no_form_fields_data_with_notification(self):
        """
        Test the 'task detail' page with:
            - data about the patient
            - data about the action to execute
            - a notification counter

        but WITHOUT:
            - data about the fields of the form
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        #  controller's method's result against
        fixture_name = 'task_detail_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". '
                'Hence, this test has not been actually executed'.format(
                    fixture_name
                )
            )

        # Set up specific data to provide the template the data
        #  it needs for the rendering
        api_data = {
            'patient': self.patient_fixture,
            'form': self.form_fixture,
            'notification_count': 666,
            'section': 'task',
            'task_valid': True,
            'username': 'norah',
            'urls': self.controller_urls,
            'view_description': [
                {
                    'type': 'form',
                    'inputs': []
                }
            ]
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and
        # convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small
        # fix for the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )
