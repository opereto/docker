import os,sys
from opereto.helpers.services import ServiceTemplate
from opereto.exceptions import *
from opereto.utils.osutil import remove_package_cmd, install_package_cmd
from opereto.utils.validations import validate_string
from opereto.utils.shell import run_shell_cmd
import json

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        raise_if_not_root()
        raise_if_not_ubuntu()


    def validate_input(self):
        pass

    def process(self):

        (rc, out, error) = run_shell_cmd('docker version')
        if rc==0:
            print >> sys.stderr, 'Docker is already installed. Please remove this version first.'
            print >> sys.stderr, out+error
            return self.client.FAILURE

        self._print_step_title('Updating docker package sources..')
        (rc, out, error) = install_package_cmd('apt-transport-https ca-certificates curl software-properties-common', update_sources=self.input['update_sources'])
        if rc:
            print >> sys.stderr, out, error
            return self.client.FAILURE
        commands = [
            'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -',
            'add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"'
        ]
        for cmd in commands:
            (rc0, out0, error0) = run_shell_cmd('sudo -iEn '+cmd)
            if rc0:
                print >> sys.stderr, 'Failed to run command: {}'.format(cmd)
                print >> sys.stderr, out0+error0
                return self.client.FAILURE

        self._print_step_title('Installing docker (make take a few minutes..)')

        install_command = 'docker-ce'
        if self.input['docker-ce-version']!='latest':
            install_command += '={}'.format(self.input['docker-ce-version'])

        (rc1, out1, error1) = install_package_cmd(install_command, update_sources=self.input['update_sources'])
        if rc1:
            print >> sys.stderr, out1, error1
            print >> sys.stderr, 'Docker setup failed. Please retry to install a different version of docker.'
            return self.client.FAILURE


        self._print_step_title('Validating docker installation (running hello-world container)..')
        (rc2, out2, error2) = run_shell_cmd('sudo docker run hello-world')
        if rc2:
            print >> sys.stderr, out2+error2
            print >> sys.stderr, 'Verification failed. Please retry to install a different version of docker.'
            return self.client.FAILURE
        else:
            print 'Docker is up and running.'
            run_shell_cmd('sudo docker kill hello-world')

        if self.input.get('dockerhub_credentials'):
            self._print_step_title('Login to docker hub..')
            try:
                json_config = self.input['dockerhub_credentials']
                if validate_string(json_config):
                    json_config=json.loads(json_config)
                login_cmd = 'sudo -iEn docker login -u {} -p {}'.format(json_config['username'], json_config['password'])
                if json_config.get('server'):
                    login_cmd += ' {}'.format(json_config['server'])
                (rc3, out3, error3) = run_shell_cmd(login_cmd)
                print >> sys.stderr, out3+error3
                if rc3:
                    raise Exception, 'Failed to login to docker hub'
            except Exception, e:
                print >> sys.stderr, 'Login failed: {}. Please retry to login manually.'.format(str(e))
                return self.client.FAILURE

        (rc4, out4, error4) = run_shell_cmd('docker version')
        print out4+error4

        self._print_step_title('Updating docker worker agent property..')
        self.client.modify_agent_property(self.input['opereto_agent'], 'opereto.docker.worker', True)

        print 'Docker worker added successfully.'
        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
