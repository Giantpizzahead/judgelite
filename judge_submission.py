'''
This file contains the code that judges a submission.
Note: This implementation can only handle one submission at a time. It will reject other submissions while a
submission is being evaluated. Luckily, the gunicorn server is able to queue up submissions!
'''

import resource
import subprocess
import tempfile
import psutil

from time import sleep
from app import DEBUG, SHOW_BORDER
from flask import *
from werkzeug.utils import secure_filename

# Java gets +1 second, Python gets +2
BASE_TIME_LIMIT = 3
# Java gets +16 MB
BASE_MEMORY_LIMIT = 128

requestActive = False
tempdir: tempfile.TemporaryDirectory

def error(msg, log=None):
    global requestActive, tempdir
    tempdir.cleanup()
    to_return = {'error': msg}
    if DEBUG:
        print("Returning", to_return)
        if log:
            to_return['log'] = log
    requestActive = False
    return to_return

def verdict(verdict, score, time=0.0, memory=0.0, testcase=0):
    global requestActive, tempdir
    tempdir.cleanup()
    to_return = {'verdict': verdict, 'score': score, 'time': time, 'memory': memory, 'testcase': testcase}
    if DEBUG: print("Returning", to_return)
    requestActive = False
    return to_return

def limit_memory():
    # Don't limit the stack size
    # resource.setrlimit(resource.RLIMIT_AS, ((BASE_MEMORY_LIMIT + 128) * 1024 * 1024, resource.RLIM_INFINITY))
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

def judge_submission(request):
    global requestActive, tempdir
    # Return a simple testing form the GET method
    if request.method == 'GET':
        return render_template('form.html')

    if requestActive:
        # Don't run multiple requests at once
        return {'error': 'Submission handler busy, please try again in a bit.'}
    requestActive = True
    if DEBUG: print('-' * 60)

    # Get files
    if 'code' not in request.files or not request.files['code']:
        return error('No code file submitted!')
    if 'input' not in request.files or not request.files['input']:
        return error('No input file submitted!')
    if 'output' not in request.files or not request.files['output']:
        return error('No output file submitted!')

    fcode = request.files['code']
    finput = request.files['input']
    fanswer = request.files['output']

    # Initialize the sandbox
    tempdir = tempfile.TemporaryDirectory()

    print(tempdir.name)

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
        compiled_filename = 'code.py'
        fcode.save(tempdir.name + '/code.py')
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
    wall_limit = BASE_TIME_LIMIT * 1.5
    mem_limit = BASE_MEMORY_LIMIT
    process = None
    finput = open(tempdir.name + '/input.in.txt', 'r')
    foutput = open(tempdir.name + '/output.out.txt', 'w')
    ferror = open(tempdir.name + '/error.err.txt', 'w')
    time_args = ['/usr/bin/time', '-f', 'metadata %e %U %S %M', '-o', tempdir.name + '/meta.info.txt', '--quiet']
    # subprocess.run(['ulimit', '-s', '65536'])
    # subprocess.run(['ulimit', '-a'])
    try:
        if request.form['type'] == 'java':
            time_limit += 1
            wall_limit += 1.5
            mem_limit += 16
            process = psutil.Popen(time_args + ['java', '-Xmx128M', '-Xss64M', compiled_filename], preexec_fn=limit_memory,
                                     cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        elif request.form['type'] == 'cpp':
            time_limit += 0
            wall_limit += 0
            mem_limit += 0
            process = psutil.Popen(time_args + ['./code'], preexec_fn=limit_memory,
                                       cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        elif request.form['type'] == 'python':
            time_limit += 2
            wall_limit += 3
            mem_limit += 0
            process = psutil.Popen(time_args + ['python3', 'code.py'], preexec_fn=limit_memory,
                                     cwd=tempdir.name, stdin=finput, stdout=foutput, stderr=ferror, text=True)
        else:
            return error('Invalid submission file type!')
        process.wait(wall_limit)
    except psutil.TimeoutExpired:
        # Kill the process and return a TLE verdict, along with an estimate of the max memory used
        # The estimate takes the sum of the memory used by all child processes, and adds it to the main process
        memory = round((sum([p.memory_info().rss for p in process.children()]) + process.memory_info().rss) / 1024 / 1024, 1)
        memory = min(memory, (mem_limit + 16 if SHOW_BORDER else mem_limit))
        process.terminate()
        return verdict('TLE', 0, time_limit + (1 if SHOW_BORDER else 0), memory, 1)

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
    time = min(time, time_limit + (1 if SHOW_BORDER else 0))
    wall_time = round(meta_dict['wall'], 2)
    memory = round(meta_dict['mem'], 1)
    memory = min(memory, (mem_limit + 16 if SHOW_BORDER else mem_limit))

    # Did the program TLE?
    if time >= time_limit:
        return verdict('TLE', 0, time, memory, 1)
    # Was it killed by the wall clock?
    elif wall_time >= wall_limit:
        return verdict('TLE', 0, time_limit + (1 if SHOW_BORDER else 0), memory, 1)
    # Did the program MLE?
    elif memory >= mem_limit:
        return verdict('MLE', 0, time, memory, 1)
    # Did the program RE?
    elif process.returncode != 0:
        ferror = open(tempdir.name + '/error.err.txt', 'r')
        # Detect Java memory errors
        if request.form['type'] == 'java' and 'java.lang.OutOfMemoryError' in ferror.read():
            return verdict('MLE', 0, time, (mem_limit + 16 if SHOW_BORDER else mem_limit), 1)
        else:
            return verdict('RE', 0, time, memory, 1)

    # Diff the results, ignoring whitespace issues and carriage returns
    result = subprocess.run(['diff', '--ignore-trailing-space', '--ignore-space-change', '--strip-trailing-cr',
                             tempdir.name + '/output.out.txt', tempdir.name + '/answer.ans.txt'], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        return verdict('WA', 0, time, memory, 1)

    # Correct answer! :D
    return verdict('AC', 1, time, memory, 1)