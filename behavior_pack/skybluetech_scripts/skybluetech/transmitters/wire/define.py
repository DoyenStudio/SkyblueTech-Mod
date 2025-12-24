# coding=utf-8
#
from ....tooldelta.no_runtime_typing import TYPE_CHECKING
from ...machinery.pool import GetMachineStrict

# TYPE_CHECKING
if TYPE_CHECKING:
    from ...machinery.basic.base_machine import BaseMachine
    PosData = tuple[int, int, int, int]
# TYPE_CHECKING END

NODE_GENERATOR = 1
NODE_APPLIANCE = 2


class WireLevelEnum:
    WIRELEVEL_NONE = 0
    WIRELEVEL_TIN = 1
    WIRELEVEL_COPPER = 2
    WIRELEVEL_SILVER = 3
    WIRELEVEL_SUPERCONDUCT = 4

    @classmethod
    def from_block_name(cls, block_name):
        # type: (str) -> int
        return {
            "skybluetech:copper_wire": cls.WIRELEVEL_COPPER,
            "skybluetech:tin_wire": cls.WIRELEVEL_TIN,
            "skybluetech:silver_wire": cls.WIRELEVEL_SILVER,
            "skybluetech:superconduct_wire": cls.WIRELEVEL_SUPERCONDUCT,
            "skybluetech:creative_wire": cls.WIRELEVEL_NONE,
        }.get(block_name, cls.WIRELEVEL_NONE)


WIRELEVEL_2_POWERLIMIT = (None, 384, 512, 4096, 1048576)


# 表示一个由线缆组成的能量网络。
# 网络只关心其中的机器节点。
class WireNetwork:

    __slots__ = (
        "dim",
        "group_generators",
        "group_appliances",
        "wire_level",
        "inited_devices",
        "all_devices",
        "wire_nodes"
    )

    def __init__(self, dim, group_generators, group_appliances, wire_level=0):
        # type: (int, set[PosData], set[PosData], int) -> None
        self.dim = dim
        self.group_generators = group_generators
        self.group_appliances = group_appliances
        self.wire_level = wire_level
        self.inited_devices = 0
        self.all_devices = 0
        self.wire_nodes = set() # type: set[tuple[int, int, int]]

    def AddWireNode(self, xyz):
        # type: (tuple[int, int, int]) -> None
        self.wire_nodes.add(xyz)

    def updateAllDevices(self):
        self.all_devices = len(self.group_generators) + len(self.group_appliances)

    def GetAllPoses(self):
        # type: () -> set[PosData]
        return self.group_generators | self.group_appliances

    def GetAllMachinesInNetwork(self):
        # type: () -> set[BaseMachine]
        all_machines = set()  # type: set[BaseMachine]
        for x, y, z, _ in self.GetAllPoses():
            m = GetMachineStrict(self.dim, x, y, z)
            if m:
                all_machines.add(m)
        return all_machines

    def IsZombieNetwork(self):
        "Deprecated"
        # 如果是两个用电器或者两个发电机连在一起就会形成僵尸网络
        return (
            (
                len(self.group_generators) == 0
                and len(self.group_appliances) == 2
            )
            or (
                len(self.group_generators) == 2
                and len(self.group_appliances) == 0
            )
        )

    def AllDevicesInited(self):
        return self.inited_devices == self.all_devices

    def AddAwakeNum(self):
        # if not self.AllDevicesInited():
        #     self.inited_devices += 1
        self.inited_devices += 1
        if self.inited_devices > self.all_devices:
            print ("[ERROR] inited_devices > all_devices", self.inited_devices, self.all_devices)

    def get_power_limit(self):
        return WIRELEVEL_2_POWERLIMIT[self.wire_level]

    def __repr__(self):
        return "WireNetwork({}, {}, {})".format(self.dim, self.group_generators, self.group_appliances)

    def __hash__(self):
        return hash((self.dim, tuple(self.group_generators), tuple(self.group_appliances)))

    def same(self, other):
        # type: (WireNetwork) -> bool
        return self.dim == other.dim and self.group_appliances == other.group_appliances and self.group_generators == other.group_generators


class CableNetwork:
    def __init__(self, dim, group_inputs, group_outputs, cable_level=0):
        # type: (int, set[PosData], set[PosData], int) -> None
        self.dim = dim
        self.group_inputs = group_inputs
        self.group_outputs = group_outputs
        self.cable_level = cable_level
        self.wire_nodes = set() # type: set[tuple[int, int, int]]

    def AddCableNode(self, xyz):
        # type: (tuple[int, int, int]) -> None
        self.wire_nodes.add(xyz)

    def __repr__(self):
        return "CableNetwork({}, {})".format(self.group_inputs, self.group_outputs)
            

    def __hash__(self):
        return hash((tuple(self.group_inputs), tuple(self.group_outputs)))

    def same(self, other):
        # type: (CableNetwork) -> bool
        return self.group_inputs == other.group_inputs and self.group_outputs == other.group_outputs

