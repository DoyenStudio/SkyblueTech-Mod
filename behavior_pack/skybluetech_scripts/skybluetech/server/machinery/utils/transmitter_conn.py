# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import (
    CheckChunkState,
    GetBlockName,
    GetBlockStates,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.skybluetech.common.define.facing import (
    DXYZ_FACING,
    FACING_EN,
    OPPOSITE_FACING,
)
from ...transmitters.cable.logic import isCable
from ...transmitters.pipe.logic import isPipe
from ...transmitters.wire.logic import isWire
from ..basic import BaseMachine

TRANSMITTER_TYPES = (
    ("cable", isCable),
    ("pipe", isPipe),
    ("wire", isWire),
)


def is_transmitter(block_name):
    # type: (str | None) -> bool
    "方块是否为传输管线 (物品管道 / 流体管道 / 电线)。"
    if not block_name:
        return False
    return bool(isCable(block_name) or isPipe(block_name) or isWire(block_name))


def get_connection_state_key(facing):
    # type: (int) -> str
    "管线方块上表示该面是否已连接的 block state 键。"
    return "skybluetech:connection_" + FACING_EN[facing]


def get_neighbor_connection(dim, neighbor_pos, facing):
    # type: (int, tuple[int, int, int], int) -> bool | None
    """
    读取邻居管线朝向 facing 一面的连接状态。

    连接状态只记录在管线一侧, 只看邻居方块名无法得知连接是否已被扳手切断。

    Returns:
        bool | None: None 表示邻居所在区块暂时不可读, 调用方应保持原状态不修改
    """
    states = GetBlockStates(dim, neighbor_pos)
    if states is None:
        return None
    return bool(states.get(get_connection_state_key(OPPOSITE_FACING[facing]), False))


def get_face_connection(dim, neighbor_pos, facing):
    # type: (int, tuple[int, int, int], int) -> bool | None
    """
    判断机器朝向 facing 一面的邻居是否连着它。

    连接状态记在管线一侧, 因此邻居是管线时要读它的连接状态; 邻居不是管线
    (或已经不存在) 时必然是断开。

    Returns:
        bool | None: None 表示邻居所在区块暂时不可读, 调用方应保持原状态不修改
    """
    neighbor_name = GetBlockName(dim, neighbor_pos)
    if neighbor_name is None:
        if not CheckChunkState(dim, neighbor_pos):
            # 邻居方块所在区块暂时不可读, 保持原状态
            return None
        # 位置可读却是空的: 邻居管线已经不存在
        return False
    if is_transmitter(neighbor_name):
        return get_neighbor_connection(dim, neighbor_pos, facing)
    # 邻居不是管线
    return False


def get_socket_states(machine_states, facing, neighbor_name, connected, types=None):
    # type: (dict, int, str | None, bool, tuple | None) -> dict[str, bool]
    """
    构造机器朝向 facing 一面需要写入的插座模型状态。

    以机器上实际声明了哪些插座状态键为准:
    <面>_<类型>_connection 按邻居的管线类型分别判断;
    connection_<面> 表示该面是否连着任意一种管线 (储罐 / 太阳能板 / 装配机
    等机器用的是这个键)。
    """
    facing_en = FACING_EN[facing]
    states = {}  # type: dict[str, bool]
    for type_name, checker in (TRANSMITTER_TYPES if types is None else types):
        key = "skybluetech:%s_%s_connection" % (facing_en, type_name)
        if key in machine_states:
            states[key] = (
                bool(neighbor_name) and bool(checker(neighbor_name)) and connected
            )
    key = "skybluetech:connection_" + facing_en
    if key in machine_states:
        states[key] = is_transmitter(neighbor_name) and connected
    return states


