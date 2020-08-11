"""
Simple python script that launches a worker (for rq).
"""

from misc.env_vars import *
from rq import Worker, Queue, Connection

if __name__ == '__main__':
    with Connection(REDIS_CONN):
        worker = Worker(Queue('default'))
        worker.work(logging_level="INFO")
