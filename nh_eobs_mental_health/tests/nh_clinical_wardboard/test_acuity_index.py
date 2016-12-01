from openerp.addons.nh_eobs_mental_health \
    .tests.common.transaction_observation import TransactionObservationCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
import time


class TestAcuityIndex(TransactionObservationCase):
    """
    Test the acuity Index of patient with the following criteria:
    - No Risk
    - Low Risk
    - Medium Risk
    - High Risk
    - Transferred in
    - On PME / Obs Stop
    - PME finished
    - Refused
    - Refused -> Transferred in
    """

    def setUp(self):
        super(TestAcuityIndex, self).setUp()
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.spell_model = self.env['nh.clinical.spell']

    def test_no_risk(self):
        """
        Test that patient with no risk has an acuity index of 'None'
        """
        self.complete_obs(clinical_risk_sample_data.NO_RISK_DATA)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'None')

    def test_low_risk(self):
        """
        Test that patient with low risk has an acuity index of 'Low'
        """
        self.complete_obs(clinical_risk_sample_data.LOW_RISK_DATA)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'Low')

    def test_medium_risk(self):
        """
        Test that patient with medium risk has an acuity index of 'Medium'
        """
        self.complete_obs(clinical_risk_sample_data.MEDIUM_RISK_DATA)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'Medium')

    def test_high_risk(self):
        """
        Test that patient with high risk has an acuity index of 'High'
        """
        self.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'High')

    def test_transferred_in(self):
        """
        Test that patient that's just been transferred in
         has an acuity index of 'NoScore'
        """
        cr, uid = self.cr, self.uid
        self.api_pool.transfer(
            cr, self.adt_id, 'TESTHN002', {'location': 'TESTWARD'})
        self.api_pool.discharge(self.cr, self.adt_id, 'TESTHN001', {})
        placement_id = self.activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.patient_2_id],
                ['state', '=', 'scheduled']
            ]
        )
        self.activity_pool.submit(
            cr, uid, placement_id[0], {'location_id': self.bed_ids[0]}
        )
        self.activity_pool.complete(cr, uid, placement_id[0])
        wardboard = self.wardboard_model.browse(self.patient_2_id)
        self.assertEqual(wardboard.acuity_index, 'NoScore')

    def test_obs_stop(self):
        """
        Test that patient on PME/Obs Stop has an acuity index of 'ObsStop'
        """
        spell = self.spell_model.browse(self.patient_id)
        spell.write({'obs_stop': True})
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        activity_id = pme_model.create_activity(
            {},
            {'reason': 1, 'spell': spell.id}
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(activity_id)
        pme_activity.spell_activity_id = spell.activity_id
        pme_model.start(activity_id)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'ObsStop')

    # def test_obs_restart(self):
    #     """
    #     Test that patient that's just had observations restarted
    #     has an acuity index of 'NoScore'
    #     """
    #     self.complete_obs(clinical_risk_sample_data.HIGH_RISK_DATA)
    #     spell = self.spell_model.browse(self.patient_id)
    #     spell.write({'obs_stop': True})
    #     pme_model = self.env['nh.clinical.patient_monitoring_exception']
    #     activity_id = pme_model.create_activity(
    #         {},
    #         {'reason': 1, 'spell': spell.id}
    #     )
    #     activity_model = self.env['nh.activity']
    #     pme_activity = activity_model.browse(activity_id)
    #     pme_activity.spell_activity_id = spell.activity_id
    #     pme_model.start(activity_id)
    #     wardboard = self.wardboard_model.browse(self.patient_id)
    #     time.sleep(2)
    #     wardboard.end_patient_monitoring_exception()
    #     wardboard_2 = self.wardboard_model.browse(self.patient_id)
    #     self.assertEqual(wardboard_2.acuity_index, 'NoScore')

    def test_refused(self):
        """
        Test that patient that is refusing obs has an acuity index of 'Refused'
        """
        self.complete_obs(clinical_risk_sample_data.REFUSED_DATA)
        wardboard = self.wardboard_model.browse(self.patient_id)
        self.assertEqual(wardboard.acuity_index, 'Refused')
    #
    # def test_refused_transferred_in(self):
    #     """
    #     Test that patient that was refusing and then was transferred to the
    #      ward has an acuity index of 'NoScore'
    #     """
    #     cr, uid = self.cr, self.uid
    #     self.get_obs(self.patient_2_id)
    #     self.complete_obs(clinical_risk_sample_data.REFUSED_DATA)
    #     self.api_pool.transfer(
    #         cr, self.adt_id, 'TESTHN002', {'location': 'TESTWARD'})
    #     self.api_pool.discharge(self.cr, self.adt_id, 'TESTHN001', {})
    #     placement_id = self.activity_pool.search(
    #         cr, uid, [
    #             ['data_model', '=', 'nh.clinical.patient.placement'],
    #             ['patient_id', '=', self.patient_2_id],
    #             ['state', '=', 'scheduled']
    #         ]
    #     )
    #     self.activity_pool.submit(
    #         cr, uid, placement_id[0], {'location_id': self.bed_ids[0]}
    #     )
    #     self.activity_pool.complete(cr, uid, placement_id[0])
    #     wardboard = self.wardboard_model.browse(self.patient_2_id)
    #     self.assertEqual(wardboard.acuity_index, 'NoScore')
