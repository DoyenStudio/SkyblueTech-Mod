# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.facing import (
    NEIGHBOR_BLOCKS_ENUM,
    OPPOSITE_FACING,
)
from skybluetech_scripts.skybluetech.common.define.id_enum.items import (
    TRANSMITTER_SETTINGS_WRENCH,
    TRANSMITTER_WRENCH,
)
from skybluetech_scripts.skybluetech.common.events.misc.transmitter_settings import (
    TransmitterSetLabel,
    TransmitterSetPriority,
    TransmitterSwitchAccessMode,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetBlockStates,
    GetPlayerDimensionId,
    IsSneaking,
    SetOnePopupNotice,
    UpdateBlockStates,
)
from skybluetech_scripts.tooldelta.events.event_bus import GetMCServerEventBus
from skybluetech_scripts.tooldelta.events.server import (
    PushUIRequest,
    ServerBlockUseEvent,
    ServerItemUseOnEvent,
)
from skybluetech_scripts.tooldelta.events.service import EventListenerService
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter

from ..base.define import AP_MODE_INPUT, AP_MODE_OUTPUT
from ..constants import FACING_EN, FACING_ZHCN
from .logic import (
    _APT,
    _NT,
    Generic,
    LogicModule,
)

SNEAK_CUT_RATE_LIMIT = 0.5

# 潜行右键会每 tick 触发一次 ServerItemUseOnEvent, 用限速器把一次长按收敛成一次操作
sneak_cut_limiter = PlayerRateLimiter(SNEAK_CUT_RATE_LIMIT)


