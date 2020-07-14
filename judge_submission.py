"""
This file contains the code that judges a submission.
Note: This implementation can only handle one submission at a time.
Luckily, there is a queuing system!
"""

import resource
import subprocess
import psutil
import shutil
import rq
from time import time as get_time, sleep

from env_vars import *
from logger import *

job: rq.job


def update_job_status(status):
    job.meta['status'] = status
    job.save_meta()


def do_cleanup(tempdir):
    # Delete the temporary directory
    shutil.rmtree(tempdir)


def verdict(tempdir, verdict_code, score, time=0.0, memory=0.0, testcase=0):
    to_return = {'verdict': verdict_code, 'score': score, 'time': time, 'memory': memory, 'testcase': testcase}
    if PROGRAM_OUTPUT and verdict_code != 'CE':
        # Add program stdout / stderr
        foutput = open(tempdir + '/output.out.txt', 'r')
        to_return['stdout'] = foutput.readlines()
        foutput.close()
        ferror = open(tempdir + '/error.err.txt', 'r')
        to_return['stderr'] = ferror.readlines()
        ferror.close()
    log('Result: ' + str(to_return))
    do_cleanup(tempdir)
    return to_return


def limit_memory():
    # Make sure the stack size is as big as the memory limit
    resource.setrlimit(resource.RLIMIT_STACK, (BASE_MEMORY_LIMIT * 1024 * 1024, resource.RLIM_INFINITY))
    # resource.setrlimit(resource.RLIMIT_AS, ((BASE_MEMORY_LIMIT + 128) * 1024 * 1024, resource.RLIM_INFINITY))


