# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.timer import Repeat

from ...common.define.belt import OUTPUT_BELTS
from ...common.define.id_enum import TransmitBelt
from ..utils.client_molangs import (
    TRANSMIT_BELT_CONNECT_LEFT,
    TRANSMIT_BELT_CONNECT_RIGHT,
    TRANSMIT_BELT_CONNECT_BACK,
    TRANSMIT_BELT_INCLINE,
)

ENTITY_TYPES = {
    TransmitBelt.BELT: "skybluetech:transmit_belt_entity",
    TransmitBelt.EXTRACTOR: "skybluetech:extractor_belt_entity",
    TransmitBelt.INSERTER: "skybluetech:inserter_belt_entity",
    TransmitBelt.DETECTOR: "skybluetech:detector_belt_entity",
}
# aux 的低两位依次为南、西、北、东。
FACING_OFFSETS = ((0, 1), (-1, 0), (0, -1), (1, 0))
# transmit_belt.json 的状态序号占据其余位，diagonal_up 是第 3 号。
INCLINE_STATUS_INDEX = 3
BELT_MOLANGS = (
    TRANSMIT_BELT_CONNECT_LEFT,
    TRANSMIT_BELT_CONNECT_RIGHT,
    TRANSMIT_BELT_CONNECT_BACK,
    TRANSMIT_BELT_INCLINE,
)

client_entities_pool = {}  # type: dict[tuple[int, int, int, int], BeltModel]
active_dimension = None  # type: int | None


def _is_incline(block):
    return (
        block is not None
        and block[0] == TransmitBelt.BELT
        and block[1] >> 2 == INCLINE_STATUS_INDEX
    )


def _get_model_flags(pos, facing, incline, read_block):
    # type: (tuple[int, int, int], int, bool, object) -> tuple[bool, ...]
    if incline:
        return (False, False, False, True)

    x, y, z = pos
    forward_x, forward_z = FACING_OFFSETS[facing]
    connections = []
    # 实体旋转后的模型左右以运输方向为准，不能套用面对方块正面的左右。
    for side in ((facing + 3) & 3, (facing + 1) & 3, (facing + 2) & 3):
        dx, dz = FACING_OFFSETS[side]
        neighbor = read_block((x + dx, y, z + dz))
        connections.append(
            neighbor is not None
            and neighbor[0] in OUTPUT_BELTS
            and (neighbor[1] & 3) == ((side + 2) & 3)
            and not _is_incline(neighbor)
        )
    lower = read_block((x - forward_x, y - 1, z - forward_z))
    if _is_incline(lower) and (lower[1] & 3) == facing:
        connections[2] = True
    return tuple(connections) + (False,)


class BeltModel(object):
    def __init__(self, key):
        # type: (tuple[int, int, int, int]) -> None
        self.key = key
        self.forget_model()

    def forget_model(self):
        self.entity_id = None  # type: str | None
        self.block_name = None  # type: str | None
        self.facing = None  # type: int | None
        self.model_flags = None  # type: tuple[bool, ...] | None

    def destroy_model(self):
        if self.entity_id is not None:
            GetClient().DestroyClientEntity(self.entity_id)
        self.forget_model()

    def update(self, read_block):
        pos = self.key[1:]
        block_name, aux = read_block(pos) or (None, 0)
        if block_name not in ENTITY_TYPES:
            self.destroy_model()
            return
        facing = aux & 3
        if self.entity_id is None or (block_name, facing) != (self.block_name, self.facing):
            self.destroy_model()
            self.entity_id = GetClient().CreateClientEntityByTypeStr(
                ENTITY_TYPES[block_name],
                (pos[0] + 0.5, pos[1], pos[2] + 0.5),
                (0, 180 + facing * 90),
            )
            if self.entity_id is None:
                return
            self.block_name = block_name
            self.facing = facing
            CF.CreateModel(self.entity_id).SetEntityShadowShow(False)
        if block_name != TransmitBelt.BELT:
            return
        model_flags = _get_model_flags(pos, facing, _is_incline((block_name, aux)), read_block)
        if model_flags == self.model_flags:
            return
        applied = True
        for index, molang in enumerate(BELT_MOLANGS):
            if self.model_flags is None or model_flags[index] != self.model_flags[index]:
                if not molang.set_to_entity(self.entity_id, float(model_flags[index])):
                    applied = False
        self.model_flags = model_flags if applied else None


def _sync_dimension():
    # type: () -> int
    global active_dimension
    dimension = CF.CreateGame(LEVEL_ID).GetCurrentDimension()
    if dimension != active_dimension:
        # 引擎切维时会删除客户端实体；保留常加载区坐标，返回时未必重发 loaded。
        for model in client_entities_pool.values():
            model.forget_model()
        active_dimension = dimension
    return dimension


def _refresh_models(keys, removed_key=None):
    dimension = _sync_dimension()
    if dimension < 0:
        return
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    blocks = {}
    if removed_key is not None and removed_key[0] == dimension:
        # remove 回调中 GetBlock 可能仍返回旧方块，只覆盖这一次局部快照。
        blocks[removed_key[1:]] = None

    def read_block(pos):
        if pos not in blocks:
            blocks[pos] = block_info.GetBlock(pos)
        return blocks[pos]

    for key in keys:
        if key[0] != dimension:
            continue
        model = client_entities_pool.get(key)
        if model is not None:
            model.update(read_block)


def _refresh_nearby(key, removed=False):
    dim, x, y, z = key
    keys = [key]
    keys.extend(
        (dim, x + dx, y + dy, z + dz)
        for dx, dz in FACING_OFFSETS
        for dy in (0, 1)
    )
    _refresh_models(keys, key if removed else None)


def _remove_model(key):
    model = client_entities_pool.pop(key, None)
    if model is not None:
        model.destroy_model()


@asModBlockLoadedListener(TransmitBelt.BELT)
@asModBlockLoadedListener(TransmitBelt.EXTRACTOR)
@asModBlockLoadedListener(TransmitBelt.INSERTER)
@asModBlockLoadedListener(TransmitBelt.DETECTOR)
def onTransmitBeltLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    _sync_dimension()
    key = (event.dimensionId, event.posX, event.posY, event.posZ)
    _remove_model(key)
    client_entities_pool[key] = BeltModel(key)
    _refresh_nearby(key)


@asModBlockRemovedListener(TransmitBelt.BELT)
@asModBlockRemovedListener(TransmitBelt.EXTRACTOR)
@asModBlockRemovedListener(TransmitBelt.INSERTER)
@asModBlockRemovedListener(TransmitBelt.DETECTOR)
def onTransmitBeltRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    _sync_dimension()
    key = (event.dimensionId, event.posX, event.posY, event.posZ)
    _remove_model(key)
    _refresh_nearby(key, removed=True)


@ClientInitCallback()
@Repeat(0.2)
def update_belt_models():
    if client_entities_pool:
        _refresh_models(tuple(client_entities_pool))


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(event):
    # type: (DimensionChangeClientEvent) -> None
    # 以本地实际维度判断，其他玩家的事件不会清除本地实体。
    _refresh_models(tuple(client_entities_pool))


@ClientUninitCallback()
def on_client_exit():
    global active_dimension
    _sync_dimension()
    for key in tuple(client_entities_pool):
        _remove_model(key)
    active_dimension = None
