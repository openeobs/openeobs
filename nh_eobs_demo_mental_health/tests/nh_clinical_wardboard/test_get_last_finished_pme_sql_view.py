from openerp.tests.common import TransactionCase


class TestGetLastFinishedPMESQLView(TransactionCase):
    """
    Test that the get_last_pme SQL view is working correctly
    """

    def get_pmes_for_state(self, state):
        """
        Get Patient Monitoring Exceptions activities in a state

        :param state: State of activity (completed, cancelled, started)
        :return: recordset of nh.activity
        """
        activity_model = self.env['nh.activity']
        return activity_model.search([
            ['data_model', '=', 'nh.clinical.patient_monitoring_exception'],
            ['state', '=', state]
        ])

    def get_last_finished_pmes(self, spell):
        """
        Use the last_finished_pme SQL view to get the last PME in a state
        of completed or cancelled for each spell
        :param spell: instance of nh.clinical.spell from recordset
        :return: dictionary of values from cursor
        """
        self.cr.execute("""
            SELECT * from last_finished_pme WHERE spell_id = {spell_id}
            """.format(spell_id=spell.id))
        return self.cr.dictfetchall()

    def setUp(self):
        super(TestGetLastFinishedPMESQLView, self).setUp()
        # Need to get the spell with a completed pme
        self.completed_pmes = self.get_pmes_for_state('completed')
        # Need to get a spell with a cancelled pme
        self.cancelled_pmes = self.get_pmes_for_state('cancelled')
        # Need to get a spell with a started pme
        self.started_pmes = self.get_pmes_for_state('started')
        self.assertTrue(len(self.completed_pmes) > 0)
        self.assertTrue(len(self.cancelled_pmes) > 0)
        self.assertTrue(len(self.started_pmes) > 0)

    def test_get_last_finished_pme_gets_completed_pme(self):
        """
        Test that the SQL view returns the last completed PME activity
        """
        for pme in self.completed_pmes:
            last_finished_pme = self.get_last_finished_pmes(
                pme.spell_activity_id.data_ref)
            self.assertEqual(last_finished_pme[0].get('id'), pme.id)

    def test_get_last_finished_pme_gets_cancelled_pme(self):
        """
        Test that the SQL view returns the last cancelled PME activity
        """
        for pme in self.cancelled_pmes:
            last_finished_pme = self.get_last_finished_pmes(
                pme.spell_activity_id.data_ref)
            self.assertEqual(last_finished_pme[0].get('id'), pme.id)

    def test_gets_only_finished_pme(self):
        """
        Test that the SQL only gets PMEs that have been completed
        """
        for pme in self.started_pmes:
            last_finished_pme = self.get_last_finished_pmes(
                pme.spell_activity_id.data_ref)
            self.assertFalse(last_finished_pme)

    def test_gets_latest_finished_pme_for_spell(self):
        """
        Test that the SQL view is getting the latest finished PME for the spell
        when there are two PMEs completed
        """
        pme = self.completed_pmes[0]
        # create a new PME for spell
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        new_pme = pme_model.create_activity(
            {},
            {
                'reason': 1,
                'spell': pme.spell_activity_id.data_ref.id
            }
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(new_pme)
        pme_activity.spell_activity_id = pme.spell_activity_id.id
        pme_model.start(new_pme)
        # complete PME for spell
        pme_model.complete(new_pme)
        # get last finished pme
        last_finished_pme = self.get_last_finished_pmes(
            pme.spell_activity_id.data_ref)
        # make sure it returns the new one
        self.assertEqual(last_finished_pme[0].get('id'), new_pme)
        # make sure it doesn't return the old one
        self.assertNotEqual(last_finished_pme[0].get('id'), pme.id)
