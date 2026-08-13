# coding=utf-8
from collections import deque
from weakref import WeakValueDictionary

from skybluetech_scripts.skybluetech.common.define.facing import (
    NEIGHBOR_BLOCKS_ENUM,
    OPPOSITE_FACING,
)
from skybluetech_scripts.tooldelta.api.common import Delay, ExecLater
from skybluetech_scripts.tooldelta.api.server import (
    CheckChunkState,
    GetBlockName,
    GetBlockStates,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events.event_bus import GetMCServerEventBus
from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    BlockRemoveServerEvent,
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
    EntityPlaceBlockAfterServerEvent,
    OnSimTickServerEvent,
)
from skybluetech_scripts.tooldelta.events.service import EventListenerService
from skybluetech_scripts.tooldelta.extensions.typing import Generic, TypeVar

from ..base.define import (
    AP_MODE_INPUT,
    AP_MODE_OUTPUT,
    BaseAccessPoint,
    BaseNetwork,
    ContainerNode,
)
from ..constants import DXYZ_FACING, FACING_EN

# TYPE_CHECKING
if 0:
    import typing

    PosData = typing.Tuple[int, int, int]  # x y z
    PosDataWithFacing = typing.Tuple[int, int, int, int]  # x y z facing
# TYPE_CHECKING END

_NT = TypeVar("_NT", bound=BaseNetwork)
_APT = TypeVar("_APT", bound=BaseAccessPoint)


