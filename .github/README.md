# Submission Judge

<a href="https://github.com/Giantpizzahead/submission-judge/actions?query=workflow%3Abuild"><img alt="build" src="https://github.com/Giantpizzahead/submission-judge/workflows/build/badge.svg" /></a>
<a href="https://codecov.io/gh/Giantpizzahead/submission-judge"><img alt="codecov" src="https://codecov.io/gh/Giantpizzahead/submission-judge/branch/master/graph/badge.svg" /></a>
<a href="https://github.com/Giantpizzahead/submission-judge/blob/master/LICENSE"><img alt="license" src="https://img.shields.io/github/license/giantpizzahead/submission-judge" /></a>

A simple judge for checking the correctness of code. Designed to be used for simple competitive programming problems.

This is a personal project, and it is **still in EARLY DEVELOPMENT**.

Documentation is currently lacking (will be added later... whenever i feel like it lol), but most of the function / variable names should be self-explanatory.

Hard-coding things is bad, so most of the 'hard-coded' values are configurable via environment variables! Check the variables in **env_vars.py** to figure out what they do.

Also look at the sample problems in the **sample_problem_info** folder (check the README.txt in problem #1 as well) to figure out how problems are structured. The problem creation process will probably be abstracted into a web form at some point though.

## Demo
A live version of this Docker image can be found <a href="http://submission-judge.westus2.cloudapp.azure.com:8080/">**here**</a>. Feel free to mess around with it. If you're feeling up for a challenge, see if you can solve the 2nd sample problem.

The security of this system should be pretty good, so if you want to try and break the judge system, go ahead! (Of course, if you do manage to break it, please file an issue so I can fix it. Thanks!)

## Usage
The built docker image can be found as a package on Github (located <a href="https://github.com/Giantpizzahead/submission-judge/packages/318563">**here**</a>). To play around with the submission judge, first <a href="https://docs.docker.com/get-docker/">install docker</a>, then <a href="https://docs.github.com/en/packages/using-github-packages-with-your-projects-ecosystem/configuring-docker-for-use-with-github-packages#authenticating-to-github-packages">authenticate to GitHub Packages</a> with Docker. Next, run:
```commandline
sudo swapoff -a
```
The above command disables memory swapping on the machine, which is required for the submission judge to enforce memory limits. By default, this does not persist across reboots.

Finally, run the below command to start the Docker container (Warning: The container may temporarily change some settings to make sure judging is consistent; these changes also do not persist across reboots):
```commandline
docker run -p 8080:8080 --privileged docker.pkg.github.com/giantpizzahead/submission-judge/submission-judge:latest
```
(Yes, it requires privileged mode. rip <a href="https://github.com/ioi/isolate">isolate</a>)

The web server listens on **port 8080**. You'll be greeted by a testing interface to mess around with.

Andddd that's it! Go get that AC! (Legends say there might even be an AC\* verdict...)

## Licensing
nah who cares about licensing, just use it! :D

(This repo uses the MIT License)

&copy;Corona 2020 Giantpizzahead