'''
This file contains the code that judges a submission.
Note: This implementation can only handle one submission at a time. It will reject other submissions while a
submission is being evaluated. Luckily, the gunicorn server is able to queue up submissions!
'''

import resource
import subprocess
import tempfile
import psutil
import os

from werkzeug.utils import secure_filename

# Time limit for programs. Java gets x1.5, Python gets x2
BASE_TIME_LIMIT = int(os.environ.get('BASE_TIME_LIMIT', 3))
# Memory limit for programs.
BASE_MEMORY_LIMIT = int(os.environ.get('BASE_MEMORY_LIMIT', 256))
# Additional seconds to add to the wall time threshold (used to kill a program that runs for too long).
WALL_TIME_EXTENSION = round(float(os.environ.get('WALL_TIME_EXTENSION', 1)), 1)

# If disabled, kills the web server after every request (to keep from reusing containers). Very unreliable.
NO_SHUTDOWN = os.environ.get('NO_SHUTDOWN', '1') == '1'
# Enables / disables debug outputs.
DEBUG = os.environ.get('DEBUG', '0') == '1'

# If enabled, shows program time / memory usage that's a tiny bit over the limits.
SHOW_BORDER = os.environ.get('SHOW_BORDER', '0') == '1'
# Additional seconds before the displayed time taken is capped.
TIME_BORDER = round(float(os.environ.get('TIME_BORDER', 1)), 1)
# Additional MBs before the displayed memory usage is capped.
MEM_BORDER = int(os.environ.get('MEM_BORDER', 32))

tempdir: tempfile.TemporaryDirectory

def do_cleanup():
    global tempdir
    tempdir.cleanup()
    # If NO_SHUTDOWN is not enabled, forcefully kill gunicorn so that each container only handles one request.
    if not NO_SHUTDOWN: subprocess.Popen(['pkill', '-QUIT', 'gunicorn'])

def error(msg, log=None):
    to_return = {'error': msg}
    if DEBUG:
        print("Returning", to_return)
        if log:
            to_return['log'] = log
    do_cleanup()
    return to_return

def verdict(verdict, score, time=0.0, memory=0.0, testcase=0):
    global tempdir
    # input()
    to_return = {'verdict': verdict, 'score': score, 'time': time, 'memory': memory, 'testcase': testcase}
    if DEBUG:
        if verdict != 'CE':
            # Add program stdout / stderr
            foutput = open(tempdir.name + '/output.out.txt', 'r')
            to_return['stdout'] = foutput.readlines()
            foutput.close()
            ferror = open(tempdir.name + '/error.err.txt', 'r')
            to_return['stderr'] = ferror.readlines()
            ferror.close()
        print("Returning", to_return)
    do_cleanup()
    return to_return

def limit_memory():
    # Make sure the stack size is as big as the memory limit
    resource.setrlimit(resource.RLIMIT_STACK, (BASE_MEMORY_LIMIT * 1024 * 1024, resource.RLIM_INFINITY))
    # resource.setrlimit(resource.RLIMIT_AS, ((BASE_MEMORY_LIMIT + 128) * 1024 * 1024, resource.RLIM_INFINITY))

