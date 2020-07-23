#!/bin/sh

if [ ! "$(docker ps -q -f name=judgelite)" ]; then
  echo "Stopping existing JudgeLite docker container..."
  sudo docker rm -f judgelite
fi

echo "Pulling latest JudgeLite docker image from Docker Hub..."
sudo docker pull giantpizzahead/judgelite

echo "Turning swap off..."
sudo swapoff -a

echo "Starting JudgeLite docker container..."
sudo docker run --name judgelite --privileged -dit \
  -p 8080:8080 \
  -e DEBUG=0 -e DEBUG_LOW=0 -e DEBUG_LOWEST=0 -e PROGRAM_OUTPUT=0 \
  -v ./problem_info:/problem_info \
  -v ./redis_db:/redis_db \
  giantpizzahead/judgelite

echo "Sending logs to judgelite.log..."
echo "------------------JUDGELITE STARTED------------------" >> judgelite.log
sudo docker logs -f judgelite >> judgelite.log &

echo "JudgeLite started up successfully!"
