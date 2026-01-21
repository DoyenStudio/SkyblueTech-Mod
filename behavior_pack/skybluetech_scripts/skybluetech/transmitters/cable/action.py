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
from ...define.events.misc.transmitter_settings import (
    TransmitterSetLabel, TransmitterSetPriority
)
from ...define.id_enum.items import TRANSMITTER_WRENCH, TRANSMITTER_SETTINGS_WRENCH
from ...define.facing import NEIGHBOR_BLOCKS_ENUM
from ..constants import FACING_EN, FACING_ZHCN
from .define import CableAccessPoint, AP_MODE_INPUT, AP_MODE_OUTPUT
from .logic import isCable, canConnect, GetNetworkByCable, GetNearbyCableNetworks
from .pool import CableAccessPointPool, CableNetworkPool


PIECE = 5.0 / 16

def get_testing_facing(clickX, clickY, clickZ):
    # type: (float, float, float) -> int | None
    if clickY > 0 and clickY < PIECE:
        return 0  # down
    elif clickY > 1 - PIECE and clickY < 1:
        return 1
    elif clickZ > 0 and clickZ < PIECE:
        return 2  # north
    elif clickZ > 1 - PIECE and clickZ < 1:
        return 3  # south
    elif clickX > 0 and clickX < PIECE:
        return 4  # west
    elif clickX > 1 - PIECE and clickX < 1:
        return 5  # east
    else:
        return None

@ServerBlockUseEvent.Listen()
def onPlayerUseWrench(event):
    # type: (ServerBlockUseEvent) -> None
    if not isCable(event.blockName):
        return
    if event.item.newItemName == TRANSMITTER_WRENCH:
        blockX = event.x
        blockY = event.y
        blockZ = event.z
        block_orig_status = GetBlockStates(event.dimensionId, (blockX, blockY, blockZ))
        facing = get_testing_facing(event.clickX, event.clickY, event.clickZ)
        if facing is None:
            SetOnePopupNotice(event.playerId, "无效扳手调节位置")
            return
        dx, dy, dz = NEIGHBOR_BLOCKS_ENUM[facing]
        nextBlock = GetBlockName(event.dimensionId, (blockX + dx, blockY + dy, blockZ + dz))
        if nextBlock is None or isCable(nextBlock):
            SetOnePopupNotice(
                event.playerId,
                "§6无法为已连接了另外一根管道的管道设置传输模式",
                "§7[§cx§7] §c错误",
            )
            return
        elif not canConnect(nextBlock):
            SetOnePopupNotice(
                event.playerId, "§6无法为未连接的管道设置传输模式", "§7[§cx§7] §c错误"
            )
            return
        facing_en_key = "skybluetech:cable_io_" + FACING_EN[facing]
        newState = not block_orig_status.get(facing_en_key, False)
        block_orig_status[facing_en_key] = newState
        current_network = GetNetworkByCable(event.dimensionId, blockX, blockY, blockZ)
        if current_network is None:
            SetOnePopupNotice(event.playerId, "§4管道数据异常", "§7[§cx§7] §c错误")
            return
        if newState:
            ap = CableAccessPoint(
                event.dimensionId,
                blockX,
                blockY,
                blockZ,
                facing,
                AP_MODE_OUTPUT
            )
            ap.bound_network(current_network)
            i, o = GetNearbyCableNetworks(event.dimensionId, *ap.target_pos)
            i.remove(current_network)
            current_network.group_inputs.remove(ap)
            current_network.group_outputs.add(ap)
            o.append(current_network)
            CableAccessPointPool[(ap.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap
        else:
            ap = CableAccessPoint(
                event.dimensionId,
                blockX,
                blockY,
                blockZ,
                facing,
                AP_MODE_INPUT
            )
            ap.bound_network(current_network)
            i, o = GetNearbyCableNetworks(event.dimensionId, *ap.target_pos)
            o.remove(current_network)
            current_network.group_inputs.add(ap)
            current_network.group_outputs.remove(ap)
            i.append(current_network)
            CableAccessPointPool[(ap.dim, ap.x, ap.y, ap.z, ap.access_facing)] = ap
        SetOnePopupNotice(
            event.playerId,
            "§f已将管道的§6"
            + FACING_ZHCN[facing]
            + "§f面设置为"
            + ("§a输入", "§c抽出")[newState],
        )
        UpdateBlockStates(event.dimensionId, (blockX, blockY, blockZ), block_orig_status)
    elif event.item.newItemName == TRANSMITTER_SETTINGS_WRENCH:
        facing = get_testing_facing(event.clickX, event.clickY, event.clickZ)
        if facing is None:
            SetOnePopupNotice(event.playerId, "无效扳手设置位置")
            return
        ap = CableAccessPointPool.get((event.dimensionId, event.x, event.y, event.z, facing))
        if ap is None:
            GetNetworkByCable(
                event.dimensionId,
                event.x, event.y, event.z
            ) # 需要激活一次
            ap = CableAccessPointPool.get((event.dimensionId, event.x, event.y, event.z, facing))
            if ap is None:
                SetOnePopupNotice(event.playerId, "管道此面没有邻接容器， 无法进行设置")
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
            }
        ).send(event.playerId)

@TransmitterSetLabel.Listen()
def onSetLabel(event):
    # type: (TransmitterSetLabel) -> None
    if not isinstance(event.label, int) or event.label < 0 or event.label > 100000:
        return
    ap = CableAccessPointPool.get((event.dim, event.x, event.y, event.z, event.facing))
    if ap is None:
        return
    ap.set_label(event.label)

@TransmitterSetPriority.Listen()
def onSetPriority(event):
    # type: (TransmitterSetPriority) -> None
    if not isinstance(event.priority, int) or event.priority < -100000 or event.priority > 100000:
        return
    ap = CableAccessPointPool.get((event.dim, event.x, event.y, event.z, event.facing))
    if ap is None:
        return
    ap.set_priority(event.priority)
