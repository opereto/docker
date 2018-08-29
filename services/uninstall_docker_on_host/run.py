import sys
from opereto.helpers.services import ServiceTemplate
from opereto.exceptions import *
from opereto.utils.osutil import remove_package_cmd, install_package_cmd, get_platform_name, DIST_TRUSTY, DIST_XENIAL
from opereto.utils.shell import run_shell_cmd

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        raise_if_not_root()
        raise_if_not_ubuntu()


    def validate_input(self):
        pass


    def process(self):
        self._print_step_title('Uninstalling old docker installations if found..')
        (rc, out, error) = remove_package_cmd('docker-ce docker docker-engine docker.io')
        print out+error

        (rc2, out2, error2) = run_shell_cmd('docker version')
        if rc2==0:
            print >> sys.stderr, 'Docker is still running on this host. Please re-try later or remove docker manually.'
            print out2+error2
            return self.client.FAILURE


        self._print_step_title('Updating docker config files..')
        self.client.modify_agent_property(self.client.input['opereto_agent'], 'dockereto.worker', False)

        print 'Docker was removed.'
        return self.client.SUCCESS


    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
