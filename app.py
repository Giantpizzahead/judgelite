"""
This python script contains the main Flask app.
"""
import random
import string
import tempfile
import yaml
import markdown

from werkzeug.utils import secure_filename
from flask import *
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

from logger import *
from manage_redis import *
from judge_submission import judge_submission

app = Flask(__name__)
app.secret_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(24))
# Set max uploaded code file size
app.config['MAX_CONTENT_LENGTH'] = (MAX_CODE_SIZE + 1) * 1024

q = Queue(connection=REDIS_CONN)


"""
Client webpage methods
"""


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory('images', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET'])
def show_index():
    is_admin = 'admin' in session
    return render_template('index.html', is_admin=is_admin)


@app.route('/problem_list', methods=['GET'])
def show_problem_list():
    return render_template('problem_list.html', problem_list=get_problem_list())


@app.route('/view_problem/<problem_id>', methods=['GET'])
def view_problem(problem_id):
    return render_template('view_problem.html', problem=get_problem_info(problem_id))


@app.route('/test_form', methods=['GET'])
def show_form():
    # Return a simple testing form for the GET method
    return render_template('form.html', filesize_limit=round(app.config['MAX_CONTENT_LENGTH'] / 1024 - 1))


@app.route('/status', methods=['GET'])
def show_status():
    if 'job_id' not in request.args:
        return json_error('No job id provided!')
    try:
        Job.fetch(request.args['job_id'], connection=REDIS_CONN)
    except NoSuchJobError:
        return json_error('Job not found!')
    return render_template('status.html', job_id=request.args['job_id'])


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'GET':
        if 'admin' not in session:
            return render_template('login.html')
        else:
            return redirect('/')
    if not request.form or 'secret-key' not in request.form:
        return render_template('login.html')
    if request.form['secret-key'] != SECRET_KEY:
        return render_template('login.html', error='Incorrect secret key!')
    # Login successful
    session['admin'] = True
    return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('admin', None)
    return redirect('/')


"""
API methods
"""


def json_error(msg):
    return {'error': msg}, 400


def is_valid_problem_id(problem_id):
    problem_list = get_problem_list()
    valid_problem = False
    for group in problem_list['groups']:
        for problem in group['problems']:
            if problem['id'] == problem_id:
                valid_problem = True
    return valid_problem


def change_md_to_html(md_file, default):
    raw: str
    if os.path.isfile(md_file):
        with open(md_file, 'r') as mdf:
            raw = mdf.read()
            raw = markdown.markdown(raw,
                                    extensions=['fenced_code', 'nl2br', 'mdx_math'],
                                    extension_configs={
                                        'mdx_math': {
                                            'enable_dollar_delimiter': True
                                        }
                                    })
    else:
        raw = default
    return raw


@app.route('/api/get_submissions', methods=['GET'])
def get_submissions():
    return str(redis_get_all_submissions())


@app.route('/api/get_submission_source/<i>', methods=['GET'])
def get_submission_source(i):
    source_code = redis_get_submission_source(i)
    if source_code is None:
        return '<code>Invalid submission index!</code>'
    else:
        source_code = source_code.decode('utf-8').replace('<', '&lt;').replace('>', '&gt;')
        return '<code><pre>{}</pre></code>'.format(source_code)


@app.route('/api/get_problem_list', methods=['GET'])
def get_problem_list():
    # Get problem list
    problem_file = open('{}/problems.yml'.format(PROBLEM_INFO_PATH), 'r')
    problem_data = yaml.safe_load(problem_file)
    problem_file.close()

    # Only return problems that are active
    active_groups = []
    for group in problem_data['groups']:
        if group['status'] == 'down':
            continue
        # This group is active; add to active problem data
        current_group = {'id': group['id'], 'name': group['name'], 'problems': []}
        for problem in group['problems']:
            if problem['status'] == 'down':
                continue
            # Problem is not down; add to active group
            current_group['problems'].append({'id': problem['id'], 'name': problem['name'],
                                              'blurb': problem['blurb'] if 'blurb' in problem else '',
                                              'difficulty': problem['difficulty'] if 'difficulty' in problem else ''})
        active_groups.append(current_group)
    
    # Return the active groups / problems
    return {'groups': active_groups}


@app.route('/api/get_problem_info/<problem_id>', methods=['GET'])
def get_problem_info(problem_id):
    # Make sure there is a problem with the given id
    if not is_valid_problem_id(problem_id):
        return json_error('Invalid problem ID!')
    
    # Get problem info
    problem_info_file = open('{}/{}/info.yml'.format(PROBLEM_INFO_PATH, problem_id), 'r')
    pinfo = yaml.safe_load(problem_info_file)
    problem_info_file.close()

    # Get problem statement (if there is one)
    problem_statement = change_md_to_html('{}/{}/statement.md'.format(PROBLEM_INFO_PATH, problem_id),
                                          '<p>No problem statement available.</p>')

    # Get hints (if there are any)
    hints = change_md_to_html('{}/{}/hints.md'.format(PROBLEM_INFO_PATH, problem_id), 'No hints available.')

    # Return only the info that the client needs to know about the problem
    return {'id': pinfo['problem_id'], 'name': pinfo['problem_name'], 'time_limit': pinfo['time_limit'],
            'memory_limit': pinfo['memory_limit'], 'max_score': pinfo['max_score'],
            'statement': problem_statement, 'hints': hints,
            'difficulty': pinfo['difficulty'] if 'difficulty' in pinfo else ''}


@app.route('/api/submit', methods=['POST'])
def handle_submission():
    # Validate request
    if not request.form:
        return json_error('Empty request form (maybe invalid code file?)')
    # Secret key needed if not admin
    if 'admin' not in session and ('secret-key' not in request.form or request.form['secret-key'] != SECRET_KEY):
        return json_error('You are not authorized to make submissions (must be admin or provide the right secret key)!')
    if 'problem_id' not in request.form or not is_valid_problem_id(request.form['problem_id']):
        return json_error('Invalid problem ID!')
    if 'type' not in request.form:
        return json_error('No submission language!')
    if request.form['type'] not in ['java', 'cpp', 'python']:
        return json_error('Invalid submission language!')
    if 'code' not in request.files or not request.files['code']:
        return json_error('No code file submitted!')
    if 'username' not in request.form or request.form['username'] == '':
        return json_error('No username!')

    sec_filename = secure_filename(request.files['code'].filename)
    if sec_filename in ['', 'input.in.txt', 'output.out.txt', 'answer.ans.txt', 'code.new.py']:
        return json_error('Invalid code filename!')
    code_filename, code_extension = os.path.splitext(sec_filename)
    if request.form['type'] == 'java' and code_extension != '.java':
        return json_error('Missing .java file extension!')

    # Make a temporary directory / save files there
    tempdir = tempfile.mkdtemp(prefix='judge-')
    request.files['code'].save(tempdir + '/' + code_filename + code_extension)

    # Enqueue the job
    job = q.enqueue_call(func=judge_submission, timeout=60,
                         ttl=RESULT_TTL, result_ttl=RESULT_TTL, failure_ttl=RESULT_TTL,
                         args=(tempdir, request.form['problem_id'], sec_filename,
                               request.form['type'], request.form['username']))
    job.meta['status'] = 'queued'
    job.save_meta()
    if DEBUG_LOWEST:
        log('New job id: {}'.format(job.get_id()))

    # Return submitted, along with the job id
    return {'status': 'success', 'job_id': job.get_id()}


@app.route('/api/get_status/<job_id>', methods=['GET'])
def get_status(job_id):
    # Make sure the job id is valid
    try:
        job = Job.fetch(job_id, connection=REDIS_CONN)
    except NoSuchJobError:
        return {'status': 'internal_error', 'error': 'NO_SUCH_JOB', 'job_id': job_id}, 200
    
    # Depending on the job's current status, return some info
    if job.is_queued:
        return job.meta, 202
    elif job.is_finished:
        return job.result, 200
    elif job.is_failed:
        return {'status': 'internal_error', 'error': 'JOB_FAILED', 'job_id': job_id}, 200
    else:
        return job.meta, 202


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