class LogicModule(Generic[_NT, _APT], EventListenerService):
    _instances = {}  # type: dict[str, LogicModule]

    def __init__(
        self,
        network_cls,  # type: type[_NT]
        access_point_cls,  # type: type[_APT]
        transmitter_check_func,  # type: typing.Callable[[str], bool]
        transmittable_block_check_func,  # type: typing.Callable[[str, int, tuple[int, int, int]], bool]
        on_transmittable_block_placed_later,  # type: typing.Callable[[int, int, int, int], None]
        on_network_tick,  # type: typing.Callable[[_NT], None]
        provider_check_func=None,  # type: typing.Callable[[str, int, tuple[int, int, int, int]], bool] | None
        accepter_check_func=None,  # type: typing.Callable[[str, int, tuple[int, int, int, int]], bool] | None
    ):
        EventListenerService.__init__(self, GetMCServerEventBus())
        self.network_cls = network_cls
        self.access_point_cls = access_point_cls
        self.transmitter_check_func = transmitter_check_func
        "方块是否为传输管线方块。"
        self.transmittable_block_check_func = transmittable_block_check_func
        "方块是否为传输目标方块。传入(方块ID, 维度, 方块坐标), 坐标可为None(仅按名称判断, 用于被移除的方块)"
        self.provider_check_func = provider_check_func
        "目标方块是否为传输源检测函数, 传入(方块ID, 维度, 方块坐标+朝向)"
        self.accepter_check_func = accepter_check_func
        "目标方块是否为传输终点检测函数, 传入(方块ID, 维度, 方块坐标+朝向)"
        self.on_network_tick = on_network_tick
        "网络 tick, 5t 触发一次网络 tick"
        self.on_transmittable_block_placed_later = on_transmittable_block_placed_later
        self.networks_pool = set()  # type: set[_NT]
        self.container_nodes_pool = {}  # type: dict[tuple[int, tuple[int, int, int]], ContainerNode[_NT]]
        self.access_points_pool = {}  # type: dict[tuple[int, int, int, int, int], _APT] # (dim, x, y, z, access_facing)
        self.nodes_pool = {}  # type: dict[int, WeakValueDictionary[tuple[int, int, int], _NT]]
        self.enable_listeners()
        self._instances[self.__module__] = self
        self._tick_counter = 0

    def GetContainerNode(self, dim, x, y, z, exists=None, enable_cache=True):
        # type: (int, int, int, int, set[PosData] | None, bool) -> ContainerNode[_NT]
        """
        获取一个容器节点, 内含六个面的输入和提取网络。

        Args:
            dim (int): 维度 ID
            x (int): 容器 x 坐标
            y (int): 容器 y 坐标
            z (int): 容器 z 坐标
            exists (set, optional): 路径缓存set
            enable_cache (bool, optional): 是否允许使用缓存

        Returns:
            tuple[set[TransmitterNetwork], set[TransmitterNetwork]]: 分别表示输入和提取模式的传输网络
        """
        if enable_cache:
            cached_cnode = self.container_nodes_pool.get((dim, (x, y, z)), None)
            if cached_cnode is not None:
                if cached_cnode.inited:
                    return cached_cnode
                else:
                    # 鉴于此时能保证容器节点内此面网络为完整的网络, 使用缓存的完整网络
                    # 需要注意的是, 当新容器加入网络时, 之前的网络则变为不完整 (因为新加入了节点), 此时必须禁用缓存
                    input_networks = cached_cnode.inputs.copy()
                    output_networks = cached_cnode.outputs.copy()
            else:
                input_networks = {}  # type: dict[int, _NT | None]
                output_networks = {}  # type: dict[int, _NT | None]
        else:
            input_networks = {}  # type: dict[int, _NT | None]
            output_networks = {}  # type: dict[int, _NT | None]
        _exists = exists or set()  # type: set[PosData]
        for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            if facing in input_networks:
                if facing not in output_networks:
                    output_networks[facing] = None
                continue
            if facing in output_networks:
                if facing not in input_networks:
                    input_networks[facing] = None
                continue
            next_pos = (x + dx, y + dy, z + dz)
            # old_network = self.nodes_pool.get(dim, {}).get(next_pos)
            network = self.get_and_init_network(dim, next_pos, _exists)
            if network is None:
                input_networks[facing] = output_networks[facing] = None
                continue
            # if old_network is not None:
            #     old_network.flush_from(network)
            self.apply_network_to_pool(network)
            p = self.access_point_cls(
                dim, x + dx, y + dy, z + dz, OPPOSITE_FACING[facing], -1
            )  # -1 表示输入输出模式未知
            if p in network.group_inputs:
                input_networks[facing] = network
                if p not in network.group_outputs:
                    output_networks[facing] = None
            if p in network.group_outputs:
                output_networks[facing] = network
                if p not in network.group_inputs:
                    input_networks[facing] = None
        new_cnode = self.container_nodes_pool[(dim, (x, y, z))] = ContainerNode(
            input_networks, output_networks
        )
        return new_cnode

    def GetNetworkByTransmitter(
        self, dim, x, y, z, cacher=None, disable_cache=False, force_use_cached=False
    ):
        # type: (int, int, int, int, set[PosData] | None, bool, bool) -> _NT | None
        if not disable_cache:
            network = self.nodes_pool.get(dim, {}).get((x, y, z))
            if network is not None:
                return network
        if force_use_cached:
            return None
        return self.get_and_init_network(dim, (x, y, z), cacher)

    def SetAccessPointIOMode(self, access_point, io_mode):
        # type: (_APT, int) -> bool
        """
        设置接入点的传输模式。

        Args:
            access_point (_APT): 接入点
            io_mode (int): 传输模式

        Returns:
            bool: 是否设置成功
        """
        network = access_point.get_bounded_network()
        if not isinstance(network, self.network_cls):
            return False
        cnode = self.GetContainerNode(network.dim, *access_point.target_pos)
        if io_mode == AP_MODE_INPUT:
            cnode.set_face(
                OPPOSITE_FACING[access_point.access_facing], AP_MODE_OUTPUT, None
            )
            network.group_outputs.discard(access_point)
            network.group_inputs.add(access_point)
            cnode.set_face(
                OPPOSITE_FACING[access_point.access_facing], AP_MODE_INPUT, network
            )
        elif io_mode == AP_MODE_OUTPUT:
            cnode.set_face(
                OPPOSITE_FACING[access_point.access_facing], AP_MODE_INPUT, None
            )
            network.group_inputs.discard(access_point)
            network.group_outputs.add(access_point)
            cnode.set_face(
                OPPOSITE_FACING[access_point.access_facing], AP_MODE_OUTPUT, network
            )
        else:
            return False
        self.access_points_pool[
            (
                network.dim,
                access_point.x,
                access_point.y,
                access_point.z,
                access_point.access_facing,
            )
        ] = access_point
        return True

    def transmitter_can_connect(self, block_name, other_block_name):
        # type: (str, str) -> bool
        """
        两个传输管线方块是否能够连接。

        Args:
            block_name (str): 方块 ID
            other_block_name (str): 另一个方块的 ID

        Returns:
            _type_: _description_
        """
        return (
            self.transmitter_check_func(block_name) and block_name == other_block_name
        )

    def can_connect(self, dim, block_name, block_pos, other_block_name, other_pos):
        # type: (int, str, tuple[int, int, int], str, tuple[int, int, int]) -> bool
        return (
            self.transmitter_can_connect(block_name, other_block_name)
            or (
                self.transmittable_block_check_func(block_name, dim, block_pos)
                and self.transmitter_check_func(other_block_name)
            )
            or (
                self.transmittable_block_check_func(other_block_name, dim, other_pos)
                and self.transmitter_check_func(block_name)
            )
        )

    def bfs_find_connections(
        self,
        dim,  # type: int
        start,  # type: PosData
        walked=None,  # type: set[PosData] | None
    ):
        # type: (...) -> _NT | None
        if walked is not None and start in walked:
            return None

        start_bname = GetBlockName(dim, start)
        if start_bname is None:
            return None
        if not self.transmitter_check_func(start_bname):  # 确保 start 一定是管道 !!!
            return None

        output_nodes = set()  # type: set[_APT]
        input_nodes = set()  # type: set[_APT]
        if walked is None:
            walked = set()
        walked.add(start)
        nodes = set()  # type: set[PosData]

        first_transmitter_name = start_bname

        queue = deque([start])
        while queue:
            current = queue.popleft()
            cx, cy, cz = current
            block_states = GetBlockStates(dim, current) or {}

            _i = set()  # type: set[_APT]
            _o = set()  # type: set[_APT]
            for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
                xyz = (cx + dx, cy + dy, cz + dz)
                block_name = GetBlockName(dim, xyz)
                if block_name is None:
                    continue
                elif self.transmitter_check_func(block_name):
                    if first_transmitter_name != block_name:
                        # 不同等级的管道无法并用
                        continue
                    if not block_states.get(
                        "skybluetech:connection_" + FACING_EN[facing], False
                    ):
                        # 该面连接已被扳手切断
                        continue
                    if xyz in walked:
                        continue
                    walked.add(xyz)
                    queue.append(xyz)
                    continue
                elif self.transmittable_block_check_func(block_name, dim, xyz):
                    custom_provider_checker = self.provider_check_func
                    custom_accepter_checker = self.accepter_check_func
                    if (
                        custom_provider_checker is not None
                        and custom_accepter_checker is not None
                    ):
                        posdata = xyz + (OPPOSITE_FACING[facing],)
                        mode = 0
                        if custom_accepter_checker(block_name, dim, posdata):
                            mode |= AP_MODE_INPUT
                        if custom_provider_checker(block_name, dim, posdata):
                            mode |= AP_MODE_OUTPUT
                        if mode == 0:
                            continue
                        ap = self.access_point_cls(dim, cx, cy, cz, facing, mode)
                        if mode & AP_MODE_INPUT:
                            _i.add(ap)
                        if mode & AP_MODE_OUTPUT:
                            _o.add(ap)
                    else:
                        dir_name = FACING_EN[facing]
                        if block_states.get("skybluetech:cable_io_" + dir_name, False):
                            _o.add(
                                self.access_point_cls(
                                    dim, cx, cy, cz, facing, AP_MODE_OUTPUT
                                )
                            )
                        else:
                            _i.add(
                                self.access_point_cls(
                                    dim, cx, cy, cz, facing, AP_MODE_INPUT
                                )
                            )
            input_nodes |= _i
            output_nodes |= _o
            nodes.add(current)
        if first_transmitter_name is None:
            raise ValueError("No transmitter found")
        return self.network_cls(
            dim,
            input_nodes,
            output_nodes,
            nodes,
            first_transmitter_name,
        )

    def get_and_init_network(
        self,
        dim,  # type: int
        start,  # type: PosData
        exists=None,  # type: set[PosData] | None
    ):  # -> Any:
        # type: (...) -> _NT | None
        """
        在管道位置获取并初始化传输网络。

        Args:
            dim (int): 维度 ID
            start (tuple[int, int, int]): 开始坐标
            exists (set, optional): 用于缓存路径点的set

        Returns:
            TransmitterNetwork (optional): 传输网络
        """
        network = self.bfs_find_connections(dim, start, exists)
        if network is None:
            return None
        dim_datas = self.nodes_pool.setdefault(dim, WeakValueDictionary())
        self.networks_pool.add(network)
        for node in network.nodes:
            dim_datas[node] = network
        all_aps = network.group_inputs | network.group_outputs  # type: set[_APT]
        for ap in all_aps:
            self.access_points_pool[
                (network.dim, ap.x, ap.y, ap.z, ap.access_facing)
            ] = ap
        return network

    def clean_nearby_network(self, dim, x, y, z):
        # type: (int, int, int, int) -> None
        """
        清理一个容器附近的所有传输网络。
        一般是容器消失时调用的。

        Args:
            dim (int): 维度 ID
            x (int): x
            y (int): y
            z (int): z
        """
        self.container_nodes_pool.pop((dim, (x, y, z)), None)
        for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
            opposite_facing = OPPOSITE_FACING[facing]
            ax, ay, az = x + dx, y + dy, z + dz
            ap = self.access_points_pool.pop((dim, ax, ay, az, opposite_facing), None)
            if ap is not None:
                bound_network = ap.get_bounded_network()  # type: _NT | None
                if bound_network is not None:
                    bound_network.group_inputs.discard(ap)
                    bound_network.group_outputs.discard(ap)
                else:
                    print(
                        "[ERROR] Transmitter access point {} bound network None".format((
                            dim,
                            x,
                            y,
                            z,
                            facing,
                        ))
                    )

    def delete_network(self, network):
        # type: (_NT) -> None
        "完全清除一个网络。"
        save_network_data = getattr(network, "save_network_data", None)
        if save_network_data is not None:
            save_network_data()
        all_aps = network.group_inputs | network.group_outputs  # type: set[_APT]
        for ap in all_aps:
            res = self.access_points_pool.pop(
                (
                    network.dim,
                    ap.x,
                    ap.y,
                    ap.z,
                    ap.access_facing,
                ),
                None,
            )
            if res is None:
                print("[Error] delete network at ap@{} failed: empty".format(ap))
            cnode = self.container_nodes_pool.get((network.dim, ap.target_pos))
            if cnode is None:
                continue
            cnode.set_face(OPPOSITE_FACING[ap.access_facing], AP_MODE_INPUT, None)
            cnode.set_face(OPPOSITE_FACING[ap.access_facing], AP_MODE_OUTPUT, None)
            if cnode.all_empty():
                self.container_nodes_pool.pop((network.dim, ap.target_pos), None)
        for node in network.nodes.copy():
            self.nodes_pool.get(network.dim, {}).pop(node, None)
        self.networks_pool.discard(network)

    def clean_node(self, dim, x, y, z):
        """
        清理一个管线节点的数据。

        Args:
            dim (int): 维度 ID
            x (int): x
            y (int): y
            z (int): z
        """
        network = self.nodes_pool.get(dim, {}).get((x, y, z), None)
        if network is None:
            network = self.GetNetworkByTransmitter(dim, x, y, z, force_use_cached=True)
        if network is not None:
            self.delete_network(network)
        else:
            print("[Error] can't delete network by transmitter", (x, y, z))
        tmp_set = set()
        for dx, dy, dz in DXYZ_FACING:
            network = self.GetNetworkByTransmitter(
                dim, x + dx, y + dy, z + dz, cacher=tmp_set, disable_cache=True
            )
            if network is not None:
                self.apply_network_to_pool(network)

    def clean_container_networks(self, dim, x, y, z, on_block_placed=False):
        # type: (int, int, int, int, bool) -> None
        """
        清理一个容器周围的网络数据。

        Args:
            dim (int): 维度 ID
            x (int): x
            y (int): y
            z (int): z
        """
        for dx, dy, dz in DXYZ_FACING:
            network = self.GetNetworkByTransmitter(
                dim, x + dx, y + dy, z + dz, force_use_cached=True
            )
            if network is not None:
                self.delete_network(network)
        tmp_set = set()
        self.GetContainerNode(dim, x, y, z, tmp_set, enable_cache=False)

    def refresh_transmitter_connections(self, dim, x, y, z, block_name=None):
        # type: (int, int, int, int, str | None) -> None
        """
        按当前邻居方块刷新管线方块的连接状态。

        区块边缘加载顺序不稳定时, 邻区块方块可能晚一点才可读取,
        且未就绪的区块可能把方块暂时读成空气而不是 None。
        此方法只更新所在区块已加载完成的邻居, 避免把暂时未加载的邻居误写成断开
        (管线间连接只清不补, 一旦误写无法自愈)。
        """
        if not CheckChunkState(dim, (x, y, z)):
            return
        if block_name is None:
            block_name = GetBlockName(dim, (x, y, z))
        if block_name is None or not self.transmitter_check_func(block_name):
            return
        states = {}  # type: dict[str, bool]
        current_states = GetBlockStates(dim, (x, y, z)) or {}
        for dx, dy, dz in NEIGHBOR_BLOCKS_ENUM:
            neighbor_pos = (x + dx, y + dy, z + dz)
            if not CheckChunkState(dim, neighbor_pos):
                continue
            neighbor_name = GetBlockName(dim, neighbor_pos)
            if neighbor_name is None:
                continue
            facing_key = (
                "skybluetech:connection_" + FACING_EN[DXYZ_FACING[(dx, dy, dz)]]
            )
            if self.transmitter_check_func(neighbor_name):
                # 管线间连接可被扳手切断, 这里只清除失效连接, 不自动补连
                states[facing_key] = current_states.get(
                    facing_key, False
                ) and self.transmitter_can_connect(block_name, neighbor_name)
            else:
                states[facing_key] = self.can_connect(
                    dim, block_name, (x, y, z), neighbor_name, neighbor_pos
                )
        if states:
            UpdateBlockStates(dim, (x, y, z), states)

    def refresh_nearby_transmitter_connections(self, dim, x, y, z):
        # type: (int, int, int, int) -> None
        for dx, dy, dz in NEIGHBOR_BLOCKS_ENUM:
            tx, ty, tz = x + dx, y + dy, z + dz
            block_name = GetBlockName(dim, (tx, ty, tz))
            if block_name is not None and self.transmitter_check_func(block_name):
                self.refresh_transmitter_connections(dim, tx, ty, tz, block_name)

    def refresh_loaded_block_entities(self, dim, block_entities):
        # type: (int, list[dict]) -> None
        rebuilt_nodes = set()  # type: set[PosData]
        for block_entity_posdata in block_entities:
            x = block_entity_posdata["posX"]
            y = block_entity_posdata["posY"]
            z = block_entity_posdata["posZ"]
            blockName = block_entity_posdata["blockName"]
            if not self.transmitter_check_func(blockName):
                continue
            self.refresh_transmitter_connections(dim, x, y, z, blockName)
            self.refresh_nearby_transmitter_connections(dim, x, y, z)
            if (x, y, z) in rebuilt_nodes:
                continue
            old_networks = set()
            old_network = self.GetNetworkByTransmitter(
                dim, x, y, z, force_use_cached=True
            )
            if old_network is not None:
                old_networks.add(old_network)
            current_states = GetBlockStates(dim, (x, y, z)) or {}
            for facing, (dx, dy, dz) in enumerate(NEIGHBOR_BLOCKS_ENUM):
                neighbor_pos = (x + dx, y + dy, z + dz)
                neighbor_name = GetBlockName(dim, neighbor_pos)
                if neighbor_name is None or not self.transmitter_can_connect(
                    blockName, neighbor_name
                ):
                    continue
                if not current_states.get(
                    "skybluetech:connection_" + FACING_EN[facing], False
                ):
                    # 连接已被扳手切断, 对侧属于独立网络, 不参与本节点的重建
                    continue
                old_network = self.GetNetworkByTransmitter(
                    dim, x + dx, y + dy, z + dz, force_use_cached=True
                )
                if old_network is not None:
                    old_networks.add(old_network)
            for old_network in old_networks:
                self.delete_network(old_network)
            network = self.GetNetworkByTransmitter(dim, x, y, z, disable_cache=True)
            if network is not None:
                self.apply_network_to_pool(network)
                rebuilt_nodes.update(network.nodes)

        for block_entity_posdata in block_entities:
            x = block_entity_posdata["posX"]
            y = block_entity_posdata["posY"]
            z = block_entity_posdata["posZ"]
            blockName = block_entity_posdata["blockName"]
            if not self.transmittable_block_check_func(blockName, dim, (x, y, z)):
                continue
            self.clean_container_networks(dim, x, y, z)
            self.refresh_nearby_transmitter_connections(dim, x, y, z)

    def apply_network_to_pool(self, network):
        # type: (_NT) -> None
        input_aps = network.group_inputs  # type: set[_APT]
        output_aps = network.group_outputs  # type: set[_APT]
        for ap in input_aps:
            self.container_nodes_pool.setdefault(
                (network.dim, ap.target_pos), ContainerNode()
            ).set_face(OPPOSITE_FACING[ap.access_facing], ap.io_mode, network)
        for ap in output_aps:
            self.container_nodes_pool.setdefault(
                (network.dim, ap.target_pos), ContainerNode()
            ).set_face(OPPOSITE_FACING[ap.access_facing], ap.io_mode, network)

    @EventListenerService.Listen(EntityPlaceBlockAfterServerEvent)
    def onBlockPlaced(self, event):
        # type: (EntityPlaceBlockAfterServerEvent) -> None
        if self.transmitter_check_func(event.fullName):
            states = {}  # type: dict[str, bool]
            for dx, dy, dz in NEIGHBOR_BLOCKS_ENUM:
                old_network = self.GetNetworkByTransmitter(
                    event.dimensionId,
                    event.x + dx,
                    event.y + dy,
                    event.z + dz,
                    force_use_cached=True,
                )
                if old_network is not None:
                    self.delete_network(old_network)
                facing_key = (
                    "skybluetech:connection_" + FACING_EN[DXYZ_FACING[(dx, dy, dz)]]
                )
                bname = GetBlockName(
                    event.dimensionId,
                    (event.x + dx, event.y + dy, event.z + dz),
                )
                if bname is None:
                    continue
                states[facing_key] = (
                    self.transmitter_check_func(bname) and bname == event.fullName
                ) or self.transmittable_block_check_func(
                    bname,
                    event.dimensionId,
                    (event.x + dx, event.y + dy, event.z + dz),
                )
            UpdateBlockStates(event.dimensionId, (event.x, event.y, event.z), states)
            # self.clean_access_point(event.dimensionId, event.x, event.y, event.z)
            # 不再需要, 直接覆盖即可
            network = self.GetNetworkByTransmitter(
                event.dimensionId, event.x, event.y, event.z, disable_cache=True
            )
            if network is not None:
                self.apply_network_to_pool(network)
        elif self.transmittable_block_check_func(
            event.fullName, event.dimensionId, (event.x, event.y, event.z)
        ):
            # 图方便
            self.clean_container_networks(
                event.dimensionId, event.x, event.y, event.z, on_block_placed=True
            )

    @EventListenerService.Listen(BlockNeighborChangedServerEvent)
    def onNeighbourBlockChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        if event.fromBlockName == event.toBlockName:
            return
        if not self.transmitter_check_func(event.blockName):
            return
        dxyz = (
            event.neighborPosX - event.posX,
            event.neighborPosY - event.posY,
            event.neighborPosZ - event.posZ,
        )
        facing_en = FACING_EN[DXYZ_FACING[dxyz]]
        facing_key = "skybluetech:connection_" + facing_en
        neighbor_pos = (
            event.neighborPosX,
            event.neighborPosY,
            event.neighborPosZ,
        )
        to_block_can_connect = self.can_connect(
            event.dimensionId,
            event.toBlockName,
            neighbor_pos,
            event.blockName,
            (event.posX, event.posY, event.posZ),
        )
        # 需要更新连接状态: 以当前状态为准, 不依赖变化前方块名称
        current_states = GetBlockStates(
            event.dimensionId, (event.posX, event.posY, event.posZ)
        ) or {}
        if current_states.get(facing_key, False) != to_block_can_connect:
            if self.transmittable_block_check_func(
                event.toBlockName, event.dimensionId, neighbor_pos
            ):
                UpdateBlockStates(
                    event.dimensionId,
                    (event.posX, event.posY, event.posZ),
                    {facing_key: to_block_can_connect},
                )
            else:
                io_key = "skybluetech:cable_io_" + facing_en
                UpdateBlockStates(
                    event.dimensionId,
                    (event.posX, event.posY, event.posZ),
                    {facing_key: to_block_can_connect, io_key: False},
                )
        if self.transmittable_block_check_func(
            event.toBlockName, event.dimensionId, neighbor_pos
        ):
            ExecLater(
                0,
                lambda: self.on_transmittable_block_placed_later(
                    event.dimensionId,
                    event.neighborPosX,
                    event.neighborPosY,
                    event.neighborPosZ,
                ),
            )

    @EventListenerService.Listen(BlockRemoveServerEvent)
    @Delay(0)  # 等待下一 tick, 此时才能保证此处方块为空
    def onBlockRemoved(self, event):
        # type: (BlockRemoveServerEvent) ->  None
        # NOTE: BlockRemove 的同步回调期间该位置仍读到原方块 (便于最后一刻读取
        # 方块数据), 因此清理必须延迟到下一 tick; 但玩家可能在这 1t 内原地重放
        # 同类方块 (快速拆+放), 此时放置事件已经完成了正确的清理与重建, 若不加
        # 校验直接清理, 会把刚建好的接入点从活网络中永久误删 (2026-07 实证)。
        # 所以延迟处理时必须先确认该处现状: 仍是同类方块则跳过, 交给放置事件。
        current = GetBlockName(event.dimension, (event.x, event.y, event.z))
        # 被移除方块已不存在, 只能按名称判断; 但新连接规则按容器大小判断,
        # 因此同时以该位置是否存在容器节点缓存为准, 避免漏掉按名称无法识别的容器
        has_container_node = (event.dimension, (event.x, event.y, event.z)) in self.container_nodes_pool
        if has_container_node or self.transmittable_block_check_func(event.fullName, event.dimension, (event.x, event.y, event.z)):
            # 是容器
            if current is None or not self.transmittable_block_check_func(
                current, event.dimension, (event.x, event.y, event.z)
            ):
                self.clean_nearby_network(event.dimension, event.x, event.y, event.z)
        if self.transmitter_check_func(event.fullName):
            # 是管道
            if current is None or not self.transmitter_check_func(current):
                self.clean_node(event.dimension, event.x, event.y, event.z)

    @EventListenerService.Listen(ChunkLoadedServerEvent)
    @Delay(1)  # 我也不知道为什么, 过早检测管道会导致区块边缘的一些容器方块检测为空气
    def onChunkLoaded(self, event):
        # type: (ChunkLoadedServerEvent) -> None
        self.refresh_loaded_block_entities(event.dimension, event.blockEntities)

    @EventListenerService.Listen(ChunkAcquireDiscardedServerEvent)
    def onChunkUnloaded(self, event):
        # type: (ChunkAcquireDiscardedServerEvent) -> None
        for block_entity_posdata in event.blockEntities:
            x = block_entity_posdata["posX"]
            y = block_entity_posdata["posY"]
            z = block_entity_posdata["posZ"]
            blockName = block_entity_posdata["blockName"]
            if self.transmitter_check_func(blockName):
                network = self.GetNetworkByTransmitter(
                    event.dimension, x, y, z, force_use_cached=True
                )
                if network is not None:
                    # 只需要直接 discard 即可, 不需要考虑区块重新加载时再加回来
                    # 因为区块重新加载时会重新载入整个网络, 替换掉原来的
                    network._nodes_to_discard.discard((x, y, z))
                    if not network._nodes_to_discard:
                        self.delete_network(network)

    @EventListenerService.Listen(OnSimTickServerEvent)
    def onWorldTick(self, _):
        self._tick_counter += 1
        if self._tick_counter % 5 == 0:
            for network in list(self.networks_pool):
                if not network.enabled:
                    continue
                self.on_network_tick(network)
