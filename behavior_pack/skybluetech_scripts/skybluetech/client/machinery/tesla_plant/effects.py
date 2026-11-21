# coding=utf-8
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.general import ClientUninitCallback

from ....common.define.id_enum import Machinery
from ....common.events.machinery.tesla_plant import TeslaPlantAttack
from ...utils.electric_arc import ElectricArc

SHOCK_SOUND = "sfx.skybluetech.tesla_plant.shock"
MAX_SHOCK_SOUNDS = 4
active_shocks = set()  # type: set[TeslaShock]


class TeslaShock(ElectricArc):
    """One short discharge; server snapshots also cover lethal hits."""

    def __init__(self, block_pos, end_pos, dim):
        # type: (tuple[int, int, int], tuple[float, float, float], int) -> None
        self.block_pos = block_pos
        self.dim = dim
        x, y, z = block_pos
        super(TeslaShock, self).__init__((x + 0.5, y + 2.5, z + 0.5), end_pos)
        active_shocks.add(self)

    def remove(self):
        super(TeslaShock, self).remove()
        active_shocks.discard(self)


@TeslaPlantAttack.Listen()
def on_tesla_plant_attack(event):
    # type: (TeslaPlantAttack) -> None
    dim = CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension()
    if event.dim != dim:
        return
    block_pos = (event.x, event.y, event.z)
    sound_count = min(len(event.entity_ids), MAX_SHOCK_SOUNDS)
    if sound_count:
        audio = CF.CreateCustomAudio(LEVEL_ID)
        sound_pos = (event.x + 0.5, event.y + 2.5, event.z + 0.5)
        for _ in range(sound_count):
            audio.PlayCustomMusic(SHOCK_SOUND, sound_pos, 1.0, 1.0, False, None)
    for index, entity_id in enumerate(event.entity_ids):
        if index < len(event.target_positions):
            pos = event.target_positions[index]
        else:
            pos = CF.CreatePos(entity_id).GetFootPos()
        if pos is not None and len(pos) == 3:
            TeslaShock(block_pos, tuple(pos), event.dim)


@asModBlockRemovedListener(Machinery.TESLA_PLANT)
def on_tesla_plant_removed(event):
    for shock in tuple(active_shocks):
        x, y, z = shock.block_pos
        if (
            event.dimensionId == shock.dim
            and event.posX == x and event.posZ == z and y <= event.posY <= y + 2
        ):
            shock.remove()


@DimensionChangeClientEvent.Listen()
def on_dimension_changed(_event):
    clear_shocks()


@ClientUninitCallback()
def clear_shocks():
    for shock in tuple(active_shocks):
        shock.remove()
