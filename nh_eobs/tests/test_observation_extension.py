from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestClinicalPatientObservationEwsRefresh(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestClinicalPatientObservationEwsRefresh, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api_pool = cls.registry('nh.clinical.api')

        cls.apidemo = cls.registry('nh.clinical.api.demo')
        cls.eobs_api = cls.registry('nh.eobs.api')
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')

        cls.patient_ids = cls.apidemo.build_unit_test_env1(cr, uid, bed_count=4, patient_count=4)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

        cls.patient_id = cls.patient_ids[0]
        cls.patient_id2 = cls.patient_ids[1]
        spell_data = {
            'patient_id': cls.patient_id,
            'pos_id': cls.pos_id,
            'code': '1234',
            'start_date': dt.now().strftime(dtf)}
        spell2_data = {
            'patient_id': cls.patient_id2,
            'pos_id': cls.pos_id,
            'code': 'abcd',
            'start_date': dt.now().strftime(dtf)}

        spell_activity_id = cls.spell_pool.create_activity(cr, uid, {}, spell_data)
        cls.activity_pool.start(cr, uid, spell_activity_id)
        cls.spell_id = spell_activity_id
        spell_activity_id = cls.spell_pool.create_activity(cr, uid, {}, spell2_data)
        cls.activity_pool.start(cr, uid, spell_activity_id)
        cls.spell2_id = spell_activity_id

    def test_complete_and_refresh_ews0_ews1_ews2_from_wardboard(self):
        cr, uid = self.cr, self.uid
        ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A'
        }

        cr.execute("""SELECT * FROM ews0""")
        self.assertEquals([], cr.fetchall())

        ews_activity_id = self.ews_pool.create_activity(cr, uid, {'parent_id': self.spell_id},
                                                        {'patient_id': self.patient_id})
        self.ews_pool.submit(cr, uid, ews_activity_id, ews_data)
        result = self.ews_pool.complete(cr, uid, ews_activity_id)
        self.assertEquals(result, True)

        cr.execute("""SELECT * FROM ews0""")
        rows = cr.fetchall()
        # activity.patient_id
        self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        self.assertEquals('scheduled', rows[0][2])
        # ews.score
        self.assertEquals(0, rows[0][5])
        # ews.frequency
        self.assertEquals(60, rows[0][6])
        # ews.clinical_risk
        self.assertEquals('None', rows[0][7])

        cr.execute("""SELECT * FROM ews1""")
        rows = cr.fetchall()
        # activity.patient_id
        self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        self.assertEquals('completed', rows[0][2])
        # ews.score
        self.assertEquals(3, rows[0][5])
        # ews.frequency
        self.assertEquals(15, rows[0][6])
        # ews.clinical_risk
        self.assertEquals('Medium', rows[0][7])
        # activity_rank
        self.assertEquals(1, rows[0][10])

        cr.execute("""SELECT * FROM ews2""")
        self.assertEquals([], cr.fetchall())

        ews_data = {
            'respiration_rate': 59,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 44.9,
            'blood_pressure_systolic': 300,
            'blood_pressure_diastolic': 280,
            'pulse_rate': 250,
            'avpu_text': 'U'
        }

        triggered_ews_id = self.activity_pool.search(cr, uid, [
            ['creator_id', '=', ews_activity_id],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.ews_pool.submit(cr, uid, triggered_ews_id[0], ews_data)
        result = self.ews_pool.complete(cr, uid, triggered_ews_id[0])
        self.assertEquals(result, True)

        cr.execute("""SELECT * FROM ews1""")
        rows = cr.fetchall()
        # activity.patient_id
        self.assertEquals(self.patient_id, rows[0][0])
        # activity.state
        self.assertEquals('completed', rows[0][2])
        # ews.score
        self.assertEquals(14, rows[0][5])
        # ews.frequency
        self.assertEquals(60, rows[0][6])
        # ews.clinical_risk
        self.assertEquals('High', rows[0][7])
        # activity_rank
        self.assertEquals(1, rows[0][10])

    def test_nh_clinical_wardboard_is_updated(self):
        cr, uid = self.cr, self.uid

        cr.execute("""SELECT * FROM nh_clinical_wardboard""")
        wb_rows = cr.fetchall()
        cr.execute("""SELECT * FROM ews1""")
        ews1_rows = cr.fetchall()

        # test for correct patient
        self.assertEquals(wb_rows[0][1], self.patient_id)
        # spell_code
        self.assertEquals(wb_rows[0][6], '1234')
        # ews_score (should be equal to ews1.score)
        ews1_score = str(ews1_rows[0][5])
        self.assertEquals(wb_rows[0][23], ews1_score)
        # ews_trend_string
        self.assertEquals(wb_rows[0][25], 'up')
        # clinical_risk (should be equal to ews1.clinical_risk)
        ews1_clinical_risk = ews1_rows[0][7]
        self.assertEquals(wb_rows[0][26], ews1_clinical_risk)