This service run dockereto container on a given remote agent host. 

#### Service success criteria
Success if container is running. Otherwise, Failure.

#### Assumptions/Limitations
* Assumes that docker is installed on the remote agents host
* Requires that remote agent will have the following property
```
{
    "dockereto.worker": true
}
```
* Requires that opereto worker lib is installed 

You can run the following services on any remote agent host to install both opereto worker lib, docker and the required property:
* install_opereto_worker_lib (see package opereto_worker_lib)
* install_docker_on_host (included in this package)


#### Dependencies
No dependencies.

#### About dockereto
By the phrase "dockereto" we refer to any docker container with opereto embedded agent installed. While the container is running, the agent is connected to opereto continuous testing hub, allowing to run opereto micro services on that container. This mechanism is very useful to setup, run, manage and teardown test tools on demand on one or more opereto workers hosts. Tools like j-meter, testcafe, selenium, appium and many others may be wrapped as dockereto containers and used whenever needed in the continuous testing cycle.

This service allows running docker containers from local images located on the worker host or fetching pre-defined docker images from docker hub. If the input flag "fetch_from_dockerhub" is true, the service code will pull the image and then run it. Otherwise, it assumes that the requested image already exists on the host. 

#### Create a dockereto container
There are two ways to embed opereto agent in a docker container:
1. Add opereto agent installation to the container Dockerfile (as the main CMD) - recommended
2. Install the agent after the container is running via docker command exec 

If the input flag "embedded_agent" is true, this service code assumes that the agent installation and execution is already included in the dockerfile, otherwise, it will install and run the agent automatically right after the container is up and running. For most test tools, the first option (embedding the agent in the dockerfile) is recommended. The container may include the tool and all its dependencies, the agent runs as the main container CMD and thus, starts automatically after container restarts.  

The following directives must be added to any docker file in order to install the agent and run it as the main container CMD. 

```
RUN apt-get -yy update && apt-get -yy upgrade && \
   apt-get install -yy sudo && \
   apt-get install -y curl && \
   rm -rf /var/lib/apt/lists/*

RUN cd /opt && \
    curl -O https://s3.amazonaws.com/opereto-agent/opereto-agent-latest.tar.gz && \
    tar -zxvf opereto-agent-latest.tar.gz && \
    cd opereto-agent-latest && \
    chmod 777 -R *
    
WORKDIR /opt/opereto-agent-latest

RUN apt-get -yy update && apt-get install -yy default-jre && sudo apt-get install -yy python-pip

ENV javaParams "-Xms1000m -Xmx1000m"
ENV opereto_host ""
ENV agent_name ""
ENV opereto_user ""
ENV opereto_password ""
ENV log_level="info"

CMD java $javaParams -jar /opt/opereto-agent-latest/opereto-agent.jar -host $opereto_host -name $agent_name -u $opereto_user -p $opereto_password -loglevel $log_level
```

For example, the following Dockerfile creates testcafe test tool dockereto container:
```
FROM ubuntu:16.04

RUN apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential curl && \
  apt-get install -y software-properties-common

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash
RUN apt-get install -y nodejs

RUN node -v
RUN npm -v

RUN apt-get install -y firefox xvfb dbus-x11 && npm install testcafe -g

COPY . /opt/testcafe
RUN mkdir /opt/testcafe/docker
COPY testcafe-docker.sh /opt/testcafe/docker

RUN cd /opt/testcafe ; \
 npm install && \
 chmod +x /opt/testcafe/docker/testcafe-docker.sh

EXPOSE 1337 1338
# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
RUN apt-get -yy update && apt-get -yy upgrade && \
   apt-get install -yy sudo && \
   apt-get install -y curl && \
   rm -rf /var/lib/apt/lists/*

RUN cd /opt && \
    curl -O https://s3.amazonaws.com/opereto-agent/opereto-agent-latest.tar.gz && \
    tar -zxvf opereto-agent-latest.tar.gz && \
    cd opereto-agent-latest && \
    chmod 777 -R *

WORKDIR /opt/opereto-agent-latest

RUN apt-get -yy update && apt-get install -yy default-jre && sudo apt-get install -yy python-pip

ENV javaParams "-Xms1000m -Xmx1000m"
ENV opereto_host ""
ENV agent_name ""
ENV opereto_user ""
ENV opereto_password ""
ENV log_level="info"

CMD java $javaParams -jar /opt/opereto-agent-latest/opereto-agent.jar -host $opereto_host -name $agent_name -u $opereto_user -p $opereto_password -loglevel $log_level
```

#### Container configuration 
You can pass a set of configuration parameters to the new container setup (same as done via the docker command line). For example:

```
 "container_config": {
        "environment": {
            "param1": "value1"
        },
        "restart_policy": {
            "Name": "always"
        }
    },

```

This service wraps the official docker python client. 
The container_config json may include one or more of the parameters listed in the container run method at: https://docker-py.readthedocs.io/en/stable/containers.html#

