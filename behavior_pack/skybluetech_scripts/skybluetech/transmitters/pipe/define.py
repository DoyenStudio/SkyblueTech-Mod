# coding=utf-8
#
from skybluetech_scripts.tooldelta.no_runtime_typing import TYPE_CHECKING
from skybluetech_scripts.tooldelta.api.server import GetBlockEntityData
from ..constants import FACING_DXYZ

# TYPE_CHECKING
if TYPE_CHECKING:
    from ...machinery.basic.base_machine import BaseMachine
    PosData = tuple[int, int, int, int]
# TYPE_CHECKING END

AP_MODE_INPUT = 0
AP_MODE_OUTPUT = 1

class PipeNetwork:
    def __init__(self, dim, group_inputs, group_outputs, nodes, pipe_level=0):
        # type: (int, set[PipeAccessPoint], set[PipeAccessPoint], set[tuple[int, int, int]], int) -> None
        self.dim = dim
        self.group_inputs = group_inputs
        self.group_outputs = group_outputs
        self.pipe_level = pipe_level
        self.nodes = nodes
        for _i in group_inputs | group_outputs:
            _i.bound_network(self)

    def get_input_access_points(self):
        return sorted(
            self.group_inputs,
            key=lambda ap: ap.get_priority(),
            reverse=True,
        )

    def get_output_access_points(self):
        return sorted(
            self.group_outputs,
            key=lambda ap: ap.get_priority(),
            reverse=True,
        )

    def flush_from(self, other):
        # type: (PipeNetwork) -> None
        self.group_inputs = other.group_inputs
        self.group_outputs = other.group_outputs

    def __eq__(self, other):
        # type: (PipeNetwork) -> bool
        return self.dim == other.dim and self.group_outputs == other.group_outputs and self.group_inputs == other.group_inputs

    def __repr__(self):
        return "WireNetwork({}, {}, {})".format(self.dim, self.group_outputs, self.group_inputs)


class PipeAccessPoint:
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
        self._bounded_network = None # type: PipeNetwork | None
        self._load_settings()

    def bound_network(self, network):
        # type: (PipeNetwork) -> None
        self._bounded_network = network

    @property
    def target_pos(self):
        dx, dy, dz = FACING_DXYZ[self.access_facing]
        return (self.x + dx, self.y + dy, self.z + dz)

    def get_bounded_network(self):
        # type: () -> PipeNetwork | None
        return self._bounded_network

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
        # type: (PipeAccessPoint) -> bool
        return self.x == other.x and self.y == other.y and self.z == other.z and self.access_facing == other.access_facing

    def __repr__(self):
        return "PipeAP({}, {}, {}, {}, {})".format(self.dim, self.x, self.y, self.z, self.access_facing)