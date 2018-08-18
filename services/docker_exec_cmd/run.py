from opereto.helpers.services import ServiceTemplate
from opereto.helpers.dockereto import Dockereto
from opereto.exceptions import *
import sys

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def setup(self):
        raise_if_not_root()
        raise_if_not_ubuntu()
        self.dockereto = Dockereto()

    def validate_input(self):
        ### TBD verify topology
        pass

    def process(self):

        self._print_step_title('Running docker command in container..')
        config = {
            'user': self.input['user']
        }

        if self.input['workdir']:
            config['workdir']=self.input['workdir']
        if self.input['tty']:
            config['tty']=True
        if self.input['privileged']:
            config['privileged']=True
        if self.input['detach']:
            print 'Running command in the background..'
            config['detach']=True
        if self.input['env_params']:
            config['environment']=self.input['env_params']

        (exc, out) = self.dockereto.cmd_exec(self.input['container_id'], self.input['command'], **config)
        if exc:
            print 'Exit code: {}'.format(int(exc))
        if (out):
            print 'Docker command output: {}'.format(out.encode('utf-8', 'replace'))

        self.client.modify_process_property('stdout', out)
        if exc is not None:
            self.client.modify_process_property('exitcode', int(exc))
        else:
            self.client.modify_process_property('exitcode', 0)

        if exc is not None and self.input['expected_exitcode'] is not None:
            try:
                if int(exc)!=int(self.input['expected_exitcode']):
                    return self.client.FAILURE
            except ValueError:
                pass

        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())



