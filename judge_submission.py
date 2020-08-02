"""
This file contains the code that judges a submission.
Note: This implementation can only handle one submission at a time. Currently, the queuing system from RQ
is used to achieve a first come, first served structure.
"""

import subprocess
import shutil
import rq
import yaml
import glob
import requests

from env_vars import *
from logger import *
from manage_redis import *

job: rq.job


def remove_dir(target_dir: str) -> None:
    """Deletes a directory (and everything in it).

    :param target_dir - The directory to delete.
    """
    shutil.rmtree(target_dir)


def verdict_test(tempdir, verdict_code, score, time=0.0, memory=0.0):
    to_return = {'verdict': verdict_code, 'score': score, 'time': round(time * 1000), 'memory': memory}
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


def verdict_compile_error(verdict_code, score, max_score, error):
    final_verdict = {'verdict': verdict_code, 'score': score, 'max_score': max_score, 'error': error}
    log('Final verdict: ' + str(final_verdict))
    return {'status': 'compile_error', 'final_score': score, 'max_score': max_score, 'error': error}


def verdict_problem(verdict_code, score, max_score, time=0.0, memory=0.0, testcase=1):
    final_verdict = {'verdict': verdict_code, 'score': score, 'max_score': max_score,
                     'time': time, 'memory': memory, 'testcase': testcase}
    log('Final verdict: ' + str(final_verdict))

    to_return = job.meta
    to_return['status'] = 'done'
    to_return['final_score'] = score
    return to_return


def verdict_error(msg):
    to_return = {'status': 'internal_error', 'error': msg}
    log('Returning error: ' + str(to_return))
    return to_return


def isolate_init(tempdir: str, problem_folder: str, code_filename: str) -> [str, None]:
    """Initializes the isolate sandbox, and moves all the required files there. Also deletes the temporary directory.

    :param tempdir: The path to the temporary directory that contains the code file.
    :param problem_folder: The path to the folder containing the problem.
    :param code_filename: The code file's name, including the extension.
    :return: The path to the isolate sandbox, or None if the initialization failed.
    """
    # Initialize the sandbox
    isolate_cleanup()
    init_result = subprocess.run(['misc/isolate', '--init', '--cg'], capture_output=True)
    if init_result.returncode != 0:
        # Error initializing sandbox
        error_log = init_result.stderr.decode('utf-8')
        log_error('Isolate init failed! Log: ' + error_log)
        return None
    isolate_loc = init_result.stdout.decode('utf-8')[:-1] + '/box'
    # Move files to the sandbox
    shutil.move(tempdir + '/' + code_filename, isolate_loc + '/' + code_filename)
    shutil.copytree(problem_folder + '/subtasks', isolate_loc + '/subtasks', copy_function=only_copy_input)
    # Delete the temporary directory
    remove_dir(tempdir)
    return isolate_loc


def only_copy_input(src: str, dest: str) -> None:
    if src[-3:] == '.in':
        shutil.copy2(src, dest)


def isolate_cleanup() -> None:
    """Cleans up the isolate sandbox."""
    subprocess.run(['misc/isolate', '--cleanup', '--cg'])


def compile_submission(isolate_dir: str, code_filename: str, code_type: str) -> (bool, str):
    """Compiles a submission in the isolate directory.

    :param isolate_dir: The location of the isolate sandbox.
    :param code_filename: The name of the code file (with extension).
    :param code_type: The language that the code is written in.
    :return: A tuple with 2 values. The 1st is a boolean representing whether or not the compilation was
        successful. The 2nd is either the compiled filename (main class for Java) if the compilation was
        successful, or an explanation as to why the compilation was not successful.
    """
    compile_args = None
    # Remove extension from the filename to determine compiled filename
    compiled_filename, _ = os.path.splitext(code_filename)
    if code_type == 'java':
        compile_args = ['/usr/lib/jvm/java-14-openjdk-amd64/bin/javac', code_filename]
    elif code_type == 'cpp':
        compiled_filename = 'code'
        compile_args = ['/usr/bin/g++', '-B', '/usr/bin', '-std=c++17', '-O2', '-o', 'code', code_filename]
    elif code_type == 'python':
        # Add two lines at the beginning to allow for deep recursion
        compiled_filename = 'code.new.py'
        fcode_old = open(isolate_dir + '/' + code_filename, 'r')
        fcode_new = open(isolate_dir + '/' + 'code.new.py', 'w')
        fcode_new.write('import sys\n')
        fcode_new.write('sys.setrecursionlimit(99999999)\n')
        fcode_new.write(fcode_old.read())
        fcode_old.close()
        fcode_new.close()
        compile_args = ['/bin/python3', '-m', 'pylint', '--errors-only', 'code.new.py']

    isolate_args = ['misc/isolate', '--run', '--cg', '--processes=50', '--silent',
                    '--time=' + str(COMPILE_TIME_LIMIT), '--wall-time=' + str(COMPILE_TIME_LIMIT),
                    '--cg-mem=' + str(COMPILE_MEMORY_LIMIT * 1024), '--chdir=/box', '--stdout=error.err.txt',
                    '--stderr-to-stdout', '--fsize=' + str(MAX_COMPILE_SIZE * 1024), '--']
    if DEBUG_LOWEST:
        log('$' + ' '.join(isolate_args + compile_args))

    # Run isolate
    process = subprocess.run(isolate_args + compile_args)

    if process.returncode != 0:
        # Compile error of some kind
        ferror = open(isolate_dir + '/error.err.txt', 'r')
        error = ferror.read(COMPILE_ERROR_OUTPUT + 20)
        # Cleanup error log by replacing placeholder filenames / removing module
        if code_type == 'python':
            error = error.replace('************* Module code.new\n', '')
            error = error.replace('code.new.py', code_filename)
        error = error[:COMPILE_ERROR_OUTPUT]
        # Notify user if output was truncated
        stderr_size = os.path.getsize(ferror.name)
        if stderr_size > COMPILE_ERROR_OUTPUT:
            error += '\n...[output truncated]'
        elif stderr_size == 0:
            error = '[Empty error log... maybe the compiler ran for too long, or ran out of memory?]'
        return False, error

    # Compiled successfully
    return True, compiled_filename


