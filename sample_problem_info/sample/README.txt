This folder contains a sample problem (sum N numbers). This text file contains some general tips for making problems.

The problem creation system will likely be moved to a web interface later.

Check the info.yml file for information on how to write one of those. I'd suggest just copying that YAML file, and using it as a template.

Subtasks run test cases in alphabetical order, so it's recommended to use a numbering system. You can add a description for each test case by putting it after the number (01_desc.in).
The judge matches each .in file to the .out file with the same name. So, make sure your .in and .out files have the SAME NAME!!! (42_hello.in -> 42_hello.out)
The test cases should be ordered in (roughly) increasing difficulty.

The idea behind bonus subtasks is to give something for experienced programmers to strive for, while also not discouraging newcomers with overly hard subtasks. This is why the results from bonus subtasks aren't factored into the overall verdict.
Bonus subtasks are evaluated in the same way as regular subtasks, but the results / verdicts from them aren't revealed to the user (to avoid a bad verdict for an otherwise correct submission). The points earned from bonus subtasks still count though! Legends say there is an 'AC*' verdict now... :O

Any auxillary files that aren't needed in the actual system can be put in the misc folder. This could include things like testcase generators and solution explanations.

Try not to use the 'average' grading method when you have lots of test cases. It will slow down the system a lot.

fill_missing_output = true
This fills in .out files if they are missing when you submit a program. It's useful for automatically generating output files to test cases. This will not overwrite any existing output files. MAKE SURE YOUR CODE IS CORRECT BEFORE USING THIS!!!