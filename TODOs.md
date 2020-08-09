## TODOs (pre-V1)
 - Update the wiki / README / add documentation
 - Continue getting feedback from people

## TODOs (post-V1)
 - Limit the frequency of submission by a single user (at least make it so they can't submit multiple at once)
 - Allow custom checkers (other than diff, as a standalone binary)
 - Allow custom graders for interactive problems!
   - Maybe make two modes: One where your program is directly linked to the submitted code via stdin and stdout, and one where your program's stdout is used (to allow for completely custom problem setup)
 - Add support for partial scoring (fractional scores for each test case allowed, instead of just right or wrong)

#### Other stuff
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
