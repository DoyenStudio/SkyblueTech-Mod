# coding=utf-8


class MultiblockPortBindings(object):
    """保存本次成型选定的接口，按控制器给出的顺序绑定和释放。"""

    _bound_ports = ()

    def _bind_ports(self, machines):
        self._bound_ports = tuple(machines)
        for machine in self._bound_ports:
            self._bind_port(machine)

    def _bind_port(self, machine):
        machine.SetMachineRef(self)

    def _unbind_ports(self, only_owned=False):
        for machine in self._bound_ports:
            if not only_owned or machine.getMachineRef() is self:
                self._release_port(machine)
        self._bound_ports = ()

    def _release_port(self, machine):
        machine.UnsetMachineRef()
