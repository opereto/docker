This service removes docker on a given remote agent host if installed. 

#### Service success criteria
Success if no docker is installed at the end (e.g. it will succeed even if docker was not installed prior to execution). Otherwise, Failure.

#### Assumptions/Limitations
* Currently supports only Linux distributions as follows: Ubuntu 14.04 Trusty, Ubuntu 16.04 Xenial
* Requires that agent user will have sudo permissions
* Requires that opereto worker lib is installed (see package opereto_worker_lib)

#### Dependencies
No dependencies.