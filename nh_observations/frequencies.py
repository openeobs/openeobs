# -*- coding: utf-8 -*-
"""
A single place for different frequency values to be read from.
Values are tuples with the time in minutes and a description.
"""
EVERY_15_MINUTES = (15, 'Every 15 Minutes')
EVERY_30_MINUTES = (30, 'Every 30 Minutes')
EVERY_HOUR = (60, 'Every Hour')
EVERY_2_HOURS = (120, 'Every 2 Hours')
EVERY_4_HOURS = (240, 'Every 4 Hours')
EVERY_6_HOURS = (360, 'Every 6 Hours')
EVERY_8_HOURS = (480, 'Every 8 Hours')
EVERY_10_HOURS = (600, 'Every 10 Hours')
EVERY_12_HOURS = (720, 'Every 12 Hours')
EVERY_DAY = (1440, 'Every Day')
EVERY_3_DAYS = (4320, 'Every 3 Days')
EVERY_WEEK = (10080, 'Every Week')


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
