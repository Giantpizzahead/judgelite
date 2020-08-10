This folder contains a sample problem (sum N numbers). This text file contains some general tips for making problems.

The statement.md, bonus.md, and hints.md files are not needed to create a problem. If they aren't there, the API call will simply return empty strings for them instead. In fact, the misc and solutions folders aren't needed either; they are used purely to organize the extraneous files.
The only mandatory things are an info.yml file, and a subtasks folder with the test cases.

Check the info_selfdoc.yml file for information on how to write an info.yml file.
When you're creating problems, I'd suggest just copying the info.yml file in this sample problem, and using it as a template.

Subtasks run test cases in alphabetical order, so it's recommended to use a numbering system. You can add a description for each test case by putting it after the number (01_desc.in).
The judge matches each .in file to the .out file with the same name. So, make sure your .in and .out files have the SAME NAME!!! (42_hello.in -> 42_hello.out)
The test cases should be ordered in (roughly) increasing difficulty.

The idea behind bonus subtasks is to give something for experienced programmers to strive for, while also not discouraging newcomers with overly hard subtasks. This is why the results from bonus subtasks aren't factored into the overall verdict.
Bonus subtasks are evaluated in the same way as regular subtasks, but the results / verdicts from them could be hidden to the user to avoid discouraging them (through some sort of client logic). Legends say there is an 'AC*' verdict now... :O

Any auxillary files that aren't needed in the actual system can be put in the misc folder. This could include things like testcase generators and solution explanations.

Try not to use the 'average' grading method when you have lots of test cases. It will slow down the system a lot.