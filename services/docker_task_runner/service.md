This service is a generic runner to docker containerized tools. In case of test tools, it runs the container and parse the test results 
base on user-defined parser service passed to it. 

#### Assumptions/Limitations
In case of test tools, it gets a pre-defined test results parser service as an input. The parser service must setisfy Opereto test result parser requirements. In addition, it gets the docker containerized test tool results directory as an input, creates a local directory on the host and mounts it to the container results directory so that test results will be accessible by this service.

#### Service success criteria
Success if docker container command execution ends with exit code 0. Otherwise, failure.

#### Dependencies
* Opereto worker virtual environment running on the docker host
* Assumes that docker is installed on the host running it (you may use install_docker_on_host service to install docker)
* In case of using private docker builds, the service assumes that the worker is already logged-in to docker hub