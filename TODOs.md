## TODOs
 - Fill in the stack tests (use LCA array generation in a tree with DFS)
 - Make a front-end web interface to create and edit problems
   - Make sure generated YAML file uses strings as subtask names

### Less important TODOs
 - Make convenience function to generate correct outputs using a program
   - Have it check the program's output if the .out file already exists (to manually check for correctness)
 - Allow custom graders (other than diff, as a standalone binary)
 - Add support for partial scoring (fractional scores for each test case allowed, instead of just right or wrong)
 - Use a config file instead of env vars
 - Combine debug env vars into a single DEBUG integer
 - Organize & document the code (not important YET)

#### Other stuff
 - See if there's some way to automate the 'swapoff -a' command (maybe replace with swap accounting?)
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
