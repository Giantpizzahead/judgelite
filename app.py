"""
This python script contains the main Flask app.

TODO:
 Increase security by running the program as a non-privileged user
 Add support for multiple test cases (use local filesystem for now)
  - Use a dictionary with the 'select multiple files' option, map .in files to .out files
  - Evaluate test cases in alphabetical order
 Look into async / threaded workers for gunicorn
"""

import tempfile

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
# Set max uploaded file size
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

q = Queue(connection=Redis())


def error(msg):
    return {'error': msg}


@app.route('/', methods=['GET', 'POST'])
def handle_submission():
    if request.method == 'GET':
        # Return a simple testing form for the GET method
        return render_template('form.html', mem_limit=BASE_MEMORY_LIMIT, time_limit=BASE_TIME_LIMIT,
                               filesize_limit=round(app.config['MAX_CONTENT_LENGTH'] / 1024 / 1024))
    else:
        # Validate request
        if 'type' not in request.form:
            return error('No submission language!')
        if request.form['type'] not in ['java', 'cpp', 'python']:
            return error('Invalid submission language!')
        if 'code' not in request.files or not request.files['code']:
            return error('No code file submitted!')
        if 'input' not in request.files or not request.files['input']:
            return error('No input file submitted!')
        if 'output' not in request.files or not request.files['output']:
            return error('No output file submitted!')
        sec_filename = secure_filename(request.files['code'].filename)
        if sec_filename in ['', 'input.in.txt', 'output.out.txt', 'answer.ans.txt', 'code.new.py']:
            return error('Invalid code filename!')
        code_filename, code_extension = os.path.splitext(sec_filename)
        if request.form['type'] == 'java' and code_extension != '.java':
            return error('Missing .java file extension!')

        # Make a temporary directory / save files there
        tempdir = tempfile.mkdtemp(prefix='judge-')
        request.files['code'].save(tempdir + '/' + code_filename + code_extension)
        request.files['input'].save(tempdir + '/input.in.txt')
        request.files['output'].save(tempdir + '/answer.ans.txt')

        # Enqueue the job
        # return judge_submission(tempdir, sec_filename, request.form['type'])
        job = q.enqueue_call(func=judge_submission, timeout=60, ttl=300, result_ttl=180, failure_ttl=180,
                             args=(tempdir, sec_filename, request.form['type']))
        job.meta['status'] = 'Initializing...'
        job.save_meta()
        if DEBUG_LOW:
            log('New job id: {}'.format(job.get_id()))

        # Return submitted, along with the job id
        return redirect(url_for('.get_status', job_id=job.get_id()))


@app.route('/status', methods=['GET'])
def get_status():
    if 'job_id' not in request.args:
        return redirect(url_for('.handle_submission'))
    try:
        Job.fetch(request.args['job_id'], connection=conn)
    except NoSuchJobError:
        return redirect(url_for('.handle_submission'))
    return render_template('status.html', job_id=request.args['job_id'])


@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    try:
        job = Job.fetch(job_key, connection=conn)
    except NoSuchJobError:
        return error('Job not found!'), 404

    if job.is_queued:
        return {'status': 'In queue (position {} of {})'.format(job.get_position() + 1, q.count)}, 202
    if job.is_finished:
        return job.result, 200
    else:
        return job.meta, 202


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
