# coding=utf-8

from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.api.client import CreateShapeFactory
from ..define.id_enum.machinery import HOVER_TEXT_DISPLAYER as MACHINE_ID
from ..define.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from ..ui.machinery.hover_text_displayer import HoverTextDisplayerUI
from ..utils.action_commit import SafeGetMachine
from ..utils.block_sync import BlockSync
from ..utils.mod_block_event import asModBlockLoadedListener, asModBlockRemovedListener
from .basic import (
    GUIControl,
    PowerControl,
    RegisterMachine,
)

# TYPE_CHECKING
if 0:
    from mod.client.component.drawingShapeCompClient import DrawingShapeCompClient
# TYPE_CHECKING END

K_TEXT = "st:text"

block_sync = BlockSync(MACHINE_ID)


@RegisterMachine
class HoverTextDisplayer(GUIControl, PowerControl):
    bound_ui = HoverTextDisplayerUI
    store_rf_max = 2000
    running_power = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        PowerControl.__init__(self, dim, x, y, z, block_entity_data)

    def OnLoad(self):
        PowerControl.OnLoad(self)
        self.set_text(self.bdata[K_TEXT] or "")
        self.can_display = self.PowerEnough()

    def OnClick(self, event):
        GUIControl.OnClick(
            self,
            event,
            {
                "st:init_content": HoverTextDisplayerContentUpdate(
                    self.x, self.y, self.z, self.text, self.running_power
                ).marshal()
            },
        )

    def OnTicking(self):
        if self.PowerEnough():
            self.ReducePower()

    def Dump(self):
        PowerControl.Dump(self)
        self.bdata[K_TEXT] = self.text

    def OnUnload(self):
        GUIControl.OnUnload(self)
        PowerControl.OnUnload(self)

    def set_text(self, text):
        # type: (str) -> None
        self.text = text
        self.running_power = self.calcuate_power_cost()
        HoverTextDisplayerContentUpdate(
            self.x, self.y, self.z, text, self.running_power
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        PowerControl.SetDeactiveFlag(self, flag)
        HoverTextDisplayerContentUpdate(
            self.x, self.y, self.z, "", self.running_power
        ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    def UnsetDeactiveFlag(self, flag):
        # type: (int) -> None
        PowerControl.UnsetDeactiveFlag(self, flag)
        if self.deactive_flags == 0:
            HoverTextDisplayerContentUpdate(
                self.x,
                self.y,
                self.z,
                self.text,
                self.running_power,
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    def calcuate_power_cost(self):
        cost = len(self.text) * 0.2 * (1.5 if "§" in self.text else 1)
        if cost % 1 > 0:
            return int(cost) + 1
        else:
            return int(cost)


@HoverTextDisplayerContentUpload.Listen()
def onTextUploaded(event):
    # type: (HoverTextDisplayerContentUpload) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, HoverTextDisplayer):
        return
    if len(event.new_text) > 256:
        event.new_text = event.new_text[:256]
    m.set_text(event.new_text)


# CLIENT PART

shapes = {}  # type: dict[tuple[int, int, int], DrawingShapeCompClient]


def add_text(pos, default_text=""):
    # type: (tuple[int, int, int], str) -> None
    x, y, z = pos
    tx = x + 0.5
    ty = y + 1.1
    tz = z + 0.5
    shape = CreateShapeFactory().AddTextShape((tx, ty, tz), default_text)
    shapes[pos] = shape


def remove_text(pos):
    # type: (tuple[int, int, int]) -> None
    shape = shapes.pop(pos, None)
    if shape:
        shape.Remove()


def update_text(pos, text):
    # type: (tuple[int, int, int], str) -> None
    shape = shapes.get(pos, None)
    if shape is not None:
        shape.SetText(text)


@asModBlockLoadedListener(HoverTextDisplayer.block_name)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    if pos not in shapes:
        add_text(pos)


@asModBlockRemovedListener(HoverTextDisplayer.block_name)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    pos = (event.posX, event.posY, event.posZ)
    remove_text(pos)


@HoverTextDisplayerContentUpdate.Listen()
def onTextUpdated(event):
    # type: (HoverTextDisplayerContentUpdate) -> None
    update_text((event.x, event.y, event.z), event.new_text)