def check_results(output_path: str, answer_path: str, subtask_name: str, checker: str) -> float:
    """Checks the answer of the program using the specified checker.

    :param output_path: The path to the program's output file.
    :param answer_path: The path to the answer file (the correct output).
    :param subtask_name: The name of the subtask being graded. Passed to a custom checker as extra info.
    :param checker: The checker to use.
    :return: The score that the program got (a float between 0 and 1).
    """
    if checker == 'diff':
        # Diff the results, ignoring whitespace issues and carriage returns
        diff_result = subprocess.run(['diff', '--ignore-trailing-space', '--strip-trailing-cr',
                                      output_path, answer_path], stdout=subprocess.DEVNULL)
        if diff_result.returncode != 0:
            return 0
        else:
            return 1
    elif checker == 'custom':
        log('Would now call custom checker with subtask name ' + subtask_name)
        return 0
    else:
        log_error(str(checker) + ' is not a valid checker!')


def run_testcase(isolate_dir, input_path, answer_path, subtask_name, problem_info, compiled_filename, code_type):
    time_limit = min(problem_info['time_limit'], MAX_TIME_LIMIT)
    mem_limit = min(problem_info['memory_limit'], MAX_MEMORY_LIMIT)
    # Setup arguments for isolate
    code_args = None
    if code_type == 'java':
        time_limit *= 1.5
        code_args = ['/usr/lib/jvm/java-14-openjdk-amd64/bin/java',
                     '-Xmx' + str(mem_limit) + 'M', '-Xss' + str(mem_limit // 2) + 'M', compiled_filename]
    elif code_type == 'cpp':
        time_limit *= 1
        code_args = ['./' + compiled_filename]
    elif code_type == 'python':
        time_limit *= 2
        code_args = ['/bin/python3', compiled_filename]
    isolate_args = ['misc/isolate', '--run', '--cg', '--processes=50', '--silent', '--time=' + str(time_limit),
                    '--wall-time=' + str(time_limit + WALL_TIME_EXTENSION), '--cg-mem=' + str(mem_limit * 1024),
                    '--chdir=/box', '--stdin=' + input_path, '--stdout=output.out.txt', '--stderr=error.err.txt',
                    '--meta=' + isolate_dir + '/../meta.info.txt', '--fsize=' + str(MAX_OUTPUT_SIZE * 1024), '--']
    if DEBUG_LOWEST:
        log('$' + ' '.join(isolate_args + code_args))

    # Run isolate
    process = subprocess.run(isolate_args + code_args)

    # Process results
    fmeta = open(isolate_dir + '/../meta.info.txt', 'r')
    meta_raw = fmeta.readlines()
    # noinspection PyTypeChecker
    meta_dict = dict(map(str.strip, line.split(':', 1)) for line in meta_raw)
    if DEBUG_LOWEST:
        log('Meta: ' + str(meta_dict))
    fmeta.close()

    # Determine time (in ms) and memory (in MB)
    time = round(float(meta_dict['time']), 3)
    time = min(time, time_limit)
    wall_time = round(float(meta_dict['time-wall']), 2)
    memory = round(int(meta_dict['cg-mem']) / 1024, 1)
    memory = min(memory, mem_limit)

    if DEBUG_LOWEST:
        # Check the results early to see if they are correct
        result = check_results(isolate_dir + '/output.out.txt', answer_path, subtask_name, problem_info['checker'])
        log('Answer would get ' + str(result) + ' score')

    # Did the program TLE?
    if time >= time_limit or wall_time >= time_limit + WALL_TIME_EXTENSION:
        return verdict_test(isolate_dir, 'TLE', 0, time_limit, memory)
    # Did the program MLE?
    elif memory >= mem_limit:
        return verdict_test(isolate_dir, 'MLE', 0, time, memory)
    # Did the program RE?
    elif process.returncode != 0:
        ferror = open(isolate_dir + '/error.err.txt', 'r')
        # Detect Java memory errors
        if code_type == 'java' and 'java.lang.OutOfMemoryError' in ferror.read(MAX_OUTPUT_SIZE * 1024 * 1024):
            if DEBUG_LOWEST:
                log('Java memory error detected: Treating as MLE')
            ferror.close()
            return verdict_test(isolate_dir, 'MLE', 0, time, mem_limit)
        else:
            ferror.close()
            return verdict_test(isolate_dir, 'RE', 0, time, memory)

    # Check results, and return a verdict
    if not os.path.isfile(answer_path):
        if 'fill_missing_output' in problem_info and problem_info['fill_missing_output']:
            # Fill output file with the program's output
            if DEBUG_LOW:
                log('Filling output file ' + str(answer_path) + ' with program output')
            shutil.copy(isolate_dir + '/output.out.txt', answer_path)
        else:
            log_error('Missing answer file ' + str(answer_path) + '!!!')
    final_score = check_results(isolate_dir + '/output.out.txt', answer_path, subtask_name, problem_info['checker'])
    if final_score == 0:
        return verdict_test(isolate_dir, 'WA', final_score, time, memory)
    # Anything that is not 0 means a correct answer! :D
    return verdict_test(isolate_dir, 'AC', final_score, time, memory)


def run_subtask(isolate_dir, problem_info, problem_folder, subtask_info, compiled_filename, code_type, subtask_i):
    subtask_name = subtask_info['name']
    if DEBUG_LOW:
        log('Running subtask ' + subtask_name)
    subtask_folder = problem_folder + '/subtasks/' + subtask_name
    num_samples = 0
    if 'num_samples' in subtask_info:
        num_samples = subtask_info['num_samples']
    score_sum = 0
    min_score = 1
    max_time = 0
    max_memory = 0
    first_wrong = None
    test_inputs = sorted(glob.glob1(subtask_folder, '*.in'))
    for test_i in range(len(test_inputs)):
        test_input = test_inputs[test_i]
        test_name = test_input[:-3]
        test_output = test_name + '.out'
        run_verdict = run_testcase(isolate_dir, 'subtasks/' + subtask_name + '/' + test_input,
                                   subtask_folder + '/' + test_output,
                                   subtask_name, problem_info, compiled_filename, code_type)
        if DEBUG_LOW:
            log('Test ' + test_name + ': ' + str(run_verdict))

        # Update stats
        score_sum += run_verdict['score']
        min_score = min(run_verdict['score'], min_score)
        max_time = max(run_verdict['time'], max_time)
        max_memory = max(run_verdict['memory'], max_memory)

        # Update job meta, but don't reveal any bonus verdicts
        if problem_info['scoring_method'] in ['average', 'average_stop']:
            job.meta['score'][subtask_i] = score_sum / len(test_inputs) * subtask_info['score']
        if run_verdict['verdict'] == 'AC' or 'is_bonus' not in subtask_info or not subtask_info['is_bonus']:
            job.meta['subtasks'][subtask_i][test_i][0] = run_verdict['verdict']
            job.meta['subtasks'][subtask_i][test_i][1] = run_verdict['time']
            job.meta['subtasks'][subtask_i][test_i][2] = run_verdict['memory']
        else:
            job.meta['subtasks'][subtask_i][test_i][0] = 'SK'
        job.save_meta()

        # If first wrong answer, track results
        if run_verdict['verdict'] != 'AC' and first_wrong is None:
            first_wrong = {**run_verdict, 'testcase': test_i + 1}
            if test_i < num_samples or problem_info['scoring_method'] == 'average_stop':
                # Stop early (failed samples or average_stop method)
                score_to_return = 0
                if problem_info['scoring_method'] == 'minimum':
                    score_to_return = min_score
                elif problem_info['scoring_method'] in ['average', 'average_stop']:
                    score_to_return = score_sum / len(test_inputs)
                if DEBUG_LOWEST:
                    log('Stopping early due to failed sample or average_stop scoring method')
                # Update job meta
                for j in range(test_i+1, len(test_inputs)):
                    job.meta['subtasks'][subtask_i][j][0] = 'SK'
                job.save_meta()
                return verdict_subtask(first_wrong['verdict'], score_to_return, first_wrong['time'],
                                       first_wrong['memory'], first_wrong['testcase'])

        # If score is already known to be 0, stop early to save processing time
        if min_score == 0 and problem_info['scoring_method'] == 'minimum':
            if DEBUG_LOWEST:
                log('Stopping early due to minimum scoring method')
            # Update job meta
            for j in range(test_i + 1, len(test_inputs)):
                job.meta['subtasks'][subtask_i][j][0] = 'SK'
            job.save_meta()
            if first_wrong is not None:
                return verdict_subtask(first_wrong['verdict'], first_wrong['score'], first_wrong['time'],
                                       first_wrong['memory'], first_wrong['testcase'])
            else:
                return verdict_subtask('AC', 0, max_time, max_memory, test_i + 1)

    # Return verdict
    final_score = 0
    final_verdict = 'AC'
    testcase = len(test_inputs)
    if problem_info['scoring_method'] == 'minimum':
        final_score = min_score
    elif problem_info['scoring_method'] in ['average', 'average_stop']:
        final_score = score_sum / len(test_inputs)
    job.meta['score'][subtask_i] = final_score * subtask_info['score']
    job.save_meta()
    if first_wrong is not None:
        final_verdict = first_wrong['verdict']
        testcase = first_wrong['testcase']
    return verdict_subtask(final_verdict, final_score, max_time, max_memory, testcase)


def judge_submission(tempdir, problem_id, code_filename, code_type, username):
    global job
    job = rq.get_current_job()
    if DEBUG_LOWEST:
        log('-' * 60)

    # Get problem info
    problem_folder = PROBLEM_INFO_PATH + '/' + problem_id
    problem_info_file = open(problem_folder + '/info.yml', 'r')
    problem_info = yaml.safe_load(problem_info_file)
    problem_info_file.close()
    if DEBUG_LOWEST:
        log(str(problem_info))

    # Put problem info into job meta
    job.meta['status'] = 'judging'
    job.meta['score'] = [0 for _ in range(len(problem_info['subtasks']))]
    job.meta['is_bonus'] = [0 for _ in range(len(problem_info['subtasks']))]
    job.meta['max_score'] = problem_info['max_score']
    job.meta['subtasks'] = []
    for i in range(len(problem_info['subtasks'])):
        subtask = problem_info['subtasks'][i]
        subtask_folder = problem_folder + '/subtasks/' + subtask['name']
        test_inputs = glob.glob1(subtask_folder, '*.in')
        subtask_arr = [['--', 0, 0] for _ in range(len(test_inputs))]
        job.meta['subtasks'].append(subtask_arr)
        if 'is_bonus' in subtask and subtask['is_bonus']:
            job.meta['is_bonus'][i] = 1
    job.save_meta()

    # Initialize the isolate sandbox / move code file there
    isolate_dir = isolate_init(tempdir, problem_folder, code_filename)
    if isolate_dir is None:
        return verdict_error('INIT_FAIL')

    # Compile the code file
    if DEBUG_LOW:
        log('Compiling ' + code_filename)
    compile_result = compile_submission(isolate_dir, code_filename, code_type)
    if not compile_result[0]:
        # Compile error
        isolate_cleanup()
        return verdict_compile_error('CE', 0, problem_info['max_score'], compile_result[1])
    compiled_filename = compile_result[1]

    # Run problem subtasks
    test_num = 1
    subtask_results = {}
    for i in range(len(problem_info['subtasks'])):
        subtask = problem_info['subtasks'][i]

        # Should this subtask actually be run?
        if 'depends_on' in subtask and subtask['depends_on'] is not None:
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
                num_tests = len(glob.glob1(problem_folder + '/subtasks/' + subtask['name'], '*.in'))
                test_num += num_tests
                # Update job meta
                for j in range(num_tests):
                    job.meta['subtasks'][i][j][0] = 'SK'
                job.save_meta()
                continue

        subtask_result = run_subtask(isolate_dir, problem_info, problem_folder, subtask,
                                     compiled_filename, code_type, i)
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
        final_score += subtask_result['score'] * subtask['score']
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
    if final_score > problem_info['max_score']:
        # AC* :O
        final_verdict = 'AC*'
    
    # Add submission result to Redis database
    with open(isolate_dir + '/' + code_filename, 'r') as fcode:
        source_code = fcode.read()
        redis_add_submission(problem_info['problem_id'], username, final_score, job.get_id(), source_code)

    # Send POST request to webhook URL
    if WEBHOOK_URL is not None:
        try:
            requests.post(WEBHOOK_URL, data={'problem_id': problem_info['problem_id'], 'username': username,
                                             'score': final_score, 'job_id': job.get_id()}, timeout=10)
        except Exception as e:
            return verdict_error('WEBHOOK_FAIL')

    # Finally, return the result. :)
    isolate_cleanup()
    return verdict_problem(final_verdict, final_score, problem_info['max_score'], max_time, max_memory, testcase)
