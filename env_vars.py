import os

"""
The following settings deal with debug outputs.
"""
# Enables / disables debug outputs.
DEBUG = os.environ.get('DEBUG', '0') == '1'
# Enables / disables very verbose debug outputs.
DEBUG_LOW = os.environ.get('DEBUG_LOW', '0') == '1'
# Enables / disables the most verbose of verbose debug outputs. Warning: Lots of text
DEBUG_LOWEST = os.environ.get('DEBUG_LOWEST', '0') == '1'
# Enables / disables adding the first X bytes of stdout and stderr to the response. Only shows in the debug log.
# This value should be an integer in the range 0-256 (to prevent huge amounts of output).
PROGRAM_OUTPUT = int(os.environ.get('PROGRAM_OUTPUT', 0))

"""
The following options deal with program compilation. They are used to prevent compiler bombs.
It's probably best to leave these at their default settings.
"""
# Time limit while compiling a program (in seconds).
COMPILE_TIME_LIMIT = round(float(os.environ.get('COMPILE_TIME_LIMIT', 10)), 1)
# Memory limit while compiling a program (in MB). Must be an integer.
COMPILE_MEMORY_LIMIT = int(os.environ.get('COMPILE_MEMORY_LIMIT', 256))
# Outputs the first X bytes of a compile error to the person who submitted the program.
# This value should be an integer in the range 0-512 (to prevent huge amounts of output).
COMPILE_ERROR_OUTPUT = int(os.environ.get('COMPILE_ERROR_OUTPUT', 512))
# Maximum size of the final executable (in MB). Must be an integer.
MAX_COMPILE_SIZE = int(os.environ.get('MAX_COMPILE_SIZE', 16))

"""
These settings deal with the actual running of the compiled program.
Most of these should be left at default, unless the machine you're running this on has a weak CPU or low RAM.
"""
# Maximum possible time limit for programs (in seconds). Java gets x1.5, Python gets x2. Rounded to 1 decimal place.
# Note that the actual time limit for a program is set by the info.yml file for each individual problem.
MAX_TIME_LIMIT = round(float(os.environ.get('MAX_TIME_LIMIT', 5)), 1)
# Maximum possible memory limit for programs (in MB). Must be an integer.
# Note that the actual memory limit for a program is set by the info.yml file for each individual problem.
MAX_MEMORY_LIMIT = int(os.environ.get('MAX_MEMORY_LIMIT', 256))
# Max file size that the program can create (including stdout and stderr) in MB. Must be an integer.
MAX_OUTPUT_SIZE = int(os.environ.get('MAX_OUTPUT_SIZE', 16))
# Number of seconds to add to the wall time threshold (used to kill a program that runs for too long).
# Rounded to 1 decimal place.
WALL_TIME_EXTENSION = round(float(os.environ.get('WALL_TIME_EXTENSION', 1.5)), 1)
# The amount of seconds to sleep in between each program status check. Too many checks may slow down the program.
# Rounded to 2 decimal places.
CHECK_INTERVAL = round(float(os.environ.get('CHECK_INTERVAL', 0.2)), 2)

"""
These settings deal with the web server (gunicorn).
"""
# Number of workers for gunicorn to use.
WORKER_COUNT = os.environ.get('WORKER_COUNT', 1)
# Number of threads for gunicorn to use.
THREAD_COUNT = os.environ.get('THREAD_COUNT', 2)
# Max code file size allowed, in KILOBYTES (KB)!!!!! Must be an integer.
MAX_CODE_SIZE = int(os.environ.get('MAX_CODE_SIZE', 256))

"""
Miscellaneous settings
"""
# How long to keep the results of jobs (in seconds). Applies to both failed and successful jobs.
# Defaults to 1 year = 31536000 seconds.
RESULT_TTL = os.environ.get('RESULT_TTL', 31536000)

"""
Non-configurable variables
"""
PROBLEM_INFO_PATH = "./sample_problem_info"
if os.path.isdir("/problem_info"):
    PROBLEM_INFO_PATH = "/problem_info"
