# JudgeLite

<a href="https://github.com/Giantpizzahead/judgelite/actions?query=workflow%3Abuild"><img alt="build" src="https://github.com/Giantpizzahead/judgelite/workflows/build/badge.svg" /></a>
<a href="https://codecov.io/gh/Giantpizzahead/judgelite"><img alt="codecov" src="https://codecov.io/gh/Giantpizzahead/judgelite/branch/master/graph/badge.svg" /></a>
<a href="https://github.com/Giantpizzahead/judgelite/.github/LICENSE"><img alt="license" src="https://img.shields.io/github/license/giantpizzahead/judgelite" /></a>

A simple, easy to setup judge for checking the correctness of code.

## Features

* **Multiple test cases and subtasks!**
* Supports interactive problems (WIP)
* Variety of scoring methods (all-or-nothing, partials, bonus tests, etc.)
* Supports submissions in C++, Java, and Python 3
* Secure code compilation and execution using <a href="https://github.com/ioi/isolate">isolate</a>
* Extremely simple setup
* Easy-to-use submission API
* Simple administrative web interface (WIP)

## Demo

**http://judgelite.westus2.cloudapp.azure.com**

The secret key is "VERYSTRONGSECRETKEY". You'll need this to submit solutions to the problems on the demo website. Warning: Trying to submit a solution to a problem without logging in first will result in an error (this will be fixed in the next release).

A live version of JudgeLite can be found at the above link. Feel free to mess around with it. If you're feeling up for a challenge, see if you can solve the 2nd sample problem.

## Setup

Easy setup instructions for Linux and Windows are on <a href="https://github.com/Giantpizzahead/judgelite/wiki/Setup-Instructions">this wiki page</a>.

The web server listens on **port 80**. You'll be greeted by a testing interface to mess around with.

Andddd that's it! Go get that AC! :)

## Usage

(Note: This is a personal project, so it's probably best to find another judge if you're trying to host a contest / create a big website. JudgeLite is ideal for smaller use cases, like programming clubs and small practice sites.)

JudgeLite is designed to be used for competitive programming problems, although anything requiring automatic testing of source code will work.

A more detailed, easier to understand Wiki page explaining how to use the submission API will be created later. For now, here is a quick summary:

To submit code, send a **POST** request to **/api/submit** with the content type **multipart/form-data**. Include the following fields:

* **problem_id** - The ID of the problem that you're submitting a solution for.
* **type** - The language that your code is written in. Should be one of "java", "cpp", or "python".
* **code** - The file containing the submission's source code. Note that this is an actual *file*, not just a string representing the source code.

The returned status code will be 200 if the submission was successful, and 400 if the submission failed. The returned repsonse will be JSON. It will have exactly two of the following entries:

* **status** - Reports on whether or not the submission was successful. Will be either "success" or "fail".
* **error** - Only present if the submission failed. Presents a user-friendly message of why the submission failed.
* **job_id** - Only present if the submission succeeded. This is the unique ID value that was assigned to the submission. It is used to query the status of the submission (see below).

To get the status of a submission, send a **GET** request to **/api/status/<job_id>**, where job_id is the ID returned from the initial POST request. The returned status code will be 202 if the submission is still processing, and 200 if the submission has been fully evaluated (or an error occurred). The returned response will be JSON. It will have the following entries:

* **status** - Contains the status of the submission. Will be one of "queued", "judging", "done", "compile_error", or "internal_error".

The following entries may or may not be available, depending on the returned status:

* **score** - (judging, done) The current score of the submission for each subtask.
* **is_bonus** - (judging, done) Whether or not each subtask is a bonus subtask (useful for changing how bonus verdicts are displayed).
* **subtasks** - (judging, done) A list of subtasks. Each subtask has a list of test cases. Each test case is an array with 3 values: ['verdict', time, memory].
* **max_score** - (judging, done, compile_error) The maximum score that a submission could get on a problem, excluding bonus points.
* **final_score** - (done, compile_error) The final score that a submission recieved.
* **error** - (compile_error, internal_error) If status is compiler_error, the error message that the compiler generated. Else, the error code for the internal error.

A sample submission form / results page can be found on the demo website. You can use the code there as an example on how to use the API.

In order to use the submission API, you would first need to create some problems to submit to! Unfortunately, JudgeLite is currently in alpha, so the web interface for making problems isn't finished yet. The file structure for creating problems is pretty easy to create though. If you want to try making some problems, take a look at the sample problems in the **sample_problem_info** directory.

## License

JudgeLite is distributed under the MIT License. This means that you are **free to customize anything you want**, as long as you distribute your work under the MIT License as well.

## Credits

This repository is maintained by <a href="https://github.com/Giantpizzahead">Giantpizzahead</a>.

Special thanks to <a href="https://github.com/frodakcin">frodakcin</a> for helping out with JudgeLite's design!
