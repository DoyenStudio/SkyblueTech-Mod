# coding=utf-8
from math import isinf, isnan

from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent,
    OnLocalPlayerStopLoading,
)
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import (
    ClientInitCallback,
    ClientUninitCallback,
)
from skybluetech_scripts.tooldelta.utils.nbt import ValueOf
from skybluetech_scripts.tooldelta.utils.timer import ExecLater, Repeat
from skybluetech_scripts.skybluetech.common.define.id_enum import BrineEvaporationPond
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
    K_DESTROY_FLAG,
)
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    K_FLUID_CAPACITY,
    K_FLUID_RENDER_ORIGIN,
    K_FLUID_RENDER_SIZE,
    K_FLUID_VOLUMES,
)
from skybluetech_scripts.skybluetech.client.utils.fluid_model import FluidVolumeModel

FLUID_SURFACE_INSET = 0.004
loaded_ponds = {}  # type: dict[tuple[int, int, int, int], PondFluidDisplay]


def _read_vector(data, key):
    # type: (dict, str) -> tuple[float, float, float] | None
    values = ValueOf(data.get(key))
    if not isinstance(values, (tuple, list)) or len(values) != 3:
        return None
    try:
        values = tuple(float(ValueOf(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return None
    if any(isnan(value) or isinf(value) for value in values):
        return None
    return values


def _read_fluid_surface(data):
    input_fluid = FluidSlotClient(data, 0)
    output_fluid = FluidSlotClient(data, 1)
    # 各快照是该方向液量最多的一种液体的同种汇总；相等时选择输入。
    fluid = input_fluid if input_fluid.volume >= output_fluid.volume else output_fluid
    # 选种保持不变；分子只计该种液体的全池储量，分母计全部接口容量。
    pool_volumes = ValueOf(data.get(K_FLUID_VOLUMES))
    if not fluid.fluid_id or not isinstance(pool_volumes, dict):
        return None
    try:
        volume = float(ValueOf(pool_volumes.get(fluid.fluid_id)) or 0.0)
        max_volume = float(ValueOf(data.get(K_FLUID_CAPACITY)) or 0.0)
    except (TypeError, ValueError, OverflowError):
        return None
    if (
        volume <= 0.0
        or max_volume <= 0.0
        or isnan(volume)
        or isinf(volume)
        or isnan(max_volume)
        or isinf(max_volume)
    ):
        return None
    return fluid.fluid_id, max(0.0, min(1.0, volume / max_volume))


class PondFluidDisplay(object):
    def __init__(self):
        self.model = None  # type: FluidVolumeModel | None
        self.model_origin = None
        self.applied_state = None

    def clear_model(self):
        if self.model is not None:
            self.model.Destroy()
        self.model = None
        self.model_origin = None
        self.applied_state = None

    def update(self, xyz, block_data):
        # type: (tuple[int, int, int], dict | None) -> None
        data = ValueOf(block_data.get("exData")) if block_data else None
        if not isinstance(data, dict) or ValueOf(data.get(K_DESTROY_FLAG)) != 0:
            self.clear_model()
            return
        origin = _read_vector(data, K_FLUID_RENDER_ORIGIN)
        size = _read_vector(data, K_FLUID_RENDER_SIZE)
        if origin is None or size is None:
            self.clear_model()
            return
        size = tuple(value - 2.0 * FLUID_SURFACE_INSET for value in size)
        if any(value <= 0.0 for value in size):
            self.clear_model()
            return

        surface = _read_fluid_surface(data)
        if surface is None:
            self.clear_model()
            return
        fluid_id, ratio = surface
        x, y, z = xyz
        model_origin = (
            x + origin[0],
            y + origin[1] + FLUID_SURFACE_INSET,
            z + origin[2],
        )
        if self.model is None or model_origin != self.model_origin:
            self.clear_model()
            self.model = FluidVolumeModel(*model_origin)
            self.model_origin = model_origin

        state = (fluid_id, size, ratio)
        previous = self.applied_state
        if state == previous:
            return
        texture_changed = previous is None or state[0] != previous[0]
        ok = True
        if texture_changed:
            ok = self.model.SetTexture(state[0])
        if ok and (texture_changed or size != previous[1]):
            ok = self.model.SetSize(*size)
        if ok and (texture_changed or ratio != previous[2]):
            ok = self.model.SetYScale(ratio)
        if ok:
            self.applied_state = state
        else:
            # 模型尚未就绪时隐藏旧内容，下一轮重新提交所有参数。
            self.model.SetYScale(0.0)
            self.applied_state = None


def _remove_pond(key):
    pond = loaded_ponds.pop(key, None)
    if pond is not None:
        pond.clear_model()


@asModBlockLoadedListener(BrineEvaporationPond.CONTROLLER)
def on_pond_loaded(event):
    key = (event.dimensionId, event.posX, event.posY, event.posZ)
    # 重复加载时清掉旧客户端实体；NBT 尚未同步也保留坐标等待后续刷新。
    _remove_pond(key)
    loaded_ponds[key] = PondFluidDisplay()


@asModBlockRemovedListener(BrineEvaporationPond.CONTROLLER)
def on_pond_removed(event):
    _remove_pond((event.dimensionId, event.posX, event.posY, event.posZ))


@ClientInitCallback()
@Repeat(0.2)
def update_pond_fluids():
    if not loaded_ponds:
        return
    current_dimension = CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension()
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    for key, pond in tuple(loaded_ponds.items()):
        if key[0] != current_dimension:
            _remove_pond(key)
            continue
        xyz = key[1:]
        pond.update(xyz, block_info.GetBlockEntityData(xyz))


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(event):
    if event.playerId != GetLocalPlayerId():
        return
    for key in tuple(loaded_ponds):
        if key[0] == event.fromDimensionId:
            _remove_pond(key)
    ExecLater(10.0 / 30.0, _reset_loaded_models)


def _reset_loaded_models():
    # 地形/维度初始化可能覆盖早期渲染参数，完成后重建一次并由定时器重填。
    for pond in tuple(loaded_ponds.values()):
        pond.clear_model()


@OnLocalPlayerStopLoading.Listen()
def on_local_player_loaded(event):
    if event.playerId == GetLocalPlayerId():
        ExecLater(10.0 / 30.0, _reset_loaded_models)


@ClientUninitCallback()
def on_client_uninit():
    for key in tuple(loaded_ponds):
        _remove_pond(key)
