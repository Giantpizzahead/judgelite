# Remember to run the docker image in privileged mode for isolate to work!

# Use the official Ubuntu LTS image (focal)
FROM ubuntu:focal AS builder

# Install Python 3, C++ (via g++), and the JDK
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    g++ \
    openjdk-14-jdk-headless

# Install other dependencies
# libcap2 is required for isolate
RUN apt-get install -y \
    time \
    redis \
    libcap2

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

# Move isolate config file to correct location
RUN mv ./isolate.cf /usr/local/etc/isolate

# Run the startup script
ENTRYPOINT ["./start.sh"]
