# coding=utf-8

from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.api.client import CreateShapeFactory
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode
from ..define.id_enum.machinery import HOVER_TEXT_DISPLAYER as MACHINE_ID
from ..define.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from ..ui.machinery.hover_text_displayer import HoverTextDisplayerUI
from ..ui_sync.machinery.hover_text_displayer import HoverTextDisplayerUISync
from ..utils.action_commit import SafeGetMachine
from ..utils.block_sync import BlockSync
from ..utils.mod_block_event import asModBlockLoadedListener, asModBlockRemovedListener
from .basic import (
    BaseClicker,
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
class HoverTextDisplayer(BaseClicker, GUIControl, PowerControl):
    block_name = MACHINE_ID
    bound_ui = HoverTextDisplayerUI
    store_rf_max = 2000
    running_power = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        BaseClicker.__init__(self)
        PowerControl.__init__(self, dim, x, y, z, block_entity_data)
        self.set_text()
        self.can_display = self.PowerEnough()
        self.sync = HoverTextDisplayerUISync.NewServer(self).Activate()
        self.OnSync()

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
            self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.MarkedAsChanged()

    def OnUnload(self):
        GUIControl.OnUnload(self)
        PowerControl.OnUnload(self)
        block_sync.discard_block((self.dim, self.x, self.y, self.z))

    def set_text(self, text=None):
        # type: (str | None) -> None
        if text is not None:
            self.text = text
        self.running_power = self.calcuate_power_cost()
        if self.IsActive():
            HoverTextDisplayerContentUpdate(
                self.x, self.y, self.z, self.text, self.running_power
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

    @property
    def text(self):
        # type: () -> str
        return self.bdata[K_TEXT] or ""

    @text.setter
    def text(self, value):
        # type: (str) -> None
        self.bdata[K_TEXT] = str(value)


@HoverTextDisplayerContentUpload.Listen()
def onTextUploaded(event):
    # type: (HoverTextDisplayerContentUpload) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, HoverTextDisplayer):
        return
    text = py2_unicode(event.new_text.strip())
    if len(text) > 256:
        text = text[:256]
    text_list = []
    cached_text = ""
    l = 0
    for char in text:
        if char == "\n":
            text_list.append(cached_text)
            cached_text = ""
            l = 0
        else:
            if char != "§":
                l += 1
            if l > 40:
                text_list.append(cached_text)
                cached_text = ""
                l = 0
            cached_text += char
    if cached_text != "":
        text_list.append(cached_text)
    m.set_text("\n".join(text_list))


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
