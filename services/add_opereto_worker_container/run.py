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
        self.agent_id = self.input['agent_identifier'] or 'opereto-worker-' + str(uuid.uuid4())[:8]

        ## agent id
        validator = JsonSchemeValidator(self.agent_id, default_variable_name_scheme)
        validator.validate()


    def process(self):

        additional_env_params = {
            'restart_policy': {'Name': 'always'}
        }

        create_worker_pid = self.client.create_process(service='setup_dockereto_container',
                                                  title='Create opereto worker container',
                                                  container_config=additional_env_params,
                                                  docker_image='opereto/worker',
                                                  agent_identifier=self.agent_id,
                                                  fetch_from_dockerhub=True)

        if not self.client.is_success(create_worker_pid):
            return self.client.FAILURE

        container_credentials = self.client.get_process_property(create_worker_pid, 'container_credentials')
        container_agent_id = container_credentials['container_agent']
        self.client.modify_process_property('container_credentials', container_credentials)
        self.client.modify_agent_property(container_agent_id, 'opereto.worker', True)


        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
