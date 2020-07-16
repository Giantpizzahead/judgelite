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
import yaml
import glob
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


def verdict_test(tempdir, verdict_code, score, time=0.0, memory=0.0):
    to_return = {'verdict': verdict_code, 'score': score, 'time': time, 'memory': memory}
    if PROGRAM_OUTPUT > 0 and verdict_code != 'CE':
        # Add program stdout / stderr
        foutput = open(tempdir + '/output.out.txt', 'r')
        to_return['stdout'] = foutput.read(PROGRAM_OUTPUT)
        stdout_size = os.path.getsize(foutput.name)
        if stdout_size > PROGRAM_OUTPUT:
            to_return['stdout'] += '...[{:.2f} MB truncated]'.format((stdout_size - PROGRAM_OUTPUT) / 1024 / 1024)
        foutput.close()
        ferror = open(tempdir + '/error.err.txt', 'r')
        to_return['stderr'] = ferror.read(PROGRAM_OUTPUT)
        stderr_size = os.path.getsize(ferror.name)
        if stderr_size > PROGRAM_OUTPUT:
            to_return['stderr'] += '...[{:.2f} MB truncated]'.format((stderr_size - PROGRAM_OUTPUT) / 1024 / 1024)
        ferror.close()
    return to_return


def verdict_subtask(verdict_code, score, time=0.0, memory=0.0, testcase=1):
    to_return = {'verdict': verdict_code, 'score': score, 'time': time, 'memory': memory, 'testcase': testcase}
    return to_return


def verdict_problem(verdict_code, score, max_score, time=0.0, memory=0.0, testcase=1):
    to_return = {'verdict': verdict_code, 'score': score, 'max_score': max_score,
                 'time': time, 'memory': memory, 'testcase': testcase}
    log('Final verdict: ' + str(to_return))
    return to_return


def limit_memory(mem_limit):
    # Make sure the stack size is as big as the memory limit
    resource.setrlimit(resource.RLIMIT_STACK, (mem_limit * 1024 * 1024, resource.RLIM_INFINITY))
    # resource.setrlimit(resource.RLIMIT_AS, ((mem_limit + 32) * 1024 * 1024, resource.RLIM_INFINITY))


