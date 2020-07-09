## Opereto docker services

Opereto container services allowing to setup, operate and teardown on-demand docker-based tool containers with an integrated opereto agent running on any opereto worker host and connected to opereto h (aka dockereto). Using containers is a highly convenient method to manage remote test tools, automation analyzers and processing utilities and other self-contained utilities. You may create any custom Dockerfile, include an opereto agent in it and save it in docker hub or as a local build on the opereto worker host.
The package includes two services:


### Prerequisits/dependencies
* Services are mapped to run on a standard opereto worker agent
* opereto_core_services
