import os

bind = '0.0.0.0:' + str(os.environ.get('PORT', 8080))
workers = 1
threads = 1
timeout = 60
graceful_timeout = 60
