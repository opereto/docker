from opereto.helpers.services import ServiceTemplate
from opereto.helpers.dockereto import Dockereto
from opereto.exceptions import *


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

        self._print_step_title('Teardown container..')
        self.dockereto.teardown_container(self.input['container_id'])

        return self.client.SUCCESS

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())



