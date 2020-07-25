## TODOs
 - Polish up the submission API (add a username & secret key)
   - Make sure to include documentation for the API
 - Add problem statement support (markdown) to the problem info
   - https://benweet.github.io/stackedit.js/
 - Use a config file instead of env vars
   - Take a look at docker config (https://medium.com/better-programming/about-using-docker-config-e967d4a74b83)
 - Combine debug env vars into a single DEBUG integer
 - Add a way to send a POST request to some other web server when a submission is done being evaluated (for easier integration)
 - Keep track of past submissions, and make a way to view all past submissions in a table
   - Great way to get started with databases! :D
   - Redis would be a great choice since it's already part of the application (https://redis.io/ for docs)

### Less important TODOs
 - Make a front-end web interface to view and submit problems
 - Make a front-end web interface to create and edit problems
   - Make sure generated YAML file uses strings as subtask names
 - Organize & document the code
 - Make convenience function to generate correct outputs using a program
   - Have it check the program's output if the .out file already exists (to manually check for correctness)
 - Allow custom graders (other than diff, as a standalone binary)
 - Allow custom graders for interactive problems!
   - Maybe make two modes: One where your program is directly linked to the submitted code via stdin and stdout, and one where your program's stdout is used (to allow for completely custom problem setup)
 - Add support for partial scoring (fractional scores for each test case allowed, instead of just right or wrong)

#### Other stuff
 - See if there's some way to automate the 'swapoff -a' command (maybe replace with swap accounting?)
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
