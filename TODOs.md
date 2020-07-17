## TODOs
 - Add a longer delay between refreshes when waiting in queue
 - Make the after-submit status report look pretty
 - Add USACO-like realtime test results
   - Maybe use the USACO design style to make it interesting?
 - Make convenience function to generate correct outputs using a program
   - Have it check the program's output if the .out file already exists (to manually check for correctness)
 - Organize & document the code

### Less important TODOs
 - Allow custom graders (other than diff, as a standalone binary)
 - Use a config file instead of env vars
 - Combine debug env vars into a single DEBUG integer
 - Investigate weird Java MLE errors (not consistent)
 - See if there's some way to automate the 'swapoff -a' command (maybe replace with swap accounting?)
 - Look into unit tests (maybe even CI/CD integration), and make some of your own! :)
 - Github badges are cool. I want some!
 - Look into async / threaded workers for gunicorn
 - Disk quota is not enabled, only fsize is. That means that you could bypass the max file size limit by creating tons of small files, overloading the system. No one would do this by accident though, so it's not something that is too important to fix (plus, who would even think to try this?).