def compile_submission(tempdir, code_filename, code_type):
    """
    Compiles a submission. Returns the filename of the compiled submission (or the main class for java).
    """
    # Remove extension from the filename to determine compiled filename
    compiled_filename, _ = os.path.splitext(code_filename)
    if code_type == 'java':
        # Compile the code
        result = subprocess.run(['javac', tempdir + '/' + code_filename],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return None
    elif code_type == 'cpp':
        compiled_filename = 'code'
        # Compile the code
        result = subprocess.run(['g++', '-std=c++14', '-O2', '-o', tempdir + '/code', tempdir + '/' + code_filename],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return None
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
            return None
    return compiled_filename


def check_results(output_path, answer_path, subtask_name, grader):
    if os.path.getsize(output_path) > MAX_OUTPUT_SIZE * 1024 * 1024:
        # Too large to be correct
        return 0

    if grader == 'diff':
        # Diff the results, ignoring whitespace issues and carriage returns
        diff_result = subprocess.run(['diff', '--ignore-trailing-space', '--ignore-space-change', '--strip-trailing-cr',
                                      output_path, answer_path], stdout=subprocess.DEVNULL)
        if diff_result.returncode != 0:
            return 0
        else:
            return 1
    elif grader == 'custom':
        # TODO: Custom grader
        log('Would now call custom grader with subtask name ' + subtask_name)
        return 0
    else:
        log_error(str(grader) + ' is not a valid grader!')


def run_program(tempdir, input_path, answer_path, subtask_name, problem_info, compiled_filename, code_type):
    time_limit = min(problem_info['time_limit'], MAX_TIME_LIMIT)
    mem_limit = min(problem_info['memory_limit'], MAX_MEMORY_LIMIT)
    max_memory_used = 0
    process = None
    finput = open(input_path, 'r')
    foutput = open(tempdir + '/output.out.txt', 'w')
    ferror = open(tempdir + '/error.err.txt', 'w')
    time_args = ['/usr/bin/time', '-f', 'metadata %e %U %S %M', '-o', tempdir + '/meta.info.txt', '--quiet']
    if code_type == 'java':
        time_limit *= 1.5
        mem_limit += 0
        process = psutil.Popen(time_args + ['java', '-Xmx' + str(mem_limit) + 'M',
                                            '-Xss' + str(mem_limit // 2) + 'M', compiled_filename],
                               preexec_fn=lambda: limit_memory(mem_limit), cwd=tempdir,
                               stdin=finput, stdout=foutput, stderr=ferror, text=True)
    elif code_type == 'cpp':
        time_limit *= 1
        mem_limit += 0
        process = psutil.Popen(time_args + ['./' + compiled_filename], preexec_fn=lambda: limit_memory(mem_limit),
                               cwd=tempdir, stdin=finput, stdout=foutput, stderr=ferror, text=True)
    elif code_type == 'python':
        time_limit *= 2
        mem_limit += 0
        process = psutil.Popen(time_args + ['python3', compiled_filename], preexec_fn=lambda: limit_memory(mem_limit),
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
        if DEBUG_LOWEST:
            log('[{:.2f}s] mem {}, max_mem {}'.format(round(get_time() - start_time, 2), memory, max_memory_used))
        if get_time() - start_time >= wall_limit:
            if DEBUG_LOWEST:
                log('Killing program: Wall limit')
            # Kill the process and return a TLE verdict
            process.kill()
            return verdict_test(tempdir, 'TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), max_memory_used)
        if max_memory_used >= (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit):
            if DEBUG_LOWEST:
                log('Killing program: Memory limit')
            # Kill the process and return a MLE verdict
            process.kill()
            time = round(get_time() - start_time, 2)
            return verdict_test(tempdir, 'MLE', 0, time, max_memory_used)
    finput.close()
    foutput.close()
    ferror.close()

    # Process results
    fmeta = open(tempdir + '/meta.info.txt', 'r')

    # Parse return of time command
    meta_raw = fmeta.readlines()
    if 'metadata' not in meta_raw[0]:
        # Remove debug message (happens with runtime errors)
        meta_raw.pop(0)
    meta_list = list(map(float, meta_raw[0].split()[1:]))
    meta_dict = {'time': meta_list[1] + meta_list[2], 'wall': meta_list[0], 'mem': meta_list[3] / 1024}
    fmeta.close()

    # Determine time (in ms) and memory (in MB)
    time = round(meta_dict['time'], 2)
    time = min(time, time_limit + (TIME_BORDER if SHOW_BORDER else 0))
    wall_time = round(meta_dict['wall'], 2)
    memory = round(meta_dict['mem'], 1)
    memory = min(memory, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))
    max_memory_used = max(memory, max_memory_used)

    if DEBUG_LOWEST:
        # Check the results early to see if they are correct
        result = check_results(tempdir + '/output.out.txt', answer_path, subtask_name, problem_info['grader'])
        log('Answer would get ' + str(result) + ' score')

    # Did the program TLE?
    if time >= time_limit:
        return verdict_test(tempdir, 'TLE', 0, time, max_memory_used)
    # Was it killed by the wall clock?
    elif wall_time >= wall_limit:
        return verdict_test(tempdir, 'TLE', 0, time_limit + (TIME_BORDER if SHOW_BORDER else 0), max_memory_used)
    # Did the program MLE?
    elif max_memory_used >= mem_limit:
        return verdict_test(tempdir, 'MLE', 0, time, max_memory_used)
    # Did the program RE?
    elif process.returncode != 0:
        ferror = open(tempdir + '/error.err.txt', 'r')
        # Detect Java memory errors
        if code_type == 'java' and 'java.lang.OutOfMemoryError' in ferror.read(MAX_OUTPUT_SIZE * 1024 * 1024):
            if DEBUG_LOWEST:
                log('Java memory error detected: Treating as MLE')
            ferror.close()
            return verdict_test(tempdir, 'MLE', 0, time, (mem_limit + MEM_BORDER if SHOW_BORDER else mem_limit))
        else:
            ferror.close()
            return verdict_test(tempdir, 'RE', 0, time, max_memory_used)

    # Check results, and return a verdict
    final_score = check_results(tempdir + '/output.out.txt', answer_path, subtask_name, problem_info['grader'])
    if final_score == 0:
        return verdict_test(tempdir, 'WA', final_score, time, max_memory_used)
    # Anything that is not 0 means a correct answer! :D
    return verdict_test(tempdir, 'AC', final_score, time, max_memory_used)


def run_subtask(tempdir, problem_info, problem_folder, subtask_name, compiled_filename, code_type, test_num):
    if DEBUG_LOW:
        log('Running subtask ' + subtask_name)
    subtask_folder = problem_folder + '/subtasks/' + subtask_name
    score_sum = 0
    min_score = 1
    max_time = 0
    max_memory = 0
    first_wrong = None
    test_inputs = sorted(glob.glob1(subtask_folder, '*.in'))
    for i in range(len(test_inputs)):
        update_job_status('Running test case ' + str(test_num))
        test_num += 1
        test_input = test_inputs[i]
        test_name = test_input[:-3]
        test_output = test_name + '.out'
        run_verdict = run_program(tempdir, subtask_folder + '/' + test_input, subtask_folder + '/' + test_output,
                                  subtask_name, problem_info, compiled_filename, code_type)
        if DEBUG_LOW:
            log('Test ' + test_name + ': ' + str(run_verdict))

        # Update stats
        score_sum += run_verdict['score']
        min_score = min(run_verdict['score'], min_score)
        max_time = max(run_verdict['time'], max_time)
        max_memory = max(run_verdict['memory'], max_memory)

        # If first wrong answer, track results
        if run_verdict['verdict'] != 'AC' and first_wrong is None:
            first_wrong = {**run_verdict, 'testcase': i + 1}

        if min_score == 0 and problem_info['scoring_method'] == 'minimum':
            # Stop early to save processing time
            if first_wrong is not None:
                return verdict_subtask(first_wrong['verdict'], first_wrong['score'], first_wrong['time'],
                                       first_wrong['memory'], first_wrong['testcase'])
            else:
                return verdict_subtask('AC', 0, max_time, max_memory, i + 1)

    # Return verdict
    final_score = 0
    final_verdict = 'AC'
    testcase = len(test_inputs)
    if problem_info['scoring_method'] == 'minimum':
        final_score = min_score
    elif problem_info['scoring_method'] == 'average':
        final_score = score_sum / len(test_inputs)
    if first_wrong is not None:
        final_verdict = first_wrong['verdict']
        testcase = first_wrong['testcase']
    return verdict_subtask(final_verdict, final_score, max_time, max_memory, testcase)


def judge_submission(tempdir, problem_id, code_filename, code_type):
    global job
    job = rq.get_current_job()
    if DEBUG_LOW:
        log('-' * 60)

    # Get problem info
    problem_folder = PROBLEM_INFO_PATH + '/' + problem_id
    problem_info_file = open(problem_folder + '/info.yml', 'r')
    problem_info = yaml.safe_load(problem_info_file)
    problem_info_file.close()
    if DEBUG_LOWEST:
        log(str(problem_info))

    # Compile the code file
    update_job_status('Compiling...')
    if DEBUG_LOW:
        log('Compiling ' + code_filename)
    compile_result = compile_submission(tempdir, code_filename, code_type)
    if compile_result is None:
        # Compile error
        do_cleanup(tempdir)
        return verdict_problem('CE', 0, problem_info['max_points'])
    compiled_filename = compile_result

    # Run problem subtasks
    test_num = 1
    subtask_results = {}
    for i in range(len(problem_info['subtasks'])):
        subtask = problem_info['subtasks'][i]

        # Should this subtask actually be run?
        if 'depends_on' in subtask:
            should_run = True
            for required in subtask['depends_on']:
                if required not in subtask_results:
                    log_error(subtask['name'] + ' has an invalid depends_on list! (' + required + ' not yet evaluated)')
                if subtask_results[required]['score'] == 0:
                    should_run = False
                    break
            if not should_run:
                subtask_results[subtask['name']] = verdict_subtask('SK', 0)
                if DEBUG_LOW:
                    log('Skipping subtask ' + subtask['name'])
                if DEBUG:
                    log('Subtask ' + subtask['name'] + ': ' + str(subtask_results[subtask['name']]))
                test_num += len(glob.glob1(problem_folder + '/subtasks/' + subtask['name'], '*.in'))
                continue

        subtask_result = run_subtask(tempdir, problem_info, problem_folder, subtask['name'],
                                     compiled_filename, code_type, test_num)
        subtask_results[subtask['name']] = subtask_result
        if DEBUG:
            log('Subtask ' + subtask['name'] + ': ' + str(subtask_result))

        test_num += len(glob.glob1(problem_folder + '/subtasks/' + subtask['name'], '*.in'))

    # Calculate final result
    final_verdict = 'AC'
    final_score = 0
    max_time = 0
    max_memory = 0
    curr_testcase = 0
    testcase = -1
    for i in range(len(problem_info['subtasks'])):
        subtask = problem_info['subtasks'][i]
        subtask_result = subtask_results[subtask['name']]
        if (subtask_result['verdict'] != 'AC' and final_verdict == 'AC' and
                (subtask_result['score'] > 0 or 'is_bonus' not in subtask or not subtask['is_bonus'])):
            # Report first wrong verdict as the final verdict, if it's not a bonus subtask
            final_verdict = subtask_result['verdict']
            testcase = curr_testcase + subtask_result['testcase']

        # Calculate metrics
        final_score += subtask_result['score'] * subtask['points']
        if subtask_result['score'] > 0 or 'is_bonus' not in subtask or not subtask['is_bonus']:
            max_time = max(subtask_result['time'], max_time)
            max_memory = max(subtask_result['memory'], max_memory)
            # Add to overall testcase number
            testcase_count = len(glob.glob1(problem_folder + '/subtasks/' + subtask['name'], '*.in'))
            curr_testcase += testcase_count

    # Do some final cleanup
    final_score = round(final_score, 2)
    if testcase == -1:
        testcase = curr_testcase
    do_cleanup(tempdir)
    if final_score > problem_info['max_points']:
        # AC* :O
        final_verdict = 'AC*'

    # Finally, return the result. :)
    return verdict_problem(final_verdict, final_score, problem_info['max_points'], max_time, max_memory, testcase)
