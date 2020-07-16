"""
Simple python script that launches a worker (for rq).
"""

from redis import Redis
from rq import Worker, Queue, Connection

conn = Redis()

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(Queue('default'))
        worker.work(logging_level="INFO")
