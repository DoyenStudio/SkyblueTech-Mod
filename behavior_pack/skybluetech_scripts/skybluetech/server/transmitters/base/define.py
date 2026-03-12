# coding=utf-8


from skybluetech_scripts.tooldelta.api.server import GetBlockEntityData
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar

# TYPE_CHECKING
if 0:
    PosData = tuple[int, int, int, int]
# TYPE_CHECKING END

_APT = TypeVar("_APT", bound="BaseAccessPoint")
_NT = TypeVar("_NT", bound="BaseNetwork")

AP_MODE_INPUT = 0b01
AP_MODE_OUTPUT = 0b10


class BaseNetwork(Generic[_APT]):
    TRANSMITTER_SPEED_MAPPING = (None,)

    def __init__(self, dim, group_inputs, group_outputs, nodes, transfer_speed=0):
        # type: (int, set[_APT], set[_APT], set[tuple[int, int, int]], int | None) -> None
        self.dim = dim
        self.group_inputs = group_inputs
        self.group_outputs = group_outputs
        self.transfer_speed = transfer_speed
        self.nodes = nodes
        for _i in group_inputs | group_outputs:
            _i.bound_network(self)

    @classmethod
    def calc_transfer_speed(cls, block_name):
        # type: (str) -> int | None
        "覆写方法, 根据传入的管线方块 ID 返回传输速率"
        return 0

    def get_input_access_points(self):
        # type: () -> list[_APT]
        "获取网络中所有的输入型接入点, 按优先级从大到小排序"
        return sorted(
            self.group_inputs,
            key=lambda ap: ap.get_priority(),
            reverse=True,
        )

    def get_output_access_points(self):
        "获取网络中所有的输出型接入点, 按优先级从大到小排序"
        return sorted(
            self.group_outputs,
            key=lambda ap: ap.get_priority(),
            reverse=True,
        )

    def flush_from(self, other):
        # type: (BaseNetwork) -> None
        self.group_inputs = other.group_inputs
        self.group_outputs = other.group_outputs

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, self.__class__):
            return False
        return (
            self.dim == other.dim
            and self.group_outputs == other.group_outputs
            and self.group_inputs == other.group_inputs
        )

    def __repr__(self):
        return "BaseNetwork({}, {}, {})".format(
            self.dim, self.group_inputs, self.group_outputs
        )


class BaseAccessPoint(Generic[_NT]):
    def __init__(self, dim, x, y, z, access_facing, io_mode):
        # type: (int, int, int, int, int, int) -> None
        """
        Args:
            access_facing (int): 接入朝向
            io_mode (int): 1: 输入, 0: 输出
        """
        if io_mode not in (-1, 1, 2, 3):
            raise ValueError("Unsupport {}".format(io_mode))
        self.dim = dim
        self.x = x
        self.y = y
        self.z = z
        self.access_facing = access_facing
        self.io_mode = io_mode
        bdata = GetBlockEntityData(self.dim, (self.x, self.y, self.z))
        if bdata is None:
            raise Exception(
                "[ERROR] No block entity data at {}".format((self.x, self.y, self.z))
            )
        self.bdata = bdata
        self._bounded_network = None  # type: _NT | None
        self._load_settings()

    def bound_network(self, network):
        # type: (_NT) -> None
        self._bounded_network = network

    @property
    def target_pos(self):
        from ..constants import FACING_DXYZ

        dx, dy, dz = FACING_DXYZ[self.access_facing]
        return (self.x + dx, self.y + dy, self.z + dz)

    def get_bounded_network(self):
        # type: () -> _NT | None
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
        # type: (object) -> bool
        if not isinstance(other, self.__class__):
            return False
        return (
            self.x == other.x
            and self.y == other.y
            and self.z == other.z
            and self.access_facing == other.access_facing
        )

    def __repr__(self):
        return "BaseAP({}, {}, {}, {}, facing={}, io_mode={})".format(
            self.dim, self.x, self.y, self.z, self.access_facing, self.io_mode
        )


class ContainerNode(Generic[_NT]):
    def __init__(self, inputs=None, outputs=None):
        # type: (dict[int, _NT | None] | None, dict[int, _NT | None] | None) -> None
        self.inited = False
        self.uninited_faces = {0, 1, 2, 3, 4, 5}
        self.inputs = {}  # type: dict[int, _NT | None]
        self.outputs = {}  # type: dict[int, _NT | None]
        if inputs is not None:
            self.inputs.update(inputs)
            for k in inputs:
                self.uninited_faces.discard(k)
        if outputs is not None:
            self.outputs.update(outputs)
            for k in outputs:
                self.uninited_faces.discard(k)
        self.update_init_status()

    def set_face(self, facing, io_mode, network):
        # type: (int, int, _NT | None) -> None
        self.uninited_faces.discard(facing)
        if io_mode & AP_MODE_INPUT:
            self.inputs[facing] = network
        if io_mode & AP_MODE_OUTPUT:
            self.outputs[facing] = network
        self.update_init_status()

    def update_init_status(self):
        self.inited = not self.uninited_faces

    def all_empty(self):
        return all(i is None for i in self.inputs.values()) and all(
            i is None for i in self.outputs.values()
        )

    def __repr__(self):
        return "ContainerNode({}, {})".format(self.inputs, self.outputs)
