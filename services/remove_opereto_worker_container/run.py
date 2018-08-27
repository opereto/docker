import os,sys
from opereto.helpers.services import ServiceTemplate
from opereto.exceptions import *
from opereto.utils.validations import JsonSchemeValidator, default_variable_name_scheme

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        raise_if_not_root()
        raise_if_not_ubuntu()


    def validate_input(self):
        validator = JsonSchemeValidator(self.input['agent_identifier'], default_variable_name_scheme)
        validator.validate()


    def process(self):

        ## fetch the container agent properties
        try:
            agent_properties = self.client.get_agent_properties(self.input['agent_identifier'])
            self.container_id = agent_properties['custom']['container_id']
            self.container_host_agent_id = agent_properties['custom']['container_host_agent']
        except Exception, e:
            self._print_error(e)
            raise_runtime_error('Cannot retrieve agent {} properties. Please check that agent exists and properly configured.'.format(self.input['agent_identifier']))

        ## remvove the worker container
        remove_worker_pid = self.client.create_process(service='teardown_dockereto_container',
                                                  title='Removes opereto worker container',
                                                  agent=self.container_host_agent_id,
                                                  container_id=self.container_id)

        if not self.client.is_success(remove_worker_pid):
            return self.client.FAILURE

        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
