## Opereto docker services

Opereto container services allowing to setup, operate and teardown on-demand docker-based tool containers with an integrated opereto agent running on any opereto worker host and connected to opereto h (aka dockereto). Using containers is a highly convenient method to manage remote test tools, automation analyzers and processing utilities and other self-contained utilities. You may create any custom Dockerfile, include an opereto agent in it and save it in docker hub or as a local build on the opereto worker host.
The package includes two services:

| Service                               | Description                                                                                       |
| --------------------------------------|:-------------------------------------------------------------------------------------------------:| 
| services/install_docker        | Install docker framework on opereto worker host                                                   | 
| services/uninstall_docker      | Uninstall docker framework on opereto worker host                                                 | 
| services/setup_dockereto_container    | Setup dockereto - docker container with opereto agent - on opereto worker host                    | 
| services/teardown_dockereto_container | Teardown a running dockereto - docker container with opereto agent - on opereto worker host       | 
| services/docker_exec_cmd              | Run a command inside this container. Similar to docker exec.                                      | 
| services/docker_copy                  | Copy files or folders between a container and the local filesystem.                               | 


### Prerequisits/dependencies
* Services are mapped to run on a standard opereto worker agent
* opereto_core_services
        
        
### Service packages documentation
* [Learn more about automation packages and how to use them](http://help.opereto.com/support/solutions/articles/9000152583-an-overview-of-service-packages)
* [Learn more how to extend this package or build custom packages](http://help.opereto.com/support/solutions/articles/9000152584-build-and-maintain-custom-packages)

