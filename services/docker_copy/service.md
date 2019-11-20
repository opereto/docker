Copy files/folders between a container and the local filesystem (same as docker cp command)

#### Service success criteria
Success if copy was successful. Otherwise, Failure.

#### Assumptions/Limitations
* Assumes that docker is installed on the remote agents host
* Requires that remote agent will have the following property
```
{
    "opereto.docker.worker": true
}
```
* Requires that opereto worker lib is installed 

You can run the following services on any remote agent host to install both opereto worker lib, docker and the required property:
* install_opereto_worker_lib (see package opereto_worker_lib)
* install_docker_on_host (included in this package)


#### Dependencies
No dependencies.


