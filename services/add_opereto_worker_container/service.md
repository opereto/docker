This service creates a new opereto worker an remote docker-based hosts

#### Service success criteria
Success if Opereto worker is created. Otherwise, Failure.

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