# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode

from ...common.define.id_enum.machinery import Machinery
from ...common.define.ui_keys import HOVER_TEXT_DISPLAYER_UI
from ...common.events.machinery.hover_text_displayer import (
    HoverTextDisplayerContentUpdate,
    HoverTextDisplayerContentUpload,
)
from ...common.machinery_def.hover_text_displayer import K_TEXT, STORE_RF_MAX
from ...common.utils.block_sync import BlockSync
from .basic import (
    BaseClicker,
    GUIControl,
    OperationListener,
    PowerControl,
    RegisterMachine,
)

block_sync = BlockSync(Machinery.HOVER_TEXT_DISPLAYER, side=BlockSync.SIDE_SERVER)


@RegisterMachine
class HoverTextDisplayer(BaseClicker, GUIControl, PowerControl, OperationListener):
    block_name = Machinery.HOVER_TEXT_DISPLAYER
    bound_ui = HOVER_TEXT_DISPLAYER_UI
    store_rf_max = STORE_RF_MAX
    running_power = 1

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.set_text()
        self.can_display = self.PowerEnough()
        self._last_can_display = self.can_display

    def OnClick(self, event, extra_datas=None):
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
        self.update_display_stat()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
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

    def update_display_stat(self):
        active = self.IsActive()
        if active != self._last_can_display:
            self._last_can_display = active
        else:
            return
        if active:
            HoverTextDisplayerContentUpdate(
                self.x,
                self.y,
                self.z,
                self.text,
                self.running_power,
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))
        else:
            HoverTextDisplayerContentUpdate(
                self.x, self.y, self.z, "", self.running_power
            ).sendMulti(block_sync.get_players((self.dim, self.x, self.y, self.z)))

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        pass

    @SuperExecutorMeta.execute_super
    def UnsetDeactiveFlag(self, flag, flush=True):
        # type: (int, bool) -> None
        pass

    def calcuate_power_cost(self):
        cost = len(self.text) * 0.2 * (1.5 if "搂" in self.text else 1)
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


@HoverTextDisplayer.ForOperation(HoverTextDisplayerContentUpload)
def onTextUploaded(event, machine):
    # type: (HoverTextDisplayerContentUpload, HoverTextDisplayer) -> None
    text = py2_unicode(event.new_text.strip())
    if len(text) > 256:
        text = text[:256]
    text_list = []
    cached_text = ""
    length = 0
    for char in text:
        if char == "\n":
            text_list.append(cached_text)
            cached_text = ""
            length = 0
        else:
            if char != "搂":
                length += 1
            if length > 40:
                text_list.append(cached_text)
                cached_text = ""
                length = 0
            cached_text += char
    if cached_text != "":
        text_list.append(cached_text)
    machine.set_text("\n".join(text_list))
