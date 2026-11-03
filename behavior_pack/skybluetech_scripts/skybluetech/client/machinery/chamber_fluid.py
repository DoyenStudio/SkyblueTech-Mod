# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import (
    DimensionChangeClientEvent, OnLocalPlayerStopLoading,
    ModBlockEntityLoadedClientEvent, ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ClientUninitCallback
from skybluetech_scripts.tooldelta.utils.nbt import ValueOf
from skybluetech_scripts.tooldelta.utils.timer import ExecLater, Repeat
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def import (
    distillation_chamber, heat_melting_chamber,
)
from skybluetech_scripts.skybluetech.client.utils.fluid_model import FluidVolumeModel


# 模型像素边界：蒸馏仓内腔 x/z=-6..6、y=2..14；熔化仓下腔
# x/z=-5..5、y=3..10。各面内缩，避开内壁和底板的共面闪烁。
INSET = 0.004
CHAMBERS = {
    Machinery.DISTILLATION_CHAMBER: (
        (distillation_chamber.INPUT_MAX_VOLUME, distillation_chamber.OUTPUT_MAX_VOLUME),
        2 / 16.0, (12 / 16.0, 12 / 16.0, 12 / 16.0),
    ),
    Machinery.HEAT_MELTING_CHAMBER: (
        (heat_melting_chamber.OUTPUT_MAX_VOLUME,),
        3 / 16.0, (10 / 16.0, 7 / 16.0, 10 / 16.0),
    ),
}
loaded_chambers = {}
local_player_id = None


class ChamberFluidDisplay(object):
    def __init__(self, block_name):
        self.capacities, self.base_y, self.size = CHAMBERS[block_name]
        self.model = None
        self.applied_state = None

    def clear_model(self):
        if self.model is not None:
            self.model.Destroy()
        self.model = None
        self.applied_state = None

    def update(self, xyz, block_data):
        data = ValueOf(block_data.get("exData")) if block_data else None
        if not isinstance(data, dict):
            self.clear_model()
            return
        selected = None
        for index, capacity in enumerate(self.capacities):
            slot = FluidSlotClient(data, index, capacity)
            volume = slot.volume
            if not slot.fluid_id or not 0.0 < volume < float("inf"):
                continue
            # 严格大于：等量时保留先遍历的输入槽，不合并两槽储量。
            if selected is None or volume > selected[1]:
                selected = (slot.fluid_id, volume, capacity)
        if selected is None:
            self.clear_model()
            return
        fluid_id, volume, capacity = selected
        state = (fluid_id, min(1.0, volume / float(capacity)))
        if state == self.applied_state:
            return
        if self.model is None:
            x, y, z = xyz
            self.model = FluidVolumeModel(x + 0.5, y + self.base_y + INSET, z + 0.5)
        previous = self.applied_state
        texture_changed = previous is None or previous[0] != fluid_id
        ok = True
        if texture_changed:
            ok = self.model.SetTexture(fluid_id)
            if ok:
                ok = self.model.SetSize(*(value - 2.0 * INSET for value in self.size))
        if ok:
            ok = self.model.SetYScale(state[1])
        if ok:
            self.applied_state = state
        else:
            self.model.SetYScale(0.0)
            self.applied_state = None


def _remove_chamber(key):
    display = loaded_chambers.pop(key, None)
    if display is not None:
        display.clear_model()


@ModBlockEntityLoadedClientEvent.Listen()
def on_chamber_loaded(event):
    block_name = event.blockName
    if block_name not in CHAMBERS:
        return
    key = (event.dimensionId, event.posX, event.posY, event.posZ)
    _remove_chamber(key)
    loaded_chambers[key] = ChamberFluidDisplay(block_name)


@ModBlockEntityRemoveClientEvent.Listen()
def on_chamber_removed(event):
    _remove_chamber((event.dimensionId, event.posX, event.posY, event.posZ))


@ClientInitCallback()
@Repeat(0.2)
def update_chamber_fluids():
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    for key, display in tuple(loaded_chambers.items()):
        xyz = key[1:]
        display.update(xyz, block_info.GetBlockEntityData(xyz))


def _reset_loaded_models():
    for display in tuple(loaded_chambers.values()):
        display.clear_model()


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(event):
    if local_player_id is not None and event.playerId != local_player_id:
        return
    for key in tuple(loaded_chambers):
        if key[0] == event.fromDimensionId:
            _remove_chamber(key)
    ExecLater(10.0 / 30.0, _reset_loaded_models)


@OnLocalPlayerStopLoading.Listen()
def on_local_player_loaded(event):
    global local_player_id
    local_player_id = event.playerId
    ExecLater(10.0 / 30.0, _reset_loaded_models)


@ClientUninitCallback()
def on_client_uninit():
    global local_player_id
    for key in tuple(loaded_chambers):
        _remove_chamber(key)
    local_player_id = None