def judge_submission(tempdir, code_filename, code_type):
    global job
    job = rq.get_current_job()
    if DEBUG_LOW:
        log('-' * 60)

    # Compile the code file
    update_job_status('Compiling...')
    if DEBUG:
        log('Compiling ' + code_filename)
    # Remove extension from the filename to determine compiled filename
    compiled_filename, _ = os.path.splitext(code_filename)
    if code_type == 'java':
        # Compile the code
        result = subprocess.run(['javac', tempdir + '/' + code_filename],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return verdict(tempdir, 'CE', 0)
    elif code_type == 'cpp':
        compiled_filename = 'code'
        # Compile the code
        result = subprocess.run(['g++', '-std=c++14', '-O2', '-o', tempdir + '/code', tempdir + '/' + code_filename],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return verdict(tempdir, 'CE', 0)
    elif code_type == 'python':
        # Add two lines at the beginning to allow for deep recursion
        compiled_filename = 'code.new.py'
        fcode_old = open(tempdir + '/' + code_filename, 'r')
        fcode_new = open(tempdir + '/code.new.py', 'w')
        fcode_new.write('import sys\n')
        fcode_new.write('sys.setrecursionlimit(99999999)\n')
        fcode_new.write(fcode_old.read())
        fcode_old.close()
        fcode_new.close()
        # Compile the code
        result = subprocess.run(['python3', '-m', 'py_compile', tempdir + '/code.new.py'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return verdict(tempdir, 'CE', 0)

    # Run the program
    update_job_status('Running on test case ' + str(1))
    if DEBUG:
        log('Running ' + compiled_filename)
    time_limit = BASE_TIME_LIMIT
    mem_limit = BASE_MEMORY_LIMIT
    max_memory_used = 0
    process = None
    finput = open(tempdir + '/input.in.txt', 'r')
    foutput = open(tempdir + '/output.out.txt', 'w')
    ferror = open(tempdir + '/error.err.txt', 'w')
    time_args = ['/usr/bin/time', '-f', 'metadata %e %U %S %M', '-o', tempdir + '/meta.info.txt', '--quiet']
    if code_type == 'java':
        time_limit *= 1.5
        mem_limit += 0
        process = psutil.Popen(time_args + ['java', '-Xmx256M', '-Xss128M', compiled_filename], preexec_fn=limit_memory,
                               cwd=tempdir, stdin=finput, stdout=foutput, stderr=ferror, text=True)
    elif code_type == 'cpp':
        time_limit *= 1
        mem_limit += 0
        process = psutil.Popen(time_args + ['./' + compiled_filename], preexec_fn=limit_memory,
                               cwd=tempdir, stdin=finput, stdout=foutput, stderr=ferror, text=True)
    elif code_type == 'python':
        time_limit *= 2
        mem_limit += 0
        process = psutil.Popen(time_args + ['python3', compiled_filename], preexec_fn=limit_memory,
                               cwd=tempdir, stdin=finput, stdout=foutput, stderr=ferror, text=True)
    # Periodically check on the program, and terminate if program exceeds wall or memory limit
    wall_limit = time_limit + WALL_TIME_EXTENSION
    start_time = get_time()
    while process.poll() is None:
        sleep(CHECK_INTERVAL)
        # Memory estimate takes the sum of the memory used by all child processes, and adds it to the main process
        memory = sum([p.memory_info().rss for p in process.children()]) + process.memory_info().rss
        memory = round(memory / 1024 / 1024, 1)
        memory = min(memory, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))
        max_memory_used = max(memory, max_memory_used)
        if DEBUG_LOW:
            log('[{:.2f}s] mem {}, max_mem {}'.format(round(get_time() - start_time, 2), memory, max_memory_used))
        if get_time() - start_time >= wall_limit:
            if DEBUG_LOW:
                log('Killing program: Wall limit')
            # Kill the process and return a TLE verdict
            process.kill()
            return verdict(tempdir, 'TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), max_memory_used, 1)
        if max_memory_used >= (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit):
            if DEBUG_LOW:
                log('Killing program: Memory limit')
            # Kill the process and return a MLE verdict
            process.kill()
            time = round(get_time() - start_time, 2)
            return verdict(tempdir, 'MLE', 0, time, max_memory_used, 1)
    finput.close()
    foutput.close()
    ferror.close()

    # Process results
    if DEBUG:
        log('Checking answer of ' + compiled_filename)
    fmeta = open(tempdir + '/meta.info.txt', 'r')

    # Parse return of time command
    meta_raw = fmeta.readlines()
    if DEBUG_LOW:
        log('Meta Raw: ' + str(meta_raw))
    if 'metadata' not in meta_raw[0]:
        # Remove debug message (happens with runtime errors)
        meta_raw.pop(0)
    meta_list = list(map(float, meta_raw[0].split()[1:]))
    meta_dict = {'time': meta_list[1] + meta_list[2], 'wall': meta_list[0], 'mem': meta_list[3] / 1024}
    fmeta.close()
    if DEBUG:
        log('Meta: ' + str(meta_dict))

    # Determine time (in ms) and memory (in MB)
    time = round(meta_dict['time'], 2)
    time = min(time, time_limit + (TIME_BORDER if SHOW_BORDER else 0))
    wall_time = round(meta_dict['wall'], 2)
    memory = round(meta_dict['mem'], 1)
    memory = min(memory, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))
    max_memory_used = max(memory, max_memory_used)

    # Did the program TLE?
    if time >= time_limit:
        return verdict(tempdir, 'TLE', 0, time, max_memory_used, 1)
    # Was it killed by the wall clock?
    elif wall_time >= wall_limit:
        return verdict(tempdir, 'TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), max_memory_used, 1)
    # Did the program MLE?
    elif max_memory_used >= mem_limit:
        return verdict(tempdir, 'MLE', 0, time, max_memory_used, 1)
    # Did the program RE?
    elif process.returncode != 0:
        ferror = open(tempdir + '/error.err.txt', 'r')
        # Detect Java memory errors
        if code_type == 'java' and 'java.lang.OutOfMemoryError' in ferror.read():
            if DEBUG_LOW:
                log('Java memory error detected: Treating as MLE')
            ferror.close()
            return verdict(tempdir, 'MLE', 0, time, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit), 1)
        else:
            ferror.close()
            return verdict(tempdir, 'RE', 0, time, max_memory_used, 1)

    # Diff the results, ignoring whitespace issues and carriage returns
    result = subprocess.run(['diff', '--ignore-trailing-space', '--ignore-space-change', '--strip-trailing-cr',
                             tempdir + '/output.out.txt', tempdir + '/answer.ans.txt'], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        return verdict(tempdir, 'WA', 0, time, max_memory_used, 1)

    # Correct answer! :D
    return verdict(tempdir, 'AC', 1, time, max_memory_used, 1)