def judge_submission(request):
    global tempdir
    if DEBUG: print('-' * 60)

    # Initialize the temporary directory
    tempdir = tempfile.TemporaryDirectory()

    # Get files
    if 'type' not in request.form:
        return error('No submission language!')
    if 'code' not in request.files or not request.files['code']:
        return error('No code file submitted!')
    if 'input' not in request.files or not request.files['input']:
        return error('No input file submitted!')
    if 'output' not in request.files or not request.files['output']:
        return error('No output file submitted!')

    fcode = request.files['code']
    finput = request.files['input']
    fanswer = request.files['output']

    # Move input / output files to that temporary directory
    finput.save(tempdir.name + '/input.in.txt')

    # Compile the code file
    if DEBUG: print("Compiling", fcode.filename)
    compiled_filename = None
    if request.form['type'] == 'java':
        # Remove extension from the filename to determine class name
        code_filename = secure_filename(fcode.filename)
        if '.java' not in code_filename:
            return error('Missing .java file extension!')
        java_index = code_filename.index('.java')
        compiled_filename = code_filename[:java_index]

        # Save & compile the file
        fcode.save(tempdir.name + '/' + code_filename)
        result = subprocess.run(['javac', tempdir.name + '/' + code_filename],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    elif request.form['type'] == 'cpp':
        # Save & compile the file
        compiled_filename = 'code'
        fcode.save(tempdir.name + '/code.cpp')
        result = subprocess.run(['g++', '-std=c++14', '-O2', '-o', tempdir.name + '/code', tempdir.name + '/code.cpp'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    elif request.form['type'] == 'python':
        # Save & compile the file
        # Add two lines at the beginning to allow for deep recursion
        compiled_filename = 'code.py'
        fcode.save(tempdir.name + '/code_raw.py')
        fcode_old = open(tempdir.name + '/code_raw.py', 'r')
        fcode_new = open(tempdir.name + '/code.py', 'w')
        fcode_new.write('import sys\n')
        fcode_new.write('sys.setrecursionlimit(99999999)\n')
        fcode_new.write(fcode_old.read())
        fcode_old.close()
        fcode_new.close()
        result = subprocess.run(['python3', '-m', 'py_compile', tempdir.name + '/code.py'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    else:
        return error('Invalid submission file type!')

    # Run the program
    if DEBUG: print("Running", compiled_filename)
    time_limit = BASE_TIME_LIMIT
    wall_limit = -1
    mem_limit = BASE_MEMORY_LIMIT
    process = None
    finput = open(tempdir.name + '/input.in.txt', 'r')
    foutput = open(tempdir.name + '/output.out.txt', 'w')
    ferror = open(tempdir.name + '/error.err.txt', 'w')
    time_args = ['/usr/bin/time', '-f', 'metadata %e %U %S %M', '-o', tempdir.name + '/meta.info.txt', '--quiet']
    try:
        if request.form['type'] == 'java':
            time_limit *= 1.5
            mem_limit += 32
            process = psutil.Popen(time_args + ['java', '-Xmx256M', '-Xss128M', compiled_filename], preexec_fn=limit_memory,
                                     cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        elif request.form['type'] == 'cpp':
            time_limit *= 1
            mem_limit += 0
            process = psutil.Popen(time_args + ['./code'], preexec_fn=limit_memory,
                                       cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        elif request.form['type'] == 'python':
            time_limit *= 2
            mem_limit += 0
            process = psutil.Popen(time_args + ['python3', 'code.py'], preexec_fn=limit_memory,
                                     cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        else:
            return error('Invalid submission file type!')
        wall_limit = time_limit + WALL_TIME_EXTENSION
        process.wait(wall_limit)
    except psutil.TimeoutExpired:
        # Kill the process and return a TLE verdict, along with an estimate of the max memory used
        # The estimate takes the sum of the memory used by all child processes, and adds it to the main process
        memory = round((sum([p.memory_info().rss for p in process.children()]) + process.memory_info().rss) / 1024 / 1024, 1)
        memory = min(memory, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))
        process.kill()
        return verdict('TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), memory, 1)

    finput.close()
    foutput.close()
    ferror.close()

    # Process results
    if DEBUG:
        print("Checking answer of", compiled_filename)
    fanswer.save(tempdir.name + '/answer.ans.txt')
    fmeta = open(tempdir.name + '/meta.info.txt', 'r')

    # Parse return of time command
    meta_raw = fmeta.readlines()
    if DEBUG: print("Meta Raw:", meta_raw)
    if 'metadata' not in meta_raw[0]:
        # Remove debug message (happens with runtime errors)
        meta_raw.pop(0)
    meta_list = list(map(float, meta_raw[0].split()[1:]))
    meta_dict = {'time': meta_list[1] + meta_list[2], 'wall': meta_list[0], 'mem': meta_list[3] / 1024}
    fmeta.close()
    if DEBUG: print("Meta: " + str(meta_dict))

    # Determine time (in ms) and memory (in MB)
    time = round(meta_dict['time'], 2)
    time = min(time, time_limit + (TIME_BORDER if SHOW_BORDER else 0))
    wall_time = round(meta_dict['wall'], 2)
    memory = round(meta_dict['mem'], 1)
    memory = min(memory, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))

    # Did the program TLE?
    if time >= time_limit:
        return verdict('TLE', 0, time, memory, 1)
    # Was it killed by the wall clock?
    elif wall_time >= wall_limit:
        return verdict('TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), memory, 1)
    # Did the program MLE?
    elif memory >= mem_limit:
        return verdict('MLE', 0, time, memory, 1)
    # Did the program RE?
    elif process.returncode != 0:
        ferror = open(tempdir.name + '/error.err.txt', 'r')
        # Detect Java memory errors
        if request.form['type'] == 'java' and 'java.lang.OutOfMemoryError' in ferror.read():
            ferror.close()
            return verdict('MLE', 0, time, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit), 1)
        else:
            ferror.close()
            return verdict('RE', 0, time, memory, 1)

    # Diff the results, ignoring whitespace issues and carriage returns
    result = subprocess.run(['diff', '--ignore-trailing-space', '--ignore-space-change', '--strip-trailing-cr',
                             tempdir.name + '/output.out.txt', tempdir.name + '/answer.ans.txt'], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        return verdict('WA', 0, time, memory, 1)

    # Correct answer! :D
    return verdict('AC', 1, time, memory, 1)