def refresh_machine_socket(dim, machine_pos, neighbor_pos):
    # type: (int, tuple[int, int, int], tuple[int, int, int]) -> bool
    """
    按邻居管线当前的连接状态, 重刷机器朝向该邻居的插座模型状态。

    管线放置 / 拆除 / 被扳手切断或恢复后调用, 使机器一侧的插座与管线一侧的
    连接状态保持一致, 避免出现"管道手臂已缩回而机器插座仍然亮着"的情况。
    邻居不是管线 (或已经不存在) 时, 插座一定收起。

    Returns:
        bool: 是否实际修改了机器的方块状态
    """
    facing = DXYZ_FACING.get((
        neighbor_pos[0] - machine_pos[0],
        neighbor_pos[1] - machine_pos[1],
        neighbor_pos[2] - machine_pos[2],
    ))
    if facing is None:
        return False
    connected = get_face_connection(dim, neighbor_pos, facing)
    if connected is None:
        return False
    neighbor_name = GetBlockName(dim, neighbor_pos)
    machine_states = GetBlockStates(dim, machine_pos) or {}
    states = {}  # type: dict[str, bool]
    for key, value in get_socket_states(
        machine_states, facing, neighbor_name, connected
    ).items():
        if machine_states.get(key, False) != value:
            states[key] = value
    if not states:
        return False
    UpdateBlockStates(dim, machine_pos, states)
    return True


class TransmitterConn(object):
    def __init__(self, cable=False, pipe=False, wire=False):
        # type: (bool, bool, bool) -> None
        """
        为传输管线渲染提供的便捷类。

        Args:
            cable: 是否渲染物品管道连接
            pipe: 是否渲染管道连接
            wire: 是否渲染电缆连接

        Methods:
            block_placed: 当机器放置时调用, 渲染连接
            neighbor_block_changed: 当相邻块改变时调用, 更新连接
        """
        self.cable = cable
        self.pipe = pipe
        self.wire = wire
        self.transmitter_types = tuple(
            (type_name, checker)
            for type_name, checker, enabled in (
                ("cable", isCable, cable),
                ("pipe", isPipe, pipe),
                ("wire", isWire, wire),
            )
            if enabled
        )

    def get_states(self, machine_states, facing, neighbor_name, connected):
        # type: (dict, int, str | None, bool) -> dict[str, bool]
        "按邻居管线与管线一侧的连接状态, 构造该面需要写入的插座模型状态。"
        return get_socket_states(
            machine_states, facing, neighbor_name, connected, self.transmitter_types
        )

    def block_placed(self, machine):
        # type: (BaseMachine) -> None
        "机器放置后, 按四周管线当前的连接状态渲染插座模型。"
        machine_pos = (machine.x, machine.y, machine.z)
        machine_states = GetBlockStates(machine.dim, machine_pos) or {}
        states = {}  # type: dict[str, bool]
        for (dx, dy, dz), facing in DXYZ_FACING.items():
            neighbor_pos = (machine.x + dx, machine.y + dy, machine.z + dz)
            connected = get_face_connection(machine.dim, neighbor_pos, facing)
            if connected is None:
                continue
            neighbor_name = GetBlockName(machine.dim, neighbor_pos)
            states.update(
                self.get_states(machine_states, facing, neighbor_name, connected)
            )
        if states:
            UpdateBlockStates(machine.dim, machine_pos, states)

    def neighbor_block_changed(self, machine, event):
        # type: (BaseMachine, BlockNeighborChangedServerEvent) -> None
        "相邻方块改变后, 按邻居管线当前的连接状态更新该面的插座模型。"
        facing = DXYZ_FACING.get((
            event.neighborPosX - machine.x,
            event.neighborPosY - machine.y,
            event.neighborPosZ - machine.z,
        ))
        if facing is None:
            return
        neighbor_pos = (event.neighborPosX, event.neighborPosY, event.neighborPosZ)
        connected = get_face_connection(machine.dim, neighbor_pos, facing)
        if connected is None:
            return
        neighbor_name = GetBlockName(machine.dim, neighbor_pos)
        machine_pos = (machine.x, machine.y, machine.z)
        machine_states = GetBlockStates(machine.dim, machine_pos) or {}
        states = self.get_states(machine_states, facing, neighbor_name, connected)
        if states:
            UpdateBlockStates(machine.dim, machine_pos, states)
