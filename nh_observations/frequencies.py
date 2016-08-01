# -*- coding: utf-8 -*-
"""
A single place for different frequency values to be read from.
Values are tuples with the time in minutes and a description.
"""
EVERY_15_MINUTES = (15, 'Every 15 minutes')
EVERY_30_MINUTES = (30, 'Every 30 minutes')
HOURLY = (60, 'Hourly')
EVERY_2_HOURS = (120, 'Every 2 hours')
EVERY_4_HOURS = (240, 'Every 4 hours')
EVERY_6_HOURS = (360, 'Every 6 hours')
EVERY_8_HOURS = (480, 'Every 8 hours')
EVERY_12_HOURS = (720, 'Every 12 hours')
DAILY = (1440, 'Daily')
TWICE_WEEKLY = (5040, 'Twice weekly')
WEEKLY = (10080, 'Weekly')


def as_list():
    return [
        EVERY_15_MINUTES,
        EVERY_30_MINUTES,
        HOURLY,
        EVERY_2_HOURS,
        EVERY_4_HOURS,
        EVERY_6_HOURS,
        EVERY_8_HOURS,
        EVERY_12_HOURS,
        DAILY,
        TWICE_WEEKLY,
        WEEKLY
    ]


def minutes_only():
    return [minutes for minutes, _ in as_list()]
