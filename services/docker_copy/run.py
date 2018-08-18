from opereto.helpers.services import ServiceTemplate
from opereto.exceptions import *
from opereto.utils.shell import run_shell_cmd
import sys

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        raise_if_not_root()
        raise_if_not_ubuntu()

    def validate_input(self):
        pass

    def process(self):
        host_path = self.input['host_path']
        container_path = '{}:{}'.format(self.input['container_id'], self.input['container_path'])
        if self.input['copy_direction']=='host_to_container':
            self._print_step_title('Coping from host file system to container..')
            source=host_path
            dest=container_path
        else:
            self._print_step_title('Coping from container to host file system..')
            source=container_path
            dest=host_path

        print 'Source: {}'.format(source)
        print 'Destination: {}'.format(dest)

        (rc, out, error) = run_shell_cmd('docker cp {} {}'.format(source, dest))
        if rc:
            print >> sys.stderr, 'Failed to copy..'
            print >> sys.stderr, out+error
            return self.client.FAILURE

        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())



