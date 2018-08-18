This service installs docker on a given remote agent host if not installed. 

#### Service success criteria
Success if Opereto docker is installed and if the built-in docker "hello workld" container runs successfully. Otherwise, Failure.

#### Assumptions/Limitations
* Currently supports only Linux distributions as follows: Ubuntu 14.04 Trusty, Ubuntu 16.04 Xenial
* Requires that agent user will have sudo permissions
* Requires that opereto worker lib is installed (see package opereto_core_services)

#### Dependencies
No dependencies.