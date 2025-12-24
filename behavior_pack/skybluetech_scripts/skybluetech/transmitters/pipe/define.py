# coding=utf-8
#
from ....tooldelta.no_runtime_typing import TYPE_CHECKING
from ...machinery.pool import GetMachineStrict

# TYPE_CHECKING
if TYPE_CHECKING:
    from ...machinery.basic.base_machine import BaseMachine
    PosData = tuple[int, int, int, int]
# TYPE_CHECKING END


class PipeNetwork:
    def __init__(self, dim, group_inputs, group_outputs, pipe_level=0):
        # type: (int, set[PosData], set[PosData], int) -> None
        self.dim = dim
        self.group_inputs = group_inputs
        self.group_outputs = group_outputs
        self.pipe_level = pipe_level
        self.pipe_nodes = set() # type: set[tuple[int, int, int]]

    def AddWireNode(self, xyz):
        # type: (tuple[int, int, int]) -> None
        self.pipe_nodes.add(xyz)

    def updateAllDevices(self):
        self.all_devices = len(self.group_inputs) + len(self.group_outputs)

    def GetAllPoses(self):
        # type: () -> set[PosData]
        return self.group_inputs | self.group_outputs

    def GetAllMachinesInNetwork(self):
        # type: () -> set[BaseMachine]
        all_machines = set()  # type: set[BaseMachine]
        for x, y, z, _ in self.GetAllPoses():
            m = GetMachineStrict(self.dim, x, y, z)
            if m:
                all_machines.add(m)
        return all_machines

    def AllDevicesInited(self):
        return self.inited_devices == self.all_devices

    def AddAwakeNum(self):
        # if not self.AllDevicesInited():
        #     self.inited_devices += 1
        self.inited_devices += 1
        if self.inited_devices > self.all_devices:
            print ("[ERROR] pipe inited_devices > all_devices", self.inited_devices, self.all_devices)

    def __repr__(self):
        return "WireNetwork({}, {}, {})".format(self.dim, self.group_outputs, self.group_inputs)

    def __hash__(self):
        return hash((self.dim, tuple(self.group_outputs), tuple(self.group_inputs)))
