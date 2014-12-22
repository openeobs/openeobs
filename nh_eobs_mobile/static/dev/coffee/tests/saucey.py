import requests, json, time

username = 'neovahealth'
access_key = 'b7964b4f-b0e7-44ee-81e3-883c3ee47652'
run_job_url = 'https://saucelabs.com/rest/v1/neovahealth/js-tests'
get_jobs_url = 'https://saucelabs.com/rest/v1/neovahealth/js-tests/status'
get_job_url = 'https://saucelabs.com/rest/v1/neovahealth/jobs/{job_id}/assets/log.json'
time_to_wait = 70
browsers = [
    ['OS X 10.9', 'iPhone', '6.0'],
    ['OS X 10.9', 'iPhone', '8.0']
]
test_suite_url = 'http://nh-ci-nhc01.nhtek.net:8069/nh_eobs_mobile/static/dev/coffee/tests/SpecRunner.html'
config = {
    'platforms': browsers,
    'record-video': False,
    'record-screenshots': False,
    'framework': 'jasmine',
    'max-duration': 60,
    'url': test_suite_url
}
jobs = []

# do the call to set up jobs
run_jobs = requests.post(run_job_url, auth=(username, access_key), data=json.dumps(config))
jobs_json = run_jobs.json()['js tests']
print 'successfully scheduled {jobs} jobs, waiting {time} seconds to let them run'.format(jobs=len(jobs_json), time=(len(jobs_json)*time_to_wait))
time.sleep(len(jobs_json)*time_to_wait)
get_jobs = requests.post(get_jobs_url, auth=(username, access_key), data=json.dumps({'js tests': jobs_json}))
jobs = get_jobs.json()['js tests']
print jobs

# print 'successfully scheduled {jobs} jobs, waiting {time} seconds to let them run'.format(jobs=len(jobs), time=(len(jobs)*time_to_wait))
# time.sleep(len(jobs)*time_to_wait)
#
for job in jobs:
    print 'Processing {job_id} - {platform}'.format(job_id=job['job_id'], platform=job['platform'])
    job_result = requests.get(get_job_url.format(job_id=job['job_id']), auth=(username, access_key))
    results = job_result.json()
    print ' '
    print ' '
    print ' '
    print results
    print ' '
    print ' '
    print ' '
    for result in results:
        if isinstance(result['result'], dict):
            r = result['result']['suites'] if 'suites' in result['result'] else []
            for res in r:
                print '    {desc}'.format(desc=res['description'])
                for spec in res['specs']:
                    print '        {d}'.format(d=spec['description'])
                    if spec['passed']:
                        print '              PASS'
                    else:
                        print '              FAIL'
                        print spec['failures']

#
