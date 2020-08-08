import json
import pytz

from datetime import datetime

from env_vars import *


def redis_add_submission(problem_id: str, username: str, score: float, job_id: str, source_code: str, verdict: str):
    timestamp = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific'))
    timestamp = timestamp.strftime("%m/%d/%Y %I:%M:%S %p")
    submission_json = json.dumps({'problem_id': problem_id, 'username': username, 'score': score, 'job_id': job_id,
                                  'verdict': verdict, 'timestamp': timestamp})
    REDIS_CONN.rpush('submissions', submission_json)
    REDIS_CONN.rpush('submission_source', source_code)
    REDIS_CONN.set('submission_index:{}'.format(job_id), redis_get_num_submissions() - 1)


def redis_get_submissions(page=1):
    submissions = REDIS_CONN.lrange('submissions', -(page * PAGE_SIZE), -(page-1) * PAGE_SIZE - 1)[::-1]
    for i in range(len(submissions)):
        submissions[i] = json.loads(submissions[i])
    return submissions


def redis_get_submission(job_id):
    submission = REDIS_CONN.lindex('submissions', redis_get_index_from_id(job_id))
    submission = json.loads(submission)
    return submission


def redis_get_submission_source(job_id):
    return REDIS_CONN.lindex('submission_source', redis_get_index_from_id(job_id))


def redis_get_index_from_id(job_id):
    return REDIS_CONN.get('submission_index:{}'.format(job_id))


def redis_get_num_submissions():
    return REDIS_CONN.llen('submissions')
