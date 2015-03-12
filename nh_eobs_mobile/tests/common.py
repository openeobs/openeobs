from openerp.tests import common
import xml.etree.ElementTree as et
import helpers

class NHMobileCommonTest(common.TransactionCase):

    def setUp(self):
        super(NHMobileCommonTest, self).setUp()

        # set up pools
        self.patient = self.registry.get('nh.clinical.patient')
        self.activity = self.registry.get('nh.activity')
        self.patient_visit = self.registry.get('nh.clinical.patient.visit')
        self.tasks = self.registry.get('nh.clinical.task.base')
        self.location = self.registry.get('nh.clinical.location')
        self.location_type = self.registry.get('nh.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')
        self.api_demo = self.registry('nh.clinical.api.demo')
        self.api = self.registry('nh.eobs.api')
        self.view = self.registry("ir.ui.view")
        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }
        self.nurse = None


    def tearDown(self):
        super(NHMobileCommonTest, self).tearDown()

    def create_test_data(self, cr, uid, wards=['U'], bed_count=2, patient_admit_count=2, patient_placement_count=2,
                         ews_count=2, context='eobs', weight_count=0, blood_sugar_count=0, height_count=0,
                         o2target_count=0):
        """
        Create a default unit test environment for mobile unit tests.
            1 ward - U
            2 beds per ward - U01, U02, T01, T02
            2 patients admitted per ward
            2 patient placed in bed per ward
            2 ews observation taken per patient
        The environment is customizable, the wards parameter must be a list of ward codes. All the other parameters are
        the number of beds, patients, placements and observations we want.

        Returns an dict with the ward, users
        """
        self.api_demo.build_unit_test_env(cr, uid, wards, bed_count, patient_admit_count, patient_placement_count,
                                           ews_count, context, weight_count, blood_sugar_count, height_count,
                                           o2target_count)
        data = []
        for ward in wards:
            users = {}
            # get the ward info
            ward_id = self.location.search(cr, uid, [('code', '=', ward)])[0]
            ward_obj = self.location.read(cr, uid, ward_id, [])


            # get ward manager and nurse users and add to ward list
            wm_id = self.users.search(cr, uid, [('login', '=', 'WM{0}'.format(ward))])[0]
            ward_manager = self.users.read(cr, uid, wm_id, [])
            users['ward_manager'] = ward_manager

            n_id = self.users.search(cr, uid, [('login', '=', 'N{0}'.format(ward))])[0]
            nurse = self.users.read(cr, uid, n_id, [])
            users['nurse'] = nurse
            data.append({'ward': ward_obj, 'users': users})

        return data

    def render_template(self, cr, uid, template_name=None, options=None):
        return self.view.render(cr, uid, template_name, options, context=self.context)

    def compare_doms(self, dom_one, dom_two):
        dom_one_tree = et.tostring(et.fromstring(dom_one)).replace('\n', '').replace(' ', '')
        dom_two_tree = et.tostring(et.fromstring(dom_two)).replace('\n', '').replace(' ', '')
        return dom_one_tree == dom_two_tree

    def process_form_description(self, form_desc):
        for form_input in form_desc:
            if form_input['type'] in ['float', 'integer']:
                form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                form_input['type'] = 'number'
                form_input['number'] = True
                form_input['info'] = ''
                form_input['errors'] = ''
                form_input['min'] = str(form_input['min'])
            elif form_input['type'] == 'selection':
                form_input['selection_options'] = []
                form_input['info'] = ''
                form_input['errors'] = ''
                for option in form_input['selection']:
                    opt = dict()
                    opt['value'] = '{0}'.format(option[0])
                    opt['label'] = option[1]
                    form_input['selection_options'].append(opt)
        return form_desc

    def process_test_form(self, form_desc):
        obs_form_string = ""
        for form_field in form_desc:
            if form_field['type'] is 'number':
                if 'validation' in form_field:
                    for validation in form_field['validation']:
                        validation['condition']['operator'] = validation['condition']['operator'].replace('<', '&lt;').replace('>', '&gt;')
                obs_form_string += helpers.OBS_INPUT.format(
                    name=form_field['name'],
                    label=form_field['label'],
                    type=form_field['type'],
                    min=form_field['min'],
                    max=form_field['max'],
                    step=form_field['step'],
                    hidden_block=' valHide' if form_field['initially_hidden'] else '',
                    hidden_input=' class="exclude"' if form_field['initially_hidden'] else '',
                    data_validation=' data-validation="{0}"'.format(form_field['validation']) if 'validation' in form_field else ''
                )
            elif form_field['type'] is 'selection':
                options_string = ''
                for option in form_field['selection_options']:
                    options_string += helpers.OPTION.format(value=option['value'], name=option['label'])
                obs_form_string += helpers.OBS_SELECT.format(
                    name=form_field['name'],
                    label=form_field['label'],
                    onchange=' data-onchange="{0}"'.format(form_field['on_change']) if 'on_change' in form_field else '',
                    options=options_string,
                    hidden_block=' valHide' if form_field['initially_hidden'] else '',
                    hidden_input=' class="exclude"' if form_field['initially_hidden'] else '',
                    )

        return obs_form_string