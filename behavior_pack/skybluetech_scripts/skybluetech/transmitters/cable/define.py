# coding=utf-8
#
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.api.server import GetBlockEntityData
from ..constants import FACING_DXYZ

# TYPE_CHECKING
if TYPE_CHECKING:
    PosData = tuple[int, int, int, int]
# TYPE_CHECKING END

AP_MODE_INPUT = 0
AP_MODE_OUTPUT = 1


class CableNetwork:
    def __init__(self, dim, group_inputs, group_outputs, nodes, cable_level=0):
        # type: (int, set[CableAccessPoint], set[CableAccessPoint], set[tuple[int, int, int]], int) -> None
        self.dim = dim
        self.group_inputs = group_inputs
        self.group_outputs = group_outputs
        self.cable_level = cable_level
        self.inited_containers = 0
        self.all_containers = 0
        self.nodes = nodes
        for _i in group_inputs | group_outputs:
            _i.bound_network(self)

    def AllContainersInited(self):
        return self.inited_containers == self.all_containers

    def AddAwakeNum(self):
        # if not self.AllDevicesInited():
        #     self.inited_tanks += 1
        self.inited_containers += 1
        if self.inited_containers > self.all_containers:
            print ("[ERROR] inited_tanks > all_containers", self.inited_containers, self.all_containers)

    # def AddCableNode(self, xyz):
    #     # type: (tuple[int, int, int]) -> None
    #     # not use yet
    #     self.wire_nodes.add(xyz)

    def __repr__(self):
        return "CableNetwork({}, {})".format(self.group_inputs, self.group_outputs)
            

    def __hash__(self):
        return hash((tuple(self.group_inputs), tuple(self.group_outputs)))

    def same(self, other):
        # type: (CableNetwork) -> bool
        return self.group_inputs == other.group_inputs and self.group_outputs == other.group_outputs


class CableAccessPoint:
    def __init__(self, dim, x, y, z, access_facing, io_mode):
        # type: (int, int, int, int, int, int) -> None
        """
        Args:
            access_facing (int): 接入朝向
            io_mode (int): 1: 输入, 0: 输出
        """
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.access_facing = access_facing
        self.io_mode = io_mode
        bdata = GetBlockEntityData(self.dim, self.x, self.y, self.z)
        if bdata is None:
            raise Exception("[ERROR] No block entity data at {}".format((self.x, self.y, self.z)))
        self.bdata = bdata
        self._bounded_network = None # type: CableNetwork | None
        self._load_settings()

    def bound_network(self, network):
        # type: (CableNetwork) -> None
        self._bounded_network = network

    def get_bounded_network(self):
        # type: () -> CableNetwork | None
        return self._bounded_network

    @property
    def target_pos(self):
        dx, dy, dz = FACING_DXYZ[self.access_facing]
        return (self.x + dx, self.y + dy, self.z + dz)

    def _load_settings(self):
        settings_list = self._init_or_fix_settings()
        self.settings = settings_list[self.access_facing]

    def _init_or_fix_settings(self):
        settings_list = self.bdata["settings"]
        if settings_list is None:
            settings_list = [{}] * 6
            self.bdata["settings"] = settings_list
        if len(settings_list) < 6:
            settings_list += [{}] * (6 - len(settings_list))
            self.bdata["settings"] = settings_list
        return settings_list

    def _dump_settings(self):
        settings_list = self._init_or_fix_settings()
        settings_list[self.access_facing] = self.settings
        self.bdata["settings"] = settings_list

    def get_label(self):
        # type: () -> int
        return self.settings.get("label", 0)

    def set_label(self, label):
        # type: (int) -> None
        self.settings["label"] = label
        self._dump_settings()

    def get_priority(self):
        # type: () -> int
        return self.settings.get("priority", 0)

    def set_priority(self, priority):
        # type: (int) -> None
        self.settings["priority"] = priority
        self._dump_settings()

    def __hash__(self):
        return hash((self.x, self.y, self.z, self.access_facing))

    def __eq__(self, other):
        # type: (CableAccessPoint) -> bool
        return self.x == other.x and self.y == other.y and self.z == other.z and self.access_facing == other.access_facing

    def __repr__(self):
        return "CableAccessPoint({}, {}, {}, {}, {})".format(self.dim, self.x, self.y, self.z, self.access_facing)
