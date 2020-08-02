import json

from datetime import datetime

from env_vars import *


def redis_add_submission(problem_id: str, username: str, score: float, job_id: str, source_code: str):
    submission_json = json.dumps({'problem_id': problem_id, 'username': username, 'score': score, 'job_id': job_id,
                                  'timestamp': datetime.now().strftime("%m/%d/%Y %H:%M:%S")})
    REDIS_CONN.lpush('submissions', submission_json)
    REDIS_CONN.lpush('submission_source', source_code)


def redis_get_all_submissions():
    return REDIS_CONN.lrange('submissions', 0, -1)


def redis_get_submission_source(i):
    return REDIS_CONN.lindex('submission_source', i)
