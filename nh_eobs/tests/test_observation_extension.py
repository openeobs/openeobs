from openerp.tests.common import TransactionCase
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestClinicalPatientObservationEwsRefresh(TransactionCase):

    def setUp(self):
        super(TestClinicalPatientObservationEwsRefresh, self).setUp()
        cr, uid = self.cr, self.uid

        self.users_pool = self.registry('res.users')
        self.activity_pool = self.registry('nh.activity')
        self.location_pool = self.registry('nh.clinical.location')
        self.pos_pool = self.registry('nh.clinical.pos')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.apidemo = self.registry('nh.clinical.api.demo')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')
        self.activity_pool = self.registry('nh.activity')
        self.context_pool = self.registry('nh.clinical.context')
        self.placement_pool = self.registry('nh.clinical.patient.placement')
        self.mrsa_pool = self.registry('nh.clinical.patient.mrsa')
        self.diabetes_pool = self.registry('nh.clinical.patient.diabetes')
        self.patient_ids = self.apidemo.build_unit_test_env1(cr, uid, bed_count=4, patient_count=4)
        self.wu_id = self.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        self.pos_id = self.location_pool.read(cr, uid, self.wu_id, ['pos_id'])['pos_id'][0]
        self.patient_id = self.patient_ids[0]
        self.patient_id2 = self.patient_ids[1]

        spell_data = {
            'patient_id': self.patient_id,
            'pos_id': self.pos_id,
            'code': '1234',
            'start_date': dt.now().strftime(dtf)}
        spell2_data = {
            'patient_id': self.patient_id2,
            'pos_id': self.pos_id,
            'code': 'abcd',
            'start_date': dt.now().strftime(dtf)}

        spell_activity_id = self.spell_pool.create_activity(cr, uid, {}, spell_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.spell_id = spell_activity_id
        spell_activity_id = self.spell_pool.create_activity(cr, uid, {}, spell2_data)
        self.activity_pool.start(cr, uid, spell_activity_id)
        self.spell2_id = spell_activity_id
        self.ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55
        }
        self.ews_data_2 = {
            'respiration_rate': 59,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 44.9,
            'blood_pressure_systolic': 300,
            'blood_pressure_diastolic': 280,
            'pulse_rate': 250,
            'avpu_text': 'U'
        }

    # def test_complete_refreshes_ews0_ews1_ews2(self):
    #     cr, uid = self.cr, self.uid
    #
        # first observation
        # ews_activity_id = self.ews_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
        #                                                 {'patient_id': self.patient_id})
        # self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        # result = self.ews_pool.complete(cr, uid, ews_activity_id)
        # self.assertEquals(result, True)
        #
        # cr.execute("""SELECT * FROM ews0""")
        # rows = cr.fetchall()
        # activity.patient_id
        # self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        # self.assertEquals('scheduled', rows[0][2])
        # ews.score
        # self.assertEquals(0, rows[0][5])
        # ews.frequency
        # self.assertEquals(60, rows[0][6])
        # ews.clinical_risk
        # self.assertEquals('None', rows[0][7])

        # cr.execute("""SELECT * FROM ews1""")
        # rows = cr.fetchall()
        # activity.patient_id
        # self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        # self.assertEquals('completed', rows[0][2])
        # ews.score
        # self.assertEquals(3, rows[0][5])
        # ews.frequency
        # self.assertEquals(15, rows[0][6])
        # ews.clinical_risk
        # self.assertEquals('Medium', rows[0][7])
        # activity_rank
        # self.assertEquals(1, rows[0][10])

        # cr.execute("""SELECT * FROM ews2""")
        # self.assertEquals([], cr.fetchall())

        # second observation
        # triggered_ews_id = self.activity_pool.search(cr, uid, [
        #     ['creator_id', '=', ews_activity_id],
        #     ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        # self.ews_pool.submit(cr, uid, triggered_ews_id[0], self.ews_data_2)
        # result = self.ews_pool.complete(cr, uid, triggered_ews_id[0])
        # self.assertEquals(result, True)
        #
        # cr.execute("""SELECT * FROM ews1""")
        # rows = cr.fetchall()
        # activity.patient_id
        # self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        # self.assertEquals('completed', rows[0][2])
        # ews.score
        # self.assertEquals(14, rows[0][5])
        # ews.frequency
        # self.assertEquals(60, rows[0][6])
        # ews.clinical_risk
        # self.assertEquals('High', rows[0][7])
        # activity_rank
        # self.assertEquals(1, rows[0][10])

    # def test_complete_refreshes_nh_clinical_wardboard_is_updated(self):
    #     cr, uid = self.cr, self.uid

        # first observation
        # ews_activity_id = self.ews_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
        #                                                 {'patient_id': self.patient_id})
        # self.ews_pool.submit(cr, uid, ews_activity_id, self.ews_data)
        # self.ews_pool.complete(cr, uid, ews_activity_id)

        # second observation
        # triggered_ews_id = self.activity_pool.search(cr, uid, [
        #     ['creator_id', '=', ews_activity_id],
        #     ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        # self.ews_pool.submit(cr, uid, triggered_ews_id[0], self.ews_data_2)
        # self.ews_pool.complete(cr, uid, triggered_ews_id[0])
        #
        # cr.execute("""SELECT * FROM ews1""")
        # ews1_rows = cr.fetchall()
        #
        # cr.execute("""SELECT * FROM nh_clinical_wardboard""")
        # wb_rows = cr.fetchall()
        #
        # test for correct patient
        # self.assertEquals(True, self.patient_id in (row[1] for row in wb_rows))
        # row = [row for row in wb_rows if row[1] == self.patient_id][0]
        # spell_code
        # self.assertEquals('1234', row[6])
        # ews_score (should be equal to ews1.score)
        # ews1_score = str(ews1_rows[0][5])
        # self.assertEquals(row[23], ews1_score)
        # ews_trend_string
        # self.assertEquals(row[25], 'up')
        # clinical_risk (should be equal to ews1.clinical_risk)
        # ews1_clinical_risk = ews1_rows[0][7]
        # self.assertEquals(row[26], ews1_clinical_risk)

    # def test_create_refreshes_ward_locations(self):
    #     cr, uid = self.cr, self.uid
    #
    #     cr.execute("""SELECT * FROM ward_locations""")
    #     rows = cr.fetchall()
    #
    #     context_id = self.context_pool.search(cr, uid, [['name', '=', 'eobs']])
    #     create new location and refresh materialized view
        # bed_id = self.location_pool.create(cr, uid, {
        #             'name': 'test_bed', 'parent_id': self.wu_id,
        #             'usage': 'bed', 'context_ids': [[6, False, context_id]]})

        # location_ids = (row[0] for row in rows)
        # self.assertEquals(False, bed_id in location_ids)
        #
        # cr.execute("""SELECT * FROM ward_locations""")
        # rows = cr.fetchall()
        # location_ids = (row[0] for row in rows)
        # self.assertEquals(True, bed_id in location_ids)

    # def test_complete_refreshes_placement(self):
    #     cr, uid = self.cr, self.uid
    #
    #     activity_ids = self.activity_pool.search(cr, uid, [
    #         ('data_model', '=', 'nh.clinical.spell'),
    #         ('patient_id', '=', self.patient_id)])
    #     place_id = self.placement_pool.create_activity(cr, uid, {'parent_id': activity_ids[0],
    #                                                              'patient_id': self.patient_id})
    #     bed_id = self.location_pool.search(cr, uid, [
    #                  ['parent_id', '=', self.wu_id], ['is_available', '=', True], ['usage', '=', 'bed']])
    #     self.placement_pool.submit(cr, uid, place_id, {'location_id': bed_id[0], 'patient_id': self.patient_id,
    #                                                 'suggested_location_id': self.wu_id})
    #     self.placement_pool.complete(cr, uid, place_id)
    #
    #     cr.execute("""SELECT * FROM placement """)
    #     rows = cr.fetchall()
    #     self.assertEquals(len(rows), 1)
    #     self.assertEquals('completed', rows[0][2])
    #     self.assertEquals(rows[0][0], self.patient_id)
    #
    # def test_complete_refreshes_param(self):
    #     cr, uid = self.cr, self.uid

        # first observation
        # mrsa_activity_id = self.mrsa_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
        #                                                 {'patient_id': self.patient_id})
        # self.mrsa_pool.submit(cr, uid, mrsa_activity_id, {'mrsa': True})
        # self.mrsa_pool.complete(cr, uid, mrsa_activity_id)
        # cr.execute("""SELECT * FROM param""")
        # rows = cr.fetchall()
        # self.assertEquals(rows[0][3], True)

        # second observation
        # diabetes_activity_id = self.diabetes_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
        #                                                 {'patient_id': self.patient_id})
        # self.diabetes_pool.submit(cr, uid, diabetes_activity_id, {'diabetes': False})
        # self.activity_pool.complete(cr, uid, diabetes_activity_id)
        # cr.execute("""SELECT * FROM param""")
        # rows = cr.fetchall()
        # self.assertEquals(rows[0][2], False)
