"""
This python script contains the main Flask app.
"""

import tempfile
import yaml

from werkzeug.utils import secure_filename
from flask import *
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from worker import conn

from env_vars import *
from logger import *
from judge_submission import judge_submission

app = Flask(__name__)
# Set max uploaded code file size
app.config['MAX_CONTENT_LENGTH'] = (MAX_CODE_SIZE + 1) * 1024

q = Queue(connection=Redis())


def error(msg):
    return {'status': 'fail', 'error': msg}, 400


@app.route('/', methods=['GET'])
def show_form():
    # Return a simple testing form for the GET method
    return render_template('form.html', filesize_limit=round(app.config['MAX_CONTENT_LENGTH'] / 1024 - 1))


@app.route('/status', methods=['GET'])
def get_status():
    if 'job_id' not in request.args:
        return error('No job id provided!')
    try:
        Job.fetch(request.args['job_id'], connection=conn)
    except NoSuchJobError:
        return error('Job not found!')
    return render_template('status.html', job_id=request.args['job_id'])


@app.route('/api/submit', methods=['POST'])
def handle_submission():
    # Validate request
    problems_file = open(PROBLEM_INFO_PATH + '/problems.yml', 'r')
    problems = yaml.safe_load(problems_file)
    problems_file.close()
    if not request.form:
        return error('Empty request form (maybe invalid code file?)')
    if 'problem_id' not in request.form or request.form['problem_id'] not in problems:
        return error('Invalid problem ID!')
    if 'type' not in request.form:
        return error('No submission language!')
    if request.form['type'] not in ['java', 'cpp', 'python']:
        return error('Invalid submission language!')
    if 'code' not in request.files or not request.files['code']:
        return error('No code file submitted!')
    sec_filename = secure_filename(request.files['code'].filename)
    if sec_filename in ['', 'input.in.txt', 'output.out.txt', 'answer.ans.txt', 'code.new.py']:
        return error('Invalid code filename!')
    code_filename, code_extension = os.path.splitext(sec_filename)
    if request.form['type'] == 'java' and code_extension != '.java':
        return error('Missing .java file extension!')

    # Make a temporary directory / save files there
    tempdir = tempfile.mkdtemp(prefix='judge-')
    request.files['code'].save(tempdir + '/' + code_filename + code_extension)

    # Enqueue the job
    # return judge_submission(tempdir, sec_filename, request.form['type'])
    job = q.enqueue_call(func=judge_submission, timeout=60,
                         ttl=RESULT_TTL, result_ttl=RESULT_TTL, failure_ttl=RESULT_TTL,
                         args=(tempdir, request.form['problem_id'], sec_filename, request.form['type']))
    job.meta['status'] = 'queued'
    job.save_meta()
    if DEBUG_LOWEST:
        log('New job id: {}'.format(job.get_id()))

    # Return submitted, along with the job id
    return {'status': 'success', 'job_id': job.get_id()}


@app.route('/api/status/<job_key>', methods=['GET'])
def get_results(job_key):
    try:
        job = Job.fetch(job_key, connection=conn)
    except NoSuchJobError:
        return {'status': 'internal_error', 'error': 'NO_SUCH_JOB', 'job_id': job_key}, 200
    if job.is_queued:
        return job.meta, 202
    elif job.is_finished:
        return job.result, 200
    elif job.is_failed:
        return {'status': 'internal_error', 'error': 'JOB_FAILED', 'job_id': job_key}, 200
    else:
        return job.meta, 202


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
