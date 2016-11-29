# -*- coding: utf-8 -*-
def create_patient_and_spell_and_complete_clinical_review(self):
    self.activity_model = self.env['nh.activity']
    self.patient_model = self.env['nh.clinical.patient']
    self.spell_model = self.env['nh.clinical.spell']
    self.clinical_review_model = \
        self.env['nh.clinical.notification.clinical_review']
    self.clinical_review_frequency_model = \
        self.env['nh.clinical.notification.clinical_review_frequency']
    self.user_model = self.env['res.users']
    self.category_model = self.env['res.partner.category']

    self.nurse_role = self.category_model.search([('name', '=', 'Nurse')])[0]

    self.nurse = self.user_model.create({
        'name': 'Jon',
        'login': 'iknownothing',
        'password': 'atall',
        'category_id': [[4, self.nurse_role.id]],
    })

    self.patient = self.patient_model.create({
        'given_name': 'Jon',
        'family_name': 'Snow',
        'patient_identifier': 'he_knows_nothing'
    })

    self.spell_activity_id = self.spell_model.create_activity(
        {},
        {
            'patient_id': self.patient.id,
            'pos_id': 1
        }
    )
    self.activity_model.start(self.spell_activity_id)

    self.clinical_review_notification_activity_id = \
        self.clinical_review_model.sudo(self.nurse).create_activity(
            {
                'parent_id': self.spell_activity_id,
                'patient_id': self.patient.id
            },
            {
                'patient_id': self.patient.id,
            }
        )
    self.clinical_review_notification_activity = \
        self.activity_model.sudo(self.nurse).browse(
            self.clinical_review_notification_activity_id
        )
    self.activity_model.sudo(self.nurse).complete(
        self.clinical_review_notification_activity_id
    )
