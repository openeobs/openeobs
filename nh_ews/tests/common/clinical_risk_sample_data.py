NO_RISK_DATA = {
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'oxygen_administration_flag': 0,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A'
}

LOW_RISK_DATA = {
    'respiration_rate': 11,
    'indirect_oxymetry_spo2': 99,
    'oxygen_administration_flag': 0,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A'
}

MEDIUM_RISK_DATA = {
    'respiration_rate': 11,
    'indirect_oxymetry_spo2': 95,
    'oxygen_administration_flag': 0,
    'body_temperature': 36.0,
    'blood_pressure_systolic': 110,
    'blood_pressure_diastolic': 70,
    'pulse_rate': 50,
    'avpu_text': 'A'
}

HIGH_RISK_DATA = {
    'respiration_rate': 25,
    'indirect_oxymetry_spo2': 93,
    'oxygen_administration_flag': 0,
    'body_temperature': 38.5,
    'blood_pressure_systolic': 100,
    'blood_pressure_diastolic': 70,
    'pulse_rate': 130,
    'avpu_text': 'A'
}

REFUSED_DATA = {
    'respiration_rate': 11,
    'partial_reason': 'refused'
}

PARTIAL_DATA_ASLEEP = {
    'respiration_rate': 11,
    'partial_reason': 'asleep'
}

PARTIAL_DATA_AWAY_FROM_BED = {
    'respiration_rate': 11,
    'partial_reason': 'patient_away_from_bed'
}

FULL_NO_OXYGEN_ADMINISTRATION = {
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A',
    'oxygen_administration_flag': False
}

PARTIAL_NO_RESPIRATION_RATE = {
    'indirect_oxymetry_spo2': 99,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A',
    'oxygen_administration_flag': False,
    'partial_reason': 'patient_away_from_bed'
}

PARTIAL_OXYGEN_ADMINISTRATION_NO_DEVICE = {
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A',
    'oxygen_administration_flag': True,
    'partial_reason': 'patient_away_from_bed'
}

PARTIAL_OXYGEN_ADMINISTRATION_DEVICE = {
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A',
    'oxygen_administration_flag': True,
    'device_id': 34,
    'partial_reason': 'patient_away_from_bed'
}

FULL_OXYGEN_ADMINISTRATION = {
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A',
    'oxygen_administration_flag': True,
    'device_id': 34,
    'concentration': 18
}
