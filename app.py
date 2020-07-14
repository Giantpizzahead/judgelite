# TODO:
#  Increase security by running the program as a non-privileged user
#  Add support for multiple test cases (use local filesystem for now)
#  - Use a dictionary with the 'select multiple files' option, map .in files to .out files
#  - Evaluate test cases in alphabetical order
#  See if it's possible to have a client that can query for the current testing progress (responsive! :D).
#  - USACO-like test results? :O

import os
import judge_submission
import requests
from flask import *

app = Flask(__name__)

@app.route('/test')
def test():
    r = requests.get('https://www.google.com/')
    print("remote", request.remote_addr)
    return r.content

@app.route('/', methods=['GET', 'POST'])
def handle_submission():
    if request.method == 'GET':
        # Return a simple testing form for the GET method
        return render_template('form.html')
    else:
        # Judge the submission
        return judge_submission.judge_submission(request)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
