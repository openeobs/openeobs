def migrate(cr, installed_version):
    if installed_version[-3:] == '0.1':
        cr.execute(
            """
            ALTER TABLE nh_clinical_patient_pbp_monitoring RENAME COLUMN pbp_monitoring TO status;
            """
        )
