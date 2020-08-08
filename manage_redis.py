import json
import pytz

from datetime import datetime

from env_vars import *


def redis_add_submission(problem_id: str, username: str, score: float, job_id: str, source_code: str, verdict: str):
    timestamp = pytz.timezone('US/Pacific').localize(datetime.now())
    timestamp = timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
    submission_json = json.dumps({'problem_id': problem_id, 'username': username, 'score': score, 'job_id': job_id,
                                  'verdict': verdict, 'timestamp': timestamp})
    REDIS_CONN.lpush('submissions', submission_json)
    REDIS_CONN.lpush('submission_source', source_code)


def redis_get_submissions(page=1):
    submissions = REDIS_CONN.lrange('submissions', (page-1) * PAGE_SIZE, page * PAGE_SIZE)
    for i in range(len(submissions)):
        submissions[i] = json.loads(submissions[i])
    return submissions


def redis_get_submission(i):
    submission = REDIS_CONN.lindex('submissions', i)
    submission = json.loads(submission)
    return submission


def redis_get_submission_source(i):
    return REDIS_CONN.lindex('submission_source', i)


def redis_get_num_submissions():
    return REDIS_CONN.llen('submissions')
