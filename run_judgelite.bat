@echo off

set SECRET_KEY="default_change_this"

echo Stopping existing JudgeLite docker container (if it exists)...
docker rm -f judgelite

echo Pulling latest JudgeLite docker image from Docker Hub...
docker pull giantpizzahead/judgelite:version-1.0

echo Starting JudgeLite docker container...
docker run --name judgelite --privileged -dit^
  -p 80:80^
  -e DEBUG=0 -e DEBUG_LOW=0 -e DEBUG_LOWEST=0 -e PROGRAM_OUTPUT=0^
  -e SECRET_KEY=%SECRET_KEY%^
  -v %cd%/problem_info:/problem_info^
  -v %cd%/redis_db:/redis_db^
  giantpizzahead/judgelite:version-1.0

echo Sending logs to judgelite.log...
echo "------------------JUDGELITE STARTED------------------" >> judgelite.log

echo -----------------------------------------------------
echo JudgeLite started up successfully! Sending logs to judgelite.log... (keep this window open to continue logging)
docker logs -f judgelite >> judgelite.log

echo ----- ERROR: JudgeLite failed to start. Check the above command outputs for more info. -----
pause