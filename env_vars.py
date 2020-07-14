import os

# Time limit for programs. Java gets x1.5, Python gets x2. Rounded to 1 decimal place.
BASE_TIME_LIMIT = round(os.environ.get('BASE_TIME_LIMIT', 2), 1)
# Memory limit for programs. Must be an integer.
BASE_MEMORY_LIMIT = int(os.environ.get('BASE_MEMORY_LIMIT', 128))
# Number of seconds to add to the wall time threshold (used to kill a program that runs for too long).
# Rounded to 1 decimal place.
WALL_TIME_EXTENSION = round(float(os.environ.get('WALL_TIME_EXTENSION', 2)), 1)
# The amount of time to sleep in between each program status check. Too many checks may slow down the program.
# Rounded to 2 decimal places.
CHECK_INTERVAL = round(float(os.environ.get('CHECK_INTERVAL', 0.2)), 2)

# Enables / disables debug outputs.
DEBUG = os.environ.get('DEBUG', '0') == '1'
# Enables / disables very verbose debug outputs.
DEBUG_LOW = os.environ.get('DEBUG_LOW', '0') == '1'
# Enables / disables adding stdout and stderr to the response. (WARNING: Can be used to hack the system!)
PROGRAM_OUTPUT = os.environ.get('PROGRAM_OUTPUT', '0') == '1'

# If enabled, shows program time / memory usage that's a tiny bit over the limits.
SHOW_BORDER = os.environ.get('SHOW_BORDER', '0') == '1'
# Additional seconds before the displayed time taken is capped.
TIME_BORDER = round(float(os.environ.get('TIME_BORDER', 1)), 1)
# Additional MBs before the displayed memory usage is capped. Must be an integer.
MEM_BORDER = int(os.environ.get('MEM_BORDER', 16))

# Number of workers for gunicorn to use.
WORKER_COUNT = os.environ.get('WORKER_COUNT', 1)
# Number of threads for gunicorn to use.
THREAD_COUNT = os.environ.get('THREAD_COUNT', 3)
