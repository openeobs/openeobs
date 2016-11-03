# -*- coding: utf-8 -*-
"""
A single place for different frequency values to be read from.
Times are in minutes.
"""
FIFTEEN_MINUTES = 15
THIRTY_MINUTES = 30
ONE_HOUR = 60
TWO_HOURS = 120
FOUR_HOURS = 240
SIX_HOURS = 360
EIGHT_HOURS = 480
TEN_HOURS = 600
TWELVE_HOURS = 720
ONE_DAY = 1440
THREE_DAYS = 4320
ONE_WEEK = 10080

# Tuples with the time and a label.
EVERY_15_MINUTES = (FIFTEEN_MINUTES, 'Every 15 Minutes')
EVERY_30_MINUTES = (THIRTY_MINUTES, 'Every 30 Minutes')
EVERY_HOUR = (ONE_HOUR, 'Every Hour')
EVERY_2_HOURS = (TWO_HOURS, 'Every 2 Hours')
EVERY_4_HOURS = (FOUR_HOURS, 'Every 4 Hours')
EVERY_6_HOURS = (SIX_HOURS, 'Every 6 Hours')
EVERY_8_HOURS = (EIGHT_HOURS, 'Every 8 Hours')
EVERY_10_HOURS = (TEN_HOURS, 'Every 10 Hours')
EVERY_12_HOURS = (TWELVE_HOURS, 'Every 12 Hours')
EVERY_DAY = (ONE_DAY, 'Every Day')
EVERY_3_DAYS = (THREE_DAYS, 'Every 3 Days')
EVERY_WEEK = (ONE_WEEK, 'Every Week')

# To summarise the mappings below, frequencies after refusals are capped at
# 24 hours.
#
# Could have just made a simple function but decided to write them out long
# hand as they may change in the future. Return the tuple with the label rather
# than just the time so it can be useful in more scenarios.
AFTER_PATIENT_REFUSED_NO_RISK_FREQUENCIES = {
    EVERY_12_HOURS[0]: EVERY_12_HOURS,
    EVERY_DAY[0]: EVERY_DAY,
    EVERY_3_DAYS[0]: EVERY_3_DAYS,
    EVERY_WEEK[0]: EVERY_WEEK
}
AFTER_PATIENT_REFUSED_LOW_RISK_FREQUENCIES = {
    EVERY_15_MINUTES[0]: EVERY_15_MINUTES,
    EVERY_30_MINUTES[0]: EVERY_30_MINUTES,
    EVERY_HOUR[0]: EVERY_HOUR,
    EVERY_2_HOURS[0]: EVERY_2_HOURS,
    EVERY_4_HOURS[0]: EVERY_4_HOURS,
    EVERY_6_HOURS[0]: EVERY_6_HOURS,
    EVERY_8_HOURS[0]: EVERY_8_HOURS,
    EVERY_12_HOURS[0]: EVERY_12_HOURS,
    EVERY_DAY[0]: EVERY_DAY,
    EVERY_3_DAYS[0]: EVERY_DAY,
    EVERY_WEEK[0]: EVERY_WEEK
}
AFTER_PATIENT_REFUSED_MEDIUM_RISK_FREQUENCIES = {
    EVERY_HOUR[0]: EVERY_HOUR
}
AFTER_PATIENT_REFUSED_HIGH_RISK_FREQUENCIES = {
    EVERY_30_MINUTES[0]: EVERY_30_MINUTES
}
AFTER_PATIENT_REFUSED_UNKNOWN_RISK_FREQUENCIES = {
    EVERY_15_MINUTES[0]: EVERY_4_HOURS
}
AFTER_PATIENT_REFUSED_TRANSFER_FREQUENCIES = {
    'transfer': EVERY_15_MINUTES
}
AFTER_PATIENT_REFUSED_OBS_RESTART_FREQUENCIES = {
    'obs restart': EVERY_HOUR
}


def as_list():
    return [
        EVERY_15_MINUTES,
        EVERY_30_MINUTES,
        EVERY_HOUR,
        EVERY_2_HOURS,
        EVERY_4_HOURS,
        EVERY_6_HOURS,
        EVERY_8_HOURS,
        EVERY_10_HOURS,
        EVERY_12_HOURS,
        EVERY_DAY,
        EVERY_3_DAYS,
        EVERY_WEEK
    ]


def minutes_only():
    return [minutes for minutes, _ in as_list()]


def get_label_for_minutes(minutes):
    label = ''
    for frequency in as_list():
        if frequency[0] == minutes:
            label = frequency[1]
    return label
