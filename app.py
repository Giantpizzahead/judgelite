# TODO:
#  Add config file for gunicorn to avoid weird param setup
#  Setup Dockerfile in IntelliJ to allow for easier testing
#  See if there's some way to make isolate work without privileged, or see if Cloud Run can allow that
#  Create some sort of documentation (the gunicorn server automatically handles the queue system so yay!)
#  Change the port being used (8080 is too easy to guess)
#  Add support for multiple test cases (use local filesystem for now)

import os
import judge_submission
from flask import *

app = Flask(__name__)
DEBUG = os.environ.get('DEBUG', '0') == '1'
SHOW_BORDER = os.environ.get('SHOW_BORDER', '0') == '1'

@app.route('/', methods=['GET', 'POST'])
def handle_submission():
    if request.method == 'GET':
        # Return a simple testing form for the GET method
        return render_template('form.html')
    else:
        # Judge the submission
        return judge_submission.judge_submission(request)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 6293)))
