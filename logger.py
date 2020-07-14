"""
Very simple logger: Literally just adds the current date and time to the start of each message.
"""

import sys
from datetime import datetime


def log(msg):
    now = datetime.now()
    dt_string = now.strftime('%m/%d %H:%M:%S')
    sys.stderr.write('[SJ ' + dt_string + '] ' + msg + '\n')
