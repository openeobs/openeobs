def migrate(cr, installed_version):
    if installed_version[-3:] == "0.1":
        cr.execute(
            """
            ALTER TABLE nh_clinical_patient_mrsa RENAME COLUMN mrsa TO status;
            ALTER TABLE nh_clinical_patient_diabetes RENAME COLUMN diabetes TO status;
            ALTER TABLE nh_clinical_patient_weight_monitoring RENAME COLUMN weight_monitoring TO status;
            """
        )
