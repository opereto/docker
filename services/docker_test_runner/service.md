This service is a generic runner to docker containerized test tools. It allows to build the container on-the-fly or fetch it from docker hub. It runs the container and parse the test results 
base on user-defined parser service passed to it. 

#### Assumptions/Limitations
This runner acts under the following assumptions:
1. It gets the docker containerized test tool results directory as an input, creates a local directory on the host and mounts it to the container results directory so that test results will be accessible by this service.
1. It assumes that the test tools container execution command ends with 0 for successful test execution. Any other exitcode is considered as a test failure.
1. It gets a pre-defined test results parser service as an input. The parser service must satisfy Opereto test result parser requirements.


#### Service success criteria
Success if docker container command execution ends with exit code 0. Otherwise, failure.

#### Dependencies
* Opereto worker virtual environment
* Assumes that docker is installed on the worker running it
* To fetch private builds from docker hub, the service assumes that the worker is already logged-in to docker hub (see install_docker_on_host service)