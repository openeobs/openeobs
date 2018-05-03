from BeautifulSoup import BeautifulSoup

from openerp.tests.common import SingleTransactionCase


class TestObservationEntryTemplate(SingleTransactionCase):

    def setUp(self):
        super(TestObservationEntryTemplate, self).setUp()

        template_id = 'nh_eobs_mobile.observation_entry'
        self.expected_field_name = 'location'
        self.expected_field_size = 20
        values = {
            'form': {
                'task-id': False, 'patient-id': 1, 'start': '1525360396',
                'source': 'patient',
                'action': '/mobile/patient/submit/therapeutic/1',
                'type': u'therapeutic'
            },
            'inputs': [
                {
                    'info': '',
                    'errors': '',
                    'necessary': 'false',
                    'name': self.expected_field_name,
                    'initially_hidden': False,
                    'required': 'false',
                    'label': 'Location',
                    'type': 'text',
                    'size': self.expected_field_size
                }
            ]
        }

        self.observation_entry_html = self.registry('ir.ui.view').render(
            self.env.cr, self.env.uid, template_id, values,
            context=self.env.context
        )

    def test_text_field_type_maps_to_textarea_element(self):
        soup = BeautifulSoup(self.observation_entry_html, isHTML=True)
        textareas = soup.findAll(
            'textarea', attrs={'name': self.expected_field_name}
        )

        self.assertEqual(1, len(textareas))

    def test_text_field_size_maps_to_textarea_size_attribute(self):
        soup = BeautifulSoup(self.observation_entry_html, isHTML=True)
        textarea = soup.find(
            'textarea', attrs={'name': self.expected_field_name}
        )

        self.assertEqual(self.expected_field_size, textarea.maxlength)