class ActionModule(Generic[_NT, _APT], EventListenerService):
    def __init__(
        self,
        logic_module,  # type: LogicModule[_NT, _APT]
        wrench_pick_threshold=5.0 / 16,
        enable_io_mode_settings=True,
        enable_label_settings=True,
    ):
        EventListenerService.__init__(self, GetMCServerEventBus())
        self.logic_module = logic_module
        self.wrench_pick_threshold = wrench_pick_threshold
        self.enable_io_mode_settings = enable_io_mode_settings
        self.enable_label_settings = enable_label_settings
        self.enable_listeners()

    def get_pick_facing(self, clickX, clickY, clickZ, face):
        # type: (float, float, float, int) -> int | None
        THR = self.wrench_pick_threshold  # 侧面立方体长度, 同时也是中心立方体的最小坐标
        CMAX = 1.0 - THR  # 中心立方体的最大坐标
        # 点击某个面时, 4个垂直方向的延伸体在该面上有投影区域
        # 判断点击坐标落在哪个投影里, 从而得知玩家想设置哪个方向
        # face 0(down)/1(up) → 检查 X,Z 轴
        # face 2(north)/3(south) → 检查 X,Y 轴
        # face 4(west)/5(east) → 检查 Z,Y 轴
        if face <= 1:
            a1, a2 = clickX, clickZ
            dirs1 = (4, 5)  # west, east
            dirs2 = (2, 3)  # north, south
        elif face <= 3:
            a1, a2 = clickX, clickY
            dirs1 = (4, 5)  # west, east
            dirs2 = (0, 1)  # down, up
        else:
            a1, a2 = clickZ, clickY
            dirs1 = (2, 3)  # north, south
            dirs2 = (0, 1)  # down, up
        r1 = r2 = None
        p1 = p2 = 0.0
        if a1 < THR:
            r1, p1 = dirs1[0], THR - a1
        elif a1 > CMAX:
            r1, p1 = dirs1[1], a1 - CMAX
        if a2 < THR:
            r2, p2 = dirs2[0], THR - a2
        elif a2 > CMAX:
            r2, p2 = dirs2[1], a2 - CMAX
        if r1 is None and r2 is None:
            return None  # 中心区域
        if r1 is None:
            return r2
        if r2 is None:
            return r1
        # 角落区域, 两个方向都有投影, 取深入程度更大的
        return r1 if p1 >= p2 else r2

    def _pick_cut_link_facing(self, event):
        # type: (ServerBlockUseEvent | ServerItemUseOnEvent) -> int | None
        # 连接被切断后连接臂缩回, 玩家只能点到中心方块朝向邻居的面 (中心区域);
        # 此时以被点击面的朝向作为目标方向。臂存在时该面被邻居方块遮挡, 无歧义。
        # 可连接的邻居包含机器, 这样断开的机器-管道连接也能被点回来。
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[event.face]
        next_pos = (event.x + dx, event.y + dy, event.z + dz)
        next_block = GetBlockName(event.dimensionId, next_pos)
        if next_block is None:
            return None
        if self.logic_module.can_connect(
            event.dimensionId,
            event.blockName,
            (event.x, event.y, event.z),
            next_block,
            next_pos,
        ):
            return event.face
        return None

    def resolve_wrench_facing(self, event):
        # type: (ServerBlockUseEvent | ServerItemUseOnEvent) -> int | None
        "取扳手点击的目标面: 先看点击位置落在哪个延伸体上, 再看被点击的面本身。"
        face = self.get_pick_facing(event.clickX, event.clickY, event.clickZ, event.face)
        if face is None:
            face = self._pick_cut_link_facing(event)
        return face

    def toggle_transmitter_link(self, dim, x, y, z, face, player_id=None):
        # type: (int, int, int, int, int, str | None) -> bool
        "切断/恢复此面与相邻管道或机器之间的连接, 并重建相关网络。"
        states = GetBlockStates(dim, (x, y, z))
        if states is None:
            return False
        block_name = GetBlockName(dim, (x, y, z))
        if block_name is None:
            return False
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[face]
        neighbor_pos = (x + dx, y + dy, z + dz)
        neighbor_name = GetBlockName(dim, neighbor_pos)
        facing_key = "skybluetech:connection_" + FACING_EN[face]
        connect = not states.get(facing_key, False)
        is_transmitter = (
            neighbor_name is not None
            and self.logic_module.transmitter_check_func(neighbor_name)
        )
        if connect and not (
            neighbor_name is not None
            and self.logic_module.can_connect(
                dim, block_name, (x, y, z), neighbor_name, neighbor_pos
            )
        ):
            if player_id is not None:
                if is_transmitter:
                    SetOnePopupNotice(
                        player_id,
                        "§6不同种类的管道无法互相连接",
                        "§7[§cx§7] §c错误",
                    )
                else:
                    SetOnePopupNotice(
                        player_id,
                        "§6此方向没有可连接的管道或容器",
                        "§7[§cx§7] §c错误",
                    )
            return False
        UpdateBlockStates(dim, (x, y, z), {facing_key: connect})
        if is_transmitter:
            # 管道之间的连接状态需要两侧同时记录
            UpdateBlockStates(
                dim,
                neighbor_pos,
                {"skybluetech:connection_" + FACING_EN[OPPOSITE_FACING[face]]: connect},
            )
        elif neighbor_name is not None:
            # 机器一侧的插座模型需要跟着显示 / 隐藏
            self.logic_module.refresh_machine_socket(dim, neighbor_pos, (x, y, z))
        logic = self.logic_module
        if neighbor_name is not None and not is_transmitter:
            # 机器: 容器节点的缓存与相邻网络都要按新状态重建
            logic.clean_container_networks(dim, *neighbor_pos)
        else:
            old_networks = set()
            for px, py, pz in ((x, y, z), neighbor_pos):
                network = logic.GetNetworkByTransmitter(
                    dim, px, py, pz, force_use_cached=True
                )
                if network is not None:
                    old_networks.add(network)
            for network in old_networks:
                logic.delete_network(network)
            tmp_set = set()
            for px, py, pz in ((x, y, z), neighbor_pos):
                network = logic.GetNetworkByTransmitter(
                    dim, px, py, pz, cacher=tmp_set, disable_cache=True
                )
                if network is not None:
                    logic.apply_network_to_pool(network)
        if player_id is not None:
            if is_transmitter:
                target = "管道"
            else:
                target = "容器"
            if connect:
                SetOnePopupNotice(
                    player_id,
                    "§f已连接管道的§6"
                    + FACING_ZHCN[face]
                    + "§f面与"
                    + target,
                )
            else:
                SetOnePopupNotice(
                    player_id,
                    "§f已断开管道§6"
                    + FACING_ZHCN[face]
                    + "§f面与"
                    + target
                    + "§f的连接",
                )
        return True

    def switch_access_mode(self, dim, x, y, z, face, player_id=None):
        # type: (int, int, int, int, int, str | None) -> bool
        if not self.enable_io_mode_settings:
            return False
        block_name = GetBlockName(dim, (x, y, z))
        if block_name is None:
            return False
        block_orig_status = GetBlockStates(dim, (x, y, z))
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[face]
        nextBlock = GetBlockName(dim, (x + dx, y + dy, z + dz))
        if nextBlock is None or self.logic_module.transmitter_check_func(nextBlock):
            if player_id is not None:
                SetOnePopupNotice(
                    player_id,
                    "§6无法为已连接了另外一根管道的管道设置传输模式",
                    "§7[§cx§7] §c错误",
                )
            return False
        elif not self.logic_module.can_connect(
            dim, nextBlock, (x + dx, y + dy, z + dz), block_name, (x, y, z)
        ):
            if player_id is not None:
                SetOnePopupNotice(
                    player_id,
                    "§6无法为未连接的管道设置传输模式",
                    "§7[§cx§7] §c错误",
                )
            return False
        facing_en_key = "skybluetech:cable_io_" + FACING_EN[face]
        newState = not block_orig_status.get(facing_en_key, False)
        block_orig_status[facing_en_key] = newState
        current_network = self.logic_module.GetNetworkByTransmitter(dim, x, y, z)
        if current_network is None:
            if player_id is not None:
                SetOnePopupNotice(player_id, "§4管道数据异常", "§7[§cx§7] §c错误")
            return False
        if newState:
            ap = self.logic_module.access_point_cls(dim, x, y, z, face, AP_MODE_OUTPUT)
            ap.bound_network(current_network)
            ok = self.logic_module.SetAccessPointIOMode(ap, AP_MODE_OUTPUT)
        else:
            ap = self.logic_module.access_point_cls(dim, x, y, z, face, AP_MODE_INPUT)
            ap.bound_network(current_network)
            ok = self.logic_module.SetAccessPointIOMode(ap, AP_MODE_INPUT)
        if ok:
            if player_id is not None:
                SetOnePopupNotice(
                    player_id,
                    "§f已将管道的§6"
                    + FACING_ZHCN[face]
                    + "§f面设置为"
                    + ("§a输入", "§c抽出")[newState],
                )
        else:
            if player_id is not None:
                SetOnePopupNotice(
                    player_id,
                    "§6无法将管道的§6"
                    + FACING_ZHCN[face]
                    + "§6面设置为"
                    + ("§a输入", "§c抽出")[newState],
                )
        UpdateBlockStates(dim, (x, y, z), block_orig_status)
        return True

    @EventListenerService.Listen(ServerItemUseOnEvent)
    def onPlayerSneakUseWrench(self, event):
        # type: (ServerItemUseOnEvent) -> None
        """
        潜行 + 右键管道: 断开 / 恢复这一面的连接。

        潜行右键不会触发 ServerBlockUseEvent, 而是走 ServerItemUseOnEvent,
        按住不放时每 tick 触发一次, 因此这里单独处理并用限速器收敛。
        """
        if event.item is None or event.item.newItemName != TRANSMITTER_WRENCH:
            return
        if not IsSneaking(event.entityId):
            return
        if not self.logic_module.transmitter_check_func(event.blockName):
            return
        event.cancel()
        if not sneak_cut_limiter.record(event.entityId):
            return
        face = self.resolve_wrench_facing(event)
        if face is None:
            SetOnePopupNotice(event.entityId, "无效扳手调节位置")
            return
        self.toggle_transmitter_link(
            event.dimensionId, event.x, event.y, event.z, face, event.entityId
        )

    @EventListenerService.Listen(ServerBlockUseEvent)
    def onPlayerUseWrench(self, event):
        # type: (ServerBlockUseEvent) -> None
        if not self.logic_module.transmitter_check_func(event.blockName):
            return
        if event.item.newItemName == TRANSMITTER_WRENCH:
            face = self.resolve_wrench_facing(event)
            if face is None:
                SetOnePopupNotice(event.playerId, "无效扳手调节位置")
                return
            dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[face]
            next_block = GetBlockName(
                event.dimensionId, (event.x + dx, event.y + dy, event.z + dz)
            )
            if IsSneaking(event.playerId):
                # 潜行点击: 断开 / 恢复此面的连接 (机器与管道之间同样适用)
                # 潜行时一般走 ServerItemUseOnEvent, 这里只作兜底
                if sneak_cut_limiter.record(event.playerId):
                    self.toggle_transmitter_link(
                        event.dimensionId,
                        event.x,
                        event.y,
                        event.z,
                        face,
                        event.playerId,
                    )
                return
            if next_block is not None and self.logic_module.transmitter_check_func(
                next_block
            ):
                if next_block == event.blockName:
                    self.toggle_transmitter_link(
                        event.dimensionId,
                        event.x,
                        event.y,
                        event.z,
                        face,
                        event.playerId,
                    )
                else:
                    SetOnePopupNotice(
                        event.playerId,
                        "§6不同种类的管道无法互相连接",
                        "§7[§cx§7] §c错误",
                    )
            else:
                if not self.enable_io_mode_settings:
                    # 电线没有输入 / 提取模式可切换, 按无效位置处理
                    SetOnePopupNotice(event.playerId, "无效扳手调节位置")
                    return
                self.switch_access_mode(
                    event.dimensionId, event.x, event.y, event.z, face, event.playerId
                )
        elif event.item.newItemName == TRANSMITTER_SETTINGS_WRENCH:
            if not self.enable_label_settings:
                return
            facing = self.get_pick_facing(
                event.clickX, event.clickY, event.clickZ, event.face
            )
            if facing is None:
                SetOnePopupNotice(event.playerId, "无效扳手设置位置")
                return
            ap = self.logic_module.access_points_pool.get((
                event.dimensionId,
                event.x,
                event.y,
                event.z,
                facing,
            ))
            if ap is None:
                self.logic_module.GetNetworkByTransmitter(
                    event.dimensionId, event.x, event.y, event.z
                )  # 需要激活一次
                ap = self.logic_module.access_points_pool.get((
                    event.dimensionId,
                    event.x,
                    event.y,
                    event.z,
                    facing,
                ))
                if ap is None:
                    SetOnePopupNotice(
                        event.playerId, "管道此面没有邻接容器， 无法进行设置"
                    )
                    return
            PushUIRequest(
                "TransmitterSettingsUI.main",
                params={
                    "dim": event.dimensionId,
                    "x": event.x,
                    "y": event.y,
                    "z": event.z,
                    "side": ap.access_facing,
                    "label": ap.get_label(),
                    "priority": ap.get_priority(),
                },
            ).send(event.playerId)

    @EventListenerService.Listen(TransmitterSwitchAccessMode)
    def onSwitchAccessMode(self, event):
        # type: (TransmitterSwitchAccessMode) -> None
        if event.transmitter_type != self.logic_module.network_cls.network_type:
            return
        self.switch_access_mode(
            GetPlayerDimensionId(event.pid),
            event.x,
            event.y,
            event.z,
            event.facing,
            event.pid,
        )

    @EventListenerService.Listen(TransmitterSetLabel)
    def onSetLabel(self, event):
        # type: (TransmitterSetLabel) -> None
        if not self.enable_label_settings:
            return
        if not isinstance(event.label, int) or event.label < 0 or event.label > 100000:
            return
        ap = self.logic_module.access_points_pool.get((
            GetPlayerDimensionId(event.pid),
            event.x,
            event.y,
            event.z,
            event.facing,
        ))
        if ap is None:
            return
        ap.set_label(event.label)

    @EventListenerService.Listen(TransmitterSetPriority)
    def onSetPriority(self, event):
        # type: (TransmitterSetPriority) -> None
        if not self.enable_label_settings:
            return
        if (
            not isinstance(event.priority, int)
            or event.priority < -100000
            or event.priority > 100000
        ):
            return
        ap = self.logic_module.access_points_pool.get((
            GetPlayerDimensionId(event.pid),
            event.x,
            event.y,
            event.z,
            event.facing,
        ))
        if ap is None:
            return
        ap.set_priority(event.priority)
