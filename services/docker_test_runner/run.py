from opereto.helpers.services import ServiceTemplate
from opereto.utils.validations import JsonSchemeValidator, validate_dict, default_variable_pattern
from opereto.utils.shell import run_shell_cmd
from opereto.utils.osutil import make_directory
from pyopereto.client import OperetoClient
import sys, os, re, time


class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)

    def validate_input(self):

        input_scheme = {
            "type": "object",
            "properties": {
                "docker_image": {
                    "type": "string",
                    "minLength": 1
                },
                "build_image": {
                    "type": "boolean"
                },
                "dockerfile_path": {
                    "type": "string"
                },
                "fetch_from_dockerhub": {
                    "type": "boolean"
                },
                "test_results_directory": {
                    "type": "string",
                    "minLength": 1
                },
                "docker_command": {
                    "type": "string",
                    "minLength": 1
                },
                "docker_env_params": {
                    "type": "object",
                    "patternProperties": {
                        default_variable_pattern: {
                            "type": "string"
                        }
                    }
                },
                "parser_config": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "minLength": 1
                        },
                        "input": {
                            "type": "object"
                        },
                        "title": {
                            "type": "string"
                        }
                    },
                    "required": ['service_id'],
                    "additionalProperties": True
                },
                "required": ['parser_config', 'docker_command', 'test_results_directory', 'docker_image'],
                "additionalProperties": True
            }
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()


    def process(self):

        ## build docker if requested
        if self.input['build_image']:
            self._print_step_title('Building image [docker content directory = {}]..'.format(self.docker_context_directory))

            if self.docker_context_directory!=self.input['opereto_workspace']:
                build_command = 'docker build {} {}'.format(self.input['build_options'],self.docker_context_directory)
                (exc, out, error) = run_shell_cmd(build_command, verbose=True)
                if exc != 0:
                    print >> sys.stderr, 'Docker build failed. Aborting..'
                    return self.client.FAILURE


        ## fetch from dockerhub if needed
        if self.input['fetch_from_dockerhub'] and not self.input['build_image']:
            self._print_step_title('Fetching image from docker hub..')
            (rc, out, error) = run_shell_cmd('docker pull {}'.format(self.docker_image))
            if rc:
                print >> sys.stderr, 'Failed to fetch image from docker hub'
                print >> sys.stderr, out+error
                return self.client.FAILURE


        ## preapre environment vars
        if self.input['docker_env_params']:
            with open(self.docker_env_vars, 'a') as env_file:
                for name, value in self.input['docker_env_params'].items():
                    env_file.write('{}={}\n'.format(name,value))

        ## run listener
        self.listener_pid = self.client.create_process('opereto_test_listener', test_results_path=self.listener_results_dir, parent_pid=self.parent_pid)

        ## run parser
        self.parser_pid = self.client.create_process(self.input['parser_config']['service_id'],
                                                     parser_directory_path=self.host_test_result_directory, listener_directory_path=self.listener_results_dir)

        ## add volume and env vars to command
        docker_cmd_splitted  = re.split('docker\s+run', self.input['docker_command'])
        cmd_additional_params = '-v {}:{} '.format(self.host_test_result_directory, self.input['test_results_directory'])
        if self.input['docker_env_params']:
            cmd_additional_params += ' --env-file {} '.format(self.docker_env_vars)

        cmd_image = self.docker_image
        if docker_cmd_splitted[1].find(self.docker_image)>=0:
            cmd_image=''
        docker_cmd = 'docker run {} {} {}'.format(cmd_additional_params,docker_cmd_splitted[1], cmd_image)

        ## run container
        print 'Running: '+ docker_cmd
        (exc, out, error) = run_shell_cmd(docker_cmd, verbose=True)
        self.client.modify_process_property('exitcode', exc)

        if exc != 0:
            print >> sys.stderr, 'Docker execution failed. Aborting..'
            return self.client.FAILURE

        return self.client.SUCCESS

    def setup(self):
        self.parent_pid = self.input['opereto_parent_flow_id'] or self.input['pid']
        self.docker_context_directory = self.input['dockerfile_path'] or self.input['opereto_workspace']
        self.docker_image = self.input['docker_image']
        self.listener_pid = None
        self.parser_pid = None
        self.listener_results_dir = os.path.join(self.input['opereto_workspace'], 'opereto_listener_results')
        self.docker_env_vars = os.path.join(self.input['opereto_workspace'], 'docker_env_vars')
        self.container_test_results_directory = self.input['test_results_directory']
        self.host_test_result_directory = os.path.join(self.input['opereto_workspace'], 'opereto_parser_results')
        make_directory(self.host_test_result_directory)


    def teardown(self):
        time.sleep(self.input['keep_parser_running'])

        if self.parser_pid:
            self.client.stop_process(self.parser_pid)
        if self.listener_pid:
            self.client.stop_process(self.listener_pid)


if __name__ == "__main__":
    exit(ServiceRunner().run())
