import sys, os,re
from opereto.helpers.services import TaskRunner
from opereto.utils.shell import run_shell_cmd
from opereto.utils.validations import JsonSchemeValidator, default_variable_pattern
from opereto.exceptions import *


class ServiceRunner(TaskRunner):

    def __init__(self, **kwargs):
        TaskRunner.__init__(self, **kwargs)

    def _validate_input(self):
        input_scheme = {
            "type": "object",
            "properties": {
                "docker_image": {
                    "type": ["string", "null"]
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
            },
            "required": ['docker_command'],
            "additionalProperties": True
        }
        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()


    def _run_task(self):

        command_prefix = ' -v {}:{}'.format(self.host_test_result_directory, self.input['test_results_directory'])

        ## add volume and env vars to command
        docker_cmd_splitted = re.split('docker\s+run', self.docker_command)
        command_postfix = docker_cmd_splitted[0]
        if len(docker_cmd_splitted) == 2:
            command_postfix = docker_cmd_splitted[1]

        ## modify docker command
        if self.docker_env_params:
            with open(self.docker_env_vars, 'a') as env_file:
                for name, value in self.docker_env_params.items():
                    env_file.write('{}={}\n'.format(name, value))
            command_prefix += ' --env-file {}'.format(self.docker_env_vars)
        if self.docker_image:
            if docker_cmd_splitted[1].find(self.docker_image) == 0:
                command_postfix += ' {}'.format(self.docker_image)
        if command_prefix:
            command_prefix += ' '
        docker_cmd = 'docker run {}{}'.format(command_prefix, command_postfix)

        ## run container
        print 'Running: ' + docker_cmd
        (exc, out, error) = run_shell_cmd(docker_cmd, verbose=True)
        self.client.modify_process_property('exitcode', exc)

        if exc not in self.valid_exit_codes:
            print >> sys.stderr, 'Docker execution failed..'
            self.exitcode = 2

    def _setup(self):
        self.docker_image = self.input['docker_image']
        self.docker_env_params = self.input['docker_env_params']
        self.docker_command = self.input['docker_command']

    def _teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
