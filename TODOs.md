## TODOs
 - Make a front-end web interface to create and edit problems
   - Make sure generated YAML file uses strings as subtask names
 - Decorate the front-end interface a bit (look into Bootstrap?)
 - Combine debug env vars into a single DEBUG integer
 - Make a way to view all past submissions in a table

### Less important TODOs
 - Allow custom checkers (other than diff, as a standalone binary)
 - Allow custom graders for interactive problems!
   - Maybe make two modes: One where your program is directly linked to the submitted code via stdin and stdout, and one where your program's stdout is used (to allow for completely custom problem setup)
 - Add support for partial scoring (fractional scores for each test case allowed, instead of just right or wrong)

#### Other stuff
 - See if there's some way to automate the 'swapoff -a' command (maybe replace with swap accounting?)
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
