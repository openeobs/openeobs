# -*- coding: utf-8 -*-
spell_activity_id = 1

refusal_episode_first = {
    'count': 1,
    'first_refusal_date_terminated': '2017-01-03 17:49:12',
    'freq_date_terminated': None,
    'freq_state': None,
    'freq_terminate_uid': None,
    'review_date_terminated': None,
    'review_state': None,
    'review_terminate_uid': None,
    'spell_activity_id': 10
}
refusal_episode_second = {
    'count': 1,
    'first_refusal_date_terminated': '2017-01-03 17:50:13',
    'freq_date_terminated': None,
    'freq_state': None,
    'freq_terminate_uid': None,
    'review_date_termninated': None,
    'review_state': None,
    'review_terminate_uid': None,
    'spell_activity_id': 10
}
refusal_episode_third = {
    'count': 1,
    'first_refusal_date_terminated': '2017-01-03 17:51:14',
    'freq_date_terminated': None,
    'freq_state': None,
    'freq_terminate_uid': None,
    'review_date_termninated': None,
    'review_state': None,
    'review_terminate_uid': None,
    'spell_activity_id': 10
}
refusal_episodes = [
    refusal_episode_first,
    refusal_episode_second,
    refusal_episode_third
]


def mock_get_refusal_episodes(*args, **kwargs):
    return refusal_episodes
