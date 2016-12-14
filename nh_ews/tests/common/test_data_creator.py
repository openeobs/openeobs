# -*- coding: utf-8 -*-
from openerp.addons.nh_odoo_fixes.tests.utils.datetime_test_utils \
    import DatetimeTestUtils


def create_patient_and_spell(self):
    """
    Create patient and spell. Assigns various objects to instance variables.

    :param self:
    :return:
    """
    self.patient_model = self.env['nh.clinical.patient']
    self.spell_model = self.env['nh.clinical.spell']
    self.activity_model = self.env['nh.activity']
    self.activity_pool = self.registry('nh.activity')
    self.ews_model = self.env['nh.clinical.patient.observation.ews']
    # nh.eobs.api not available to this module
    self.api_model = self.env['nh.clinical.api']
    self.datetime_test_utils = DatetimeTestUtils()

    self.patient = self.patient_model.create({
        'given_name': 'Jon',
        'family_name': 'Snow',
        'patient_identifier': 'a_patient_identifier',
        'other_identifier': 'another_identifier'
    })

    self.spell_activity_id = self.spell_model.create_activity(
        {},
        {'patient_id': self.patient.id, 'pos_id': 1}
    )

    self.spell_activity = \
        self.activity_model.browse(self.spell_activity_id)

    # Fails in spell.get_patient_by_id() if not started.
    self.activity_pool.start(self.env.cr, self.env.uid,
                             self.spell_activity_id)

    self.spell = self.spell_activity.data_ref
