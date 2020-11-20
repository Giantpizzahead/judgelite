#!/bin/sh

SECRET_KEY="default_change_this"

if [ "$(docker ps -q -a -f name=judgelite)" ]; then
  echo "Stopping existing JudgeLite docker container..."
  sudo docker rm -f judgelite
fi

echo "Pulling latest JudgeLite docker image from Docker Hub..."
sudo docker pull giantpizzahead/judgelite:version-1.1.1

echo "Turning swap off..."
sudo swapoff -a

echo "Starting JudgeLite docker container..."
sudo docker run --name judgelite --privileged -dit \
  -p 80:80 \
  -e DEBUG=0 -e DEBUG_LOW=0 -e DEBUG_LOWEST=0 -e PROGRAM_OUTPUT=0 \
  -e SECRET_KEY=$SECRET_KEY \
  -v $PWD/problem_info:/problem_info \
  -v $PWD/redis_db:/redis_db \
  giantpizzahead/judgelite:version-1.1.1

echo "Sending logs to judgelite.log..."
echo "------------------JUDGELITE STARTED------------------" >> judgelite.log
sudo docker logs -f judgelite >> judgelite.log &

echo "-----------------------------------------------------"
echo "JudgeLite started up successfully!"
