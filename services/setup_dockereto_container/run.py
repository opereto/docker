import sys
from opereto.helpers.services import ServiceTemplate
from opereto.helpers.dockereto import Dockereto
from opereto.utils.shell import run_shell_cmd
from opereto.utils.validations import JsonSchemeValidator, included_services_scheme, item_properties_scheme, default_entity_description_scheme, default_entity_name_scheme, default_variable_name_scheme
from opereto.exceptions import *
import time
import uuid
import os

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        self.container=None
        self.cleanup=False
        raise_if_not_root()
        raise_if_not_ubuntu()
        self.dockereto = Dockereto()

    def validate_input(self):
        ## set and validate users
        source_user = self.client.input['opereto_originator_username']
        self.users = [source_user]
        self.owners = [source_user]

        try:
            if self.input['additional_users'] is not None:
                additional_users = self.input['additional_users'].replace(" ", "").split(',')
        except:
            additional_users=[]
        try:
            if self.input['additional_owners'] is not None:
                additional_owners = self.input['additional_owners'].replace(" ", "").split(',')
        except:
            additional_owners=[]
        self.users = [source_user] + list(set([x for x in additional_users if x]))
        self.owners = [source_user] + list(set([x for x in additional_owners if x]))

        all_users = self.users+self.owners
        existing_users = self.client.search_users()
        existing_user_ids=[]
        for existing in existing_users:
            existing_user_ids.append(existing['id'])
        for user in all_users:
            if user!='' and user not in existing_user_ids:
                print >> sys.stderr, 'User {} does not exist'.format(user)
                return self.client.FAILURE

        self.agent_id = self.input['agent_identifier'] or 'dockereto-' + str(uuid.uuid4())[:12]

        ## agent id
        validator = JsonSchemeValidator(self.agent_id, default_variable_name_scheme)
        validator.validate()

        ## agent name
        validator = JsonSchemeValidator(self.input['agent_name'], default_entity_name_scheme)
        validator.validate()

        ## agent description
        validator = JsonSchemeValidator(self.input['agent_description'], default_entity_description_scheme)
        validator.validate()

        ## agent_properties
        if self.input['agent_properties']:
            validator = JsonSchemeValidator(self.input['agent_properties'], item_properties_scheme)
            validator.validate()

        ## post_operations
        if self.input['post_operations']:
            validator = JsonSchemeValidator(self.input['post_operations'], included_services_scheme)
            validator.validate()



    def process(self):

        self._print_step_title('Setup container..')
        image_name = self.input['docker_image']
        if self.input['fetch_from_dockerhub']:
            self._print_step_title('Fetching image from docker hub..')
            (rc, out, error) = run_shell_cmd('docker pull {}'.format(image_name))
            if rc:
                print >> sys.stderr, 'Failed to fetch image from docker hub'
                print >> sys.stderr, out+error
                return self.client.FAILURE

        additional_config = self.input['container_config'] or {}
        install_agent=False

        if self.input['embedded_agent']:
            agent_cred = {
                'opereto_host': self.input['opereto_host'],
                'opereto_token': self.input['opereto_token'],
                'agent_name': self.agent_id,
                'log_level': 'info',
                'javaParams':'-Xms1000m -Xmx1000m'
            }
            if additional_config.get('environment'):
                additional_config['environment'].update(agent_cred)
            else:
                additional_config['environment']=agent_cred
        else:
            install_agent=True

        self.container = self.dockereto.setup_container(image_name, **additional_config)

        container_cred = {
            'container_id': self.container.id,
            'host_agent': self.input['opereto_agent'],
            'container_agent': self.agent_id
        }
        self.client.modify_process_property('container_credentials', container_cred)

        WAIT_AGENT_ITERATIONS=10
        if install_agent:
            WAIT_AGENT_ITERATIONS=20
            self._print_step_title('Installing opereto agent on container..')

            def copy_files(file):
                source = os.path.join(self.input['opereto_workspace'], file)
                dest = os.path.join('/', file)
                copy_pid = self.client.create_process('docker_copy', container_id=self.container.id, host_path=source, container_path=dest, copy_direction='host_to_container')
                if not self.client.is_success(copy_pid):
                    self.cleanup=True
                    return self.client.FAILURE

            if copy_files('opereto-agent.jar'):
                return self.client.FAILURE
            if copy_files('run-opereto-agent.sh'):
                return self.client.FAILURE


            cmd_pid0 = self.client.create_process('docker_exec_cmd', workdir='/', container_id=self.container.id, command='chmod 777 run-opereto-agent.sh')
            if not self.client.is_success(cmd_pid0):
                self.cleanup=True
                return self.client.FAILURE

            install_cmd = '/run-opereto-agent.sh -h {} -t {} -n {} -o root -g root'.format(self.input['opereto_host'], self.input['opereto_token'], self.agent_id)
            cmd_pid = self.client.create_process('docker_exec_cmd', detach=True, workdir='/', container_id=self.container.id, command=install_cmd)
            if not self.client.is_success(cmd_pid):
                self.cleanup=True
                return self.client.FAILURE


        ## check agent availability
        self._print_step_title('Waiting for container agent to connect..')
        agent_is_up = False
        for i in range(WAIT_AGENT_ITERATIONS):
            try:
                agent_status = self.client.get_agent_status(self.agent_id)
                if agent_status['online']:
                    agent_is_up = True
                    print 'Container agent is up and running.'
                    break
            except:
                pass
            time.sleep(10)

        if not agent_is_up:
            print >> sys.stderr, 'Container agent is not connected.'
            self.cleanup=True
            return self.client.FAILURE

        ## create/modify agent
        permissions = {
            'owners': self.users,
            'users': self.owners
        }
        agent_properties = self.input['agent_properties']
        agent_properties.update({'container_host_agent': self.input['opereto_agent'], 'container_id': self.container.id })

        self.client.modify_agent_properties(self.agent_id, agent_properties)
        self.client.modify_agent(self.agent_id, name=self.input['agent_name'], description=self.input['agent_description'], permissions=permissions)

        ## run post install services
        for service in self.input['post_operations']:
            input = service.get('input') or {}
            agent = service.get('agents') or self.agent_id
            pid = self.client.create_process(service=service['service'], agent=agent, title=service.get('title'), **input)
            if not self.client.is_success(pid):
                self.cleanup=True
                return self.client.FAILURE

        return self.client.SUCCESS

    def teardown(self):
        if self.cleanup:
            self.dockereto.teardown_container(self.container.id)


if __name__ == "__main__":
    exit(ServiceRunner().run())



