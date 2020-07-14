import os
from env_vars import WORKER_COUNT, THREAD_COUNT

bind = '0.0.0.0:' + str(os.environ.get('PORT', 8080))

# Using threaded workers
worker_class = 'gthread'
workers = WORKER_COUNT
threads = THREAD_COUNT

# Timeout can be pretty short
timeout = 60
graceful_timeout = 60

# Request sizes should be pretty small
limit_request_line = 1000
limit_request_fields = 20
limit_request_field_size = 2000

# daemon = True
