# Part of Open eObs. See LICENSE file for full copyright and licensing details.
def migrate(cr, installed_version):
    if installed_version[-3:] == "1.0":
        cr.execute(
            """
            ALTER TABLE nh_clinical_patient_mrsa RENAME COLUMN status TO mrsa;
            ALTER TABLE nh_clinical_patient_diabetes RENAME COLUMN status TO diabetes;
            ALTER TABLE nh_clinical_patient_weight_monitoring RENAME COLUMN status to weight_monitoring;
            """
        )