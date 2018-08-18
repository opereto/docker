This service removes a running dockereto container on a given remote agent host. 
To learn more about dockereto containers, please check out the setup_dockereto_container service doumentation.

#### Service success criteria
Success if container was running and removed successfuly. Otherwise, Failure.

#### Assumptions/Limitations
* Currently supports only Linux distributions as follows: Ubuntu 14.04 Trusty, Ubuntu 16.04 Xenial
* Requires that agent user will have sudo permissions
* Requires that opereto worker lib is installed (see package opereto_core_services)

#### Dependencies
No dependencies.