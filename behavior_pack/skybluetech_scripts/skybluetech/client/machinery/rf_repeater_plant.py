# coding=utf-8
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent
from skybluetech_scripts.tooldelta.api.client import (
    CreateShapeFactory,
    GetBlockNameAndAux,
    GetBlockEntityData as CGetBlockEntityData,
)
from skybluetech_scripts.tooldelta.utils.nbt import NBT2Py
from ...common.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildAddWire,
)
from ...common.define.id_enum.machinery import RF_REPEATER_PLANT as MACHINE_ID
from .utils.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)
from ...common.utils.block_sync import BlockSync

block_sync = BlockSync(MACHINE_ID, side=BlockSync.SIDE_CLIENT)
lasers = {}  # type: dict[tuple[int, int, int], dict[tuple[int, int, int], WireLaser]]


class WireLaser:
    def __init__(self, start_pos, end_pos):
        # type: (tuple[float, float, float], tuple[float, float, float]) -> None
        x1, y1, z1 = self.start_pos = start_pos
        x2, y2, z2 = self.end_pos = end_pos
        self.shape = CreateShapeFactory().AddLineShape(
            (x1 + 0.5, y1 + 2.8, z1 + 0.5),
            (x2 + 0.5, y2 + 2.8, z2 + 0.5),
            hex2rgb(0x00FFFF),
        )
        self._removed = False

    def Remove(self):
        if self._removed:
            return
        self._removed = True
        self.shape.Remove()

    def __hash__(self):
        return hash((self.start_pos, self.end_pos))

    def __eq__(self, other):
        # type: (object) -> bool
        if not isinstance(other, WireLaser):
            return False
        return self.start_pos == other.start_pos and self.end_pos == other.end_pos


def hex2rgb(hex):
    # type: (int) -> tuple[int, int, int]
    return (hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF


def add_wire(xyz1, xyz2):
    # type: (tuple[int, int, int], tuple[int, int, int]) -> None
    laser = WireLaser(xyz1, xyz2)
    prev_laser = lasers.get(xyz1, {}).get(xyz2, None)
    if prev_laser:
        prev_laser.Remove()
    prev_laser = lasers.get(xyz2, {}).get(xyz1, None)
    if prev_laser:
        prev_laser.Remove()
    lasers.setdefault(xyz1, {})[xyz2] = laser
    lasers.setdefault(xyz2, {})[xyz1] = laser


def remove_wire_src(xyz):
    # type: (tuple[int, int, int]) -> None
    pos_lasers = lasers.pop(xyz, None)
    if pos_lasers is None:
        return
    for other_xyz, laser in pos_lasers.copy().items():
        laser.Remove()
        other_pos_lasers = lasers.get(other_xyz)
        if other_pos_lasers is not None:
            laser_2 = other_pos_lasers.pop(xyz, None)
            if laser_2:
                laser_2.Remove()
            if not other_pos_lasers:
                del lasers[other_xyz]


@ClientBlockUseEvent.Listen(inner_priority=10)
def onClientBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    if event.blockName != MACHINE_ID:
        return
    _, aux = GetBlockNameAndAux((event.x, event.y, event.z))
    layer = (aux & 0b1100) >> 2
    if layer != 0:
        # 只改变 GUI 读取到的 xyz。。
        event.y -= layer


@asModBlockLoadedListener(MACHINE_ID)
def onPlantLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    block_entity_data = CGetBlockEntityData(event.posX, event.posY, event.posZ)
    if block_entity_data is None:
        return
    pydata = NBT2Py(block_entity_data["exData"])
    con_nodes = pydata.get("con_nodes", [])
    for con_node in con_nodes:
        add_wire((event.posX, event.posY, event.posZ), tuple(con_node))


@asModBlockRemovedListener(MACHINE_ID)
def onPlantUnloaded(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    remove_wire_src((event.posX, event.posY, event.posZ))


@RFRepeaterPlantBuildAddWire.Listen()
def onAddWire(event):
    # type: (RFRepeaterPlantBuildAddWire) -> None
    add_wire((event.x, event.y, event.z), (event.to_x, event.to_y, event.to_z))
