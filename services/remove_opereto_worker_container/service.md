This service removes existing opereto worker an remote docker-based hosts. The service gets a worker agent identifier. 
It checks if an such an agent exists. If it does, it retrieve the agent container id and running host from the agent properties and 
invokes teardown process on that container host to remove the worker container.

#### Service success criteria
Success if specified Opereto worker is removed. Otherwise, Failure.

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
* install_docker (included in this package)


#### Dependencies
No dependencies.