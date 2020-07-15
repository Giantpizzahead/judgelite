# Use the official Ubuntu LTS image (focal)
FROM ubuntu:focal AS builder

# Install Python 3, C++ (via g++), and the JDK
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    g++ \
    openjdk-14-jdk-headless

# Install dependencies
RUN apt-get install -y \
    time \
    redis

# Install production dependencies for Python 3
RUN pip3 install \
    Flask \
    gunicorn \
    psutil \
    rq \
    pyyaml

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run the startup script
ENTRYPOINT ["/app/start.sh"]
