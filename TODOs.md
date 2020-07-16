## TODOs
 - Add a compile time limit to keep the job from hanging (10 seconds should work, but set as env var just in case)
   - Actually, just use isolate to compile the program as well. Maybe even restructure the code so that you can use the same function for both compilation and execution. This would protect against things like <a href="https://codegolf.stackexchange.com/questions/69189/build-a-compiler-bomb">compiler bombs</a> as well... Then again, who would be mean enough to try on of those? (definitely not me :P)
 - Send back information on compile errors (be careful with this!)
   - Should be safe as long as isolate is used
 - Add USACO-like realtime test results
   - Maybe use the USACO design style to make it interesting?
 - Make convenience function to generate correct outputs using a program
   - Have it check the program's output if the .out file already exists (to manually check for correctness)
 - Add option to skip remaining tests in subtasks only if the verdict is TLE (to save time)
 - Consider moving off GCP Always Free, and switching to a year-long trial (maybe with Azure). This would allow for a higher memory limit!
 - Organize & document the code

### Less important TODOs
 - Allow custom graders (other than diff, as a standalone binary)
 - Use a config file instead of env vars
 - Investigate weird Java MLE errors (not consistent)
 - See if there's some way to automate the 'swapoff -a' command (maybe replace with swap accounting?)
 - Look into async / threaded workers for gunicorn
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
