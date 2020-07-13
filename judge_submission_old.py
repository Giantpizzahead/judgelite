'''
This file contains the code that judges a submission.
Note: This implementation can only handle one submission at a time. It will reject other submissions while a
submission is being evaluated. Luckily, the gunicorn server is able to queue up submissions!
'''

import subprocess
import math

from app import DEBUG, SHOW_BORDER
from flask import *
from werkzeug.utils import secure_filename

requestActive = False

def error(msg, log=None):
    global requestActive
    # Cleanup sandbox
    subprocess.run(['./isolate', '--cleanup', '--cg'])
    to_return = {'error': msg}
    if DEBUG:
        print("Returning", to_return)
        if log:
            to_return['log'] = log
    requestActive = False
    return to_return

def verdict(verdict, score, time=0, memory=0, testcase=0):
    global requestActive
    # Cleanup sandbox
    subprocess.run(['./isolate', '--cleanup', '--cg'])
    to_return = {'verdict': verdict, 'score': score, 'time': time, 'memory': memory, 'testcase': testcase}
    if DEBUG: print("Returning", to_return)
    requestActive = False
    return to_return

def judge_submission(request):
    global requestActive
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
    subprocess.run(['./isolate', '--cleanup', '--cg'])
    result = subprocess.run(['./isolate', '--init', '--cg'], capture_output=True)
    if result.returncode != 0:
        print("INIT_FAIL", result.stderr)
        return error('Internal error (If the issue persists, let an officer know. Error code: INIT_FAIL)', result.stderr.decode('utf-8'))
    boxdir = result.stdout.decode('utf-8')[:-1] + '/box'

    # Move input / output files to that temporary directory
    finput.save(boxdir + '/input.in.txt')

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
        fcode.save(boxdir + '/' + code_filename)
        result = subprocess.run(['javac', boxdir + '/' + code_filename])

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    elif request.form['type'] == 'cpp':
        # Save & compile the file
        compiled_filename = 'code'
        fcode.save(boxdir + '/code.cpp')
        result = subprocess.run(['g++', '-std=c++14', '-O2', '-o', boxdir + '/code', boxdir + '/code.cpp'])

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    elif request.form['type'] == 'python':
        # Save & compile the file
        compiled_filename = 'code.py'
        fcode.save(boxdir + '/code.py')
        result = subprocess.run(['python3', '-m', 'py_compile', boxdir + '/code.py'])

        # Handle compile error
        if result.returncode != 0:
            return verdict('CE', 0)
    else:
        return error('Invalid submission file type!')

    # Run the program
    if DEBUG: print("Running", compiled_filename)
    time_limit = -1
    wall_time_limit = -1
    mem_limit = -1
    if request.form['type'] == 'java':
        # The JVM does some really sketch stuff in memory, so the only way to enforce memory limit is to use
        # the Xmx and Xss arguments
        time_limit = 4000
        wall_time_limit = 7500
        mem_limit = 96 + 8
        result = subprocess.run(['./isolate', '--cg', '--processes', '--time=5', '--wall-time=7.5',
                                 '--stdin=input.in.txt', '--stdout=output.out.txt',
                                 '--meta=' + boxdir + '/meta.info.txt', '--run', '--',
                                 '/usr/lib/jvm/java-14-openjdk-amd64/bin/java', '-Xmx96M', '-Xss64M', compiled_filename],
                                capture_output=True)
    elif request.form['type'] == 'cpp':
        time_limit = 3000
        wall_time_limit = 6000
        mem_limit = 96
        result = subprocess.run(['./isolate', '--cg', '--cg-mem=114688', '--time=4', '--wall-time=6',
                                 '--stdin=input.in.txt', '--stdout=output.out.txt',
                                 '--meta=' + boxdir + '/meta.info.txt', '--run', '--', 'code'],
                                capture_output=True)
    elif request.form['type'] == 'python':
        time_limit = 5000
        wall_time_limit = 9000
        mem_limit = 96
        result = subprocess.run(['./isolate', '--cg', '--cg-mem=114688', '--time=6', '--wall-time=9',
                                 '--stdin=input.in.txt', '--stdout=output.out.txt',
                                 '--meta=' + boxdir + '/meta.info.txt', '--run', '--',
                                 '/bin/python3', 'code.py'],
                                capture_output=True)
    else:
        return error('Invalid submission file type!')

    # Check for internal sandbox error
    if result.returncode != 0 and result.returncode != 1:
        return error('Internal error (If the issue persists, let an officer know. Error code: SB_FAIL)', result.stderr.decode('utf-8'))

    # Move answer file to box
    if DEBUG: print("Checking answer of", compiled_filename)

    # Process results
    fanswer.save(boxdir + '/answer.ans.txt')
    fmeta = open(boxdir + '/meta.info.txt')
    # Parse key:value format of fmeta
    meta_dict = dict(map(str.strip, line.split(':', 1)) for line in fmeta.readlines())
    if DEBUG: print("Meta: " + str(meta_dict))

    # Determine time (in ms) and memory (in MB)
    time = -1
    wall_time = -1
    if 'time' in meta_dict:
        time = math.ceil(float(meta_dict['time']) * 1000)
        time = min(time, time_limit + (1000 if SHOW_BORDER else 0))
    if 'time-wall' in meta_dict:
        wall_time = math.ceil(float(meta_dict['time-wall']) * 1000)
    memory = -1
    if 'max-rss' in meta_dict:
        memory = math.ceil(int(meta_dict['cg-mem']) / 1024 * 10) / 10
        memory = min(memory, (112 if SHOW_BORDER else mem_limit))

    # Did the program TLE?
    if time >= time_limit:
        return verdict('TLE', 0, time, memory, 1)
    # Was it killed by the wall clock?
    elif wall_time >= wall_time_limit:
        return verdict('TLE', 0, time_limit + (1000 if SHOW_BORDER else 0), memory, 1)
    # Did the program MLE?
    elif memory >= mem_limit:
        return verdict('MLE', 0, time, memory, 1)
    # Did the program RE?
    elif result.returncode == 1:
        # Detect Java memory errors
        result_stderr = result.stderr.decode('utf-8')
        if request.form['type'] == 'java' and 'java.lang.OutOfMemoryError' in result_stderr:
            return verdict('MLE', 0, time, (112 if SHOW_BORDER else mem_limit), 1)
        else:
            return verdict('RE', 0, time, memory, 1)

    # Diff the results, ignoring whitespace issues and carriage returns
    result = subprocess.run(['diff', '--ignore-trailing-space', '--ignore-space-change', '--strip-trailing-cr',
                             boxdir + '/output.out.txt', boxdir + '/answer.ans.txt'], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        return verdict('WA', 0, time, memory, 1)

    # Correct answer! :D
    return verdict('AC', 1, time, memory, 1)