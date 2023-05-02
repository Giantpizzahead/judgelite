# JudgeLite <a href="https://github.com/Giantpizzahead/judgelite/actions?query=workflow%3Abuild"><img alt="build" src="https://github.com/Giantpizzahead/judgelite/workflows/build/badge.svg" /></a> <a href="https://hub.docker.com/r/giantpizzahead/judgelite"><img alt="Docker Image Version" src="https://img.shields.io/docker/v/giantpizzahead/judgelite?label=docker&logo=docker" /></a> <a href="https://codecov.io/gh/Giantpizzahead/judgelite"><img alt="codecov" src="https://codecov.io/gh/Giantpizzahead/judgelite/branch/master/graph/badge.svg" /></a> <a href="https://github.com/Giantpizzahead/judgelite/.github/LICENSE"><img alt="license" src="https://img.shields.io/github/license/giantpizzahead/judgelite" /></a>

<img src="media/logo.png" alt="JudgeLite logo" align="right" width="128">

### A simple, easy to setup judge for checking the correctness of code.

#### Made by (and used by) <a href="http://hhsproclub.com/">Homestead High School's Programming Club</a>.

## Features

* **Multiple test cases and subtasks!**
* Variety of scoring methods (all-or-nothing, partials, stop-on-wrong, etc.)
* Support for <a href="https://github.com/Giantpizzahead/judgelite/wiki/Custom-Checkers">custom checkers</a> written in all 3 languages shown below
* Supports submissions in C++, Java, and Python 3
* Secure code compilation and execution using <a href="https://github.com/ioi/isolate">isolate</a>
* Extremely simple <a href="https://github.com/Giantpizzahead/judgelite/wiki/Setup-Instructions">setup</a>
* Bonus test cases! (less discouraging form of subtasks)
* Easy-to-use <a href="https://github.com/Giantpizzahead/judgelite/wiki/API-Reference">submission API</a>
* Easy <a href="https://github.com/Giantpizzahead/judgelite/wiki/Creating-Problems">problem creation</a>
* Simple administrative web interface
* Supports interactive problems (WIP)

## Demo

[Video demo](https://www.youtube.com/watch?v=m7hOYGyG4y8)

![Home page](https://i.gyazo.com/2c9bc77860fcc3dd1c8fc4078810822f.png)
*Home page*

![Submission list](https://i.gyazo.com/b1b359b488434c1aa10f14c52b0cd377.png)
*Submission list*

![Submission details](https://i.gyazo.com/6e91e6ecadbb67a04458a504d1e89378.png)
*Submission details*

![Problem statement](https://i.gyazo.com/6d408b6e74cd6e0e945b3506650fa35a.png)
*Problem statement*

![Subtasks! And lots of test cases...](https://i.gyazo.com/1a454eab33f79ef38748ef16b5b93f1a.png)
*Subtasks! And lots of test cases...*

## Setup

Easy setup instructions for Linux and Windows are on <a href="https://github.com/Giantpizzahead/judgelite/wiki/Setup-Instructions">this wiki page</a>.

The web server listens on **port 80**. You'll be greeted by a nice admin interface.

Andddd that's it! Go get that AC! :)

## Usage

(Note: This is a personal project, so it's probably best to find another judge if you're trying to host a contest / create a big website. JudgeLite is ideal for smaller use cases, like programming clubs and small practice sites.)

JudgeLite is designed to be used for competitive programming problems, although anything requiring automatic testing of source code will work.

There is an **API Reference page** on JudgeLite, where all the allowed API calls are showcased with examples. You can use the reference as an example on how to use the API. A more detailed Wiki page explaining the subtleties of the submission API can be found <a href="https://github.com/Giantpizzahead/judgelite/wiki/API-Reference">here</a>.

In order to use JudgeLite, you'll need to first create some problems to submit to! Luckily, the file structure for creating problems is pretty easy to follow (uses <a href="https://yaml.org/">YAML</a> and <a href="https://www.markdownguide.org/">Markdown</a>). Take a look at the sample problem structure in the **sample_problem_info** directory for an example set of problems. A more detailed Wiki page about problem creation can be found <a href="https://github.com/Giantpizzahead/judgelite/wiki/Creating-Problems">here</a>.

## Contributing

We welcome contributions of all kinds, whether they're bug reports, feature requests, or pull requests! See the [contributing guidelines](https://github.com/Giantpizzahead/judgelite/blob/master/CONTRIBUTING.md) for more details. If you'd like to get your hands dirty, try tackling one of the [open issues](https://github.com/Giantpizzahead/judgelite/issues).

## License

JudgeLite is distributed under the [MIT License](https://github.com/Giantpizzahead/judgelite/blob/master/LICENSE). This means that you are **free to customize anything you want**, as long as you distribute your work under the MIT License as well.

## Credits

This repository is maintained by <a href="https://github.com/Giantpizzahead">Giantpizzahead</a>.

Special thanks to <a href="https://github.com/frodakcin">frodakcin</a> and the other HHS Programming Club officers for helping out with JudgeLite's development!
