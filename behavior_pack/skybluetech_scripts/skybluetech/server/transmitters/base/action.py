# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import (
    ServerBlockUseEvent,
    PushUIRequest,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetBlockName,
    GetBlockStates,
    UpdateBlockStates,
    SetOnePopupNotice,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.events.service import ServerListenerService
from ....common.events.misc.transmitter_settings import (
    TransmitterSetLabel,
    TransmitterSetPriority,
)
from ....common.define.id_enum.items import (
    TRANSMITTER_WRENCH,
    TRANSMITTER_SETTINGS_WRENCH,
)
from ....common.define.facing import NEIGHBOR_BLOCKS_ENUM, OPPOSITE_FACING
from ..base.define import AP_MODE_INPUT, AP_MODE_OUTPUT
from ..constants import FACING_EN, FACING_ZHCN
from .logic import (
    LogicModule,
    Generic,
    _NT,
    _APT,
)


class ActionModule(Generic[_NT, _APT], ServerListenerService):
    def __init__(
        self,
        logic_module,  # type: LogicModule[_NT, _APT]
        wrench_pick_threshold=5.0 / 16,
        enable_io_mode_settings=True,
        enable_label_settings=True,
    ):
        ServerListenerService.__init__(self)
        self.logic_module = logic_module
        self.wrench_pick_threshold = wrench_pick_threshold
        self.enable_io_mode_settings = enable_io_mode_settings
        self.enable_label_settings = enable_label_settings
        self.enable_listeners()

    def get_testing_facing(self, clickX, clickY, clickZ):
        # type: (float, float, float) -> int | None
        THR = self.wrench_pick_threshold
        if clickY > 0 and clickY < THR:
            return 0  # down
        elif clickY > 1 - THR and clickY < 1:
            return 1
        elif clickZ > 0 and clickZ < THR:
            return 2  # north
        elif clickZ > 1 - THR and clickZ < 1:
            return 3  # south
        elif clickX > 0 and clickX < THR:
            return 4  # west
        elif clickX > 1 - THR and clickX < 1:
            return 5  # east
        else:
            return None

    @ServerListenerService.Listen(ServerBlockUseEvent)
    def onPlayerUseWrench(self, event):
        # type: (ServerBlockUseEvent) -> None
        if not self.logic_module.transmitter_check_func(event.blockName):
            return
        if event.item.newItemName == TRANSMITTER_WRENCH:
            if not self.enable_io_mode_settings:
                return
            blockX = event.x
            blockY = event.y
            blockZ = event.z
            block_orig_status = GetBlockStates(
                event.dimensionId, (blockX, blockY, blockZ)
            )
            facing = self.get_testing_facing(event.clickX, event.clickY, event.clickZ)
            if facing is None:
                SetOnePopupNotice(event.playerId, "无效扳手调节位置")
                return
            dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[facing]
            nextBlock = GetBlockName(
                event.dimensionId, (blockX + dx, blockY + dy, blockZ + dz)
            )
            if nextBlock is None or self.logic_module.transmitter_check_func(nextBlock):
                SetOnePopupNotice(
                    event.playerId,
                    "§6无法为已连接了另外一根管道的管道设置传输模式",
                    "§7[§cx§7] §c错误",
                )
                return
            elif not self.logic_module.can_connect(nextBlock, event.blockName):
                SetOnePopupNotice(
                    event.playerId,
                    "§6无法为未连接的管道设置传输模式",
                    "§7[§cx§7] §c错误",
                )
                return
            facing_en_key = "skybluetech:cable_io_" + FACING_EN[facing]
            newState = not block_orig_status.get(facing_en_key, False)
            block_orig_status[facing_en_key] = newState
            current_network = self.logic_module.GetNetworkByTransmitter(
                event.dimensionId, blockX, blockY, blockZ
            )
            if current_network is None:
                SetOnePopupNotice(event.playerId, "§4管道数据异常", "§7[§cx§7] §c错误")
                return
            if newState:
                ap = self.logic_module.access_point_cls(
                    event.dimensionId, blockX, blockY, blockZ, facing, AP_MODE_OUTPUT
                )
                ap.bound_network(current_network)
                ok = self.logic_module.SetAccessPointIOMode(ap, AP_MODE_OUTPUT)
            else:
                ap = self.logic_module.access_point_cls(
                    event.dimensionId, blockX, blockY, blockZ, facing, AP_MODE_INPUT
                )
                ap.bound_network(current_network)
                ok = self.logic_module.SetAccessPointIOMode(ap, AP_MODE_INPUT)
            if ok:
                SetOnePopupNotice(
                    event.playerId,
                    "§f已将管道的§6"
                    + FACING_ZHCN[facing]
                    + "§f面设置为"
                    + ("§a输入", "§c抽出")[newState],
                )
            else:
                SetOnePopupNotice(
                    event.playerId,
                    "§6无法将管道的§6"
                    + FACING_ZHCN[facing]
                    + "§6面设置为"
                    + ("§a输入", "§c抽出")[newState],
                )
            UpdateBlockStates(
                event.dimensionId, (blockX, blockY, blockZ), block_orig_status
            )
        elif event.item.newItemName == TRANSMITTER_SETTINGS_WRENCH:
            if not self.enable_label_settings:
                return
            facing = self.get_testing_facing(event.clickX, event.clickY, event.clickZ)
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

    @ServerListenerService.Listen(TransmitterSetLabel)
    def onSetLabel(self, event):
        # type: (TransmitterSetLabel) -> None
        if not self.enable_label_settings:
            return
        if not isinstance(event.label, int) or event.label < 0 or event.label > 100000:
            return
        ap = self.logic_module.access_points_pool.get((
            event.dim,
            event.x,
            event.y,
            event.z,
            event.facing,
        ))
        if ap is None:
            return
        ap.set_label(event.label)

    @ServerListenerService.Listen(TransmitterSetPriority)
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
            event.dim,
            event.x,
            event.y,
            event.z,
            event.facing,
        ))
        if ap is None:
            return
        ap.set_priority(event.priority)
