import os

# Time limit for programs (in seconds). Java gets x1.5, Python gets x2. Rounded to 1 decimal place.
BASE_TIME_LIMIT = round(float(os.environ.get('BASE_TIME_LIMIT', 2)), 1)
# Memory limit for programs (in MB). Must be an integer.
BASE_MEMORY_LIMIT = int(os.environ.get('BASE_MEMORY_LIMIT', 96))
# Number of seconds to add to the wall time threshold (used to kill a program that runs for too long).
# Rounded to 1 decimal place.
WALL_TIME_EXTENSION = round(float(os.environ.get('WALL_TIME_EXTENSION', 1.5)), 1)
# The amount of seconds to sleep in between each program status check. Too many checks may slow down the program.
# Rounded to 2 decimal places.
CHECK_INTERVAL = round(float(os.environ.get('CHECK_INTERVAL', 0.2)), 2)

# Enables / disables debug outputs.
DEBUG = os.environ.get('DEBUG', '0') == '1'
# Enables / disables very verbose debug outputs.
DEBUG_LOW = os.environ.get('DEBUG_LOW', '0') == '1'
# Enables / disables adding the first X bytes of stdout and stderr to the response.
# This value should either be 0 or 512 (to prevent huge amounts of output).
# (WARNING: Can be used to hack the VM! Only use this option to debug.)
PROGRAM_OUTPUT = int(os.environ.get('PROGRAM_OUTPUT', 0))

# If enabled, shows program time / memory usage that's a tiny bit over the limits.
SHOW_BORDER = os.environ.get('SHOW_BORDER', '0') == '1'
# Additional seconds before the displayed time taken is capped.
TIME_BORDER = round(float(os.environ.get('TIME_BORDER', 1)), 1)
# Additional MBs before the displayed memory usage is capped. Must be an integer.
MEM_BORDER = int(os.environ.get('MEM_BORDER', 16))

# Number of workers for gunicorn to use.
WORKER_COUNT = os.environ.get('WORKER_COUNT', 1)
# Number of threads for gunicorn to use.
THREAD_COUNT = os.environ.get('THREAD_COUNT', 2)
# Max uploaded file size (summed across all submitted files).
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 32))
# Max output size to read in MB (anything past this size will automatically return WA).
MAX_OUTPUT_SIZE = int(os.environ.get('MAX_OUTPUT_SIZE', 16))
