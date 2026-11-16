# coding=utf-8
from collections import Counter
from mod.client.extraClientApi import GetLocalPlayerId, GetMinecraftEnum, PopTopUI as close_screen
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from ....common.utils import blueprint as bp
from ....common.events.machinery.blueprint import BlueprintAction
from ...machinery.blueprint_preview import preview
from .define import MAIN_PATH, MachinePanelUIProxy

GRID = "bp_materials"
BUTTON_TEXTURE = "textures/ui/skybluetech/button_"


def read_clipboard():
    return CF.CreateGame(LEVEL_ID).GetClipboardContent()


def write_clipboard(text):
    return CF.CreateGame(LEVEL_ID).SetClipboardContent(text)


@RegistToolDeltaScreen("BlueprintTableUI.main", is_proxy=True)
class BlueprintTableUI(MachinePanelUIProxy):
    def OnCreate(self):
        preview.clear()
        preview.location = tuple(self.pos)
        preview.panel = self
        self.mode = None
        self.rows = []
        self.stock = Counter()
        self.code = self.sent = ""
        self.pending = None
        self.ready = False
        self.updating = False
        self.ticks = 0
        self.grid = self.ctrl("materials").asScrollView().GetContent().asGrid()
        self.edit = self.ctrl("input").asTextEditBox()
        self.status = self.ctrl("status").asLabel()
        self.visibility()

    def ctrl(self, name):
        return self.GetElement(MAIN_PATH / name)

    def send(self, action, value=None):
        BlueprintAction(self.pos[1], self.pos[2], self.pos[3], action, value).send()

    def visibility(self):
        saving = self.mode == "save"
        for name in ("select", "copy"):
            self.ctrl(name).SetVisible(saving)
        self.ctrl("paste").SetVisible(self.mode == "build")
        self.ctrl("copy").SetAlpha(1.0 if self.code else 0.45)
        self.ctrl("confirm").SetAlpha(1.0 if self.ready else 0.45)

    def set_input(self, code):
        self.updating = True
        if self.edit.GetText() != code:
            self.edit.SetText(code)
        self.updating = False

    def apply_state(self, state):
        code = bp.as_text(state["code"]).encode("utf-8")
        if self.pending is not None and not state["locked"] and state["mode"] == "build" and code != self.pending:
            return False
        self.pending = None
        if self.mode != state["mode"]:
            self.mode = state["mode"]
            for mode in ("save", "build"):
                button = self.ctrl(mode)
                selected = mode == self.mode
                button["default"].asImage().SetSprite(BUTTON_TEXTURE + ("pressed" if selected else "default"))
                button["hover"].asImage().SetSprite(BUTTON_TEXTURE + ("pressed" if selected else "hovered"))
        self.code = self.sent = code
        self.ready = state["ready"]
        self.rows = [(name, aux, count, Item(name, aux).GetBasicInfo().id_aux)
                     for name, aux, count in state["rows"]]
        self.set_input(code)
        self.status.SetText(state["status"])
        self.refresh_stock()
        self.grid.SetGridDimension((5, max(1, (len(self.rows) + 4) // 5)))
        self.grid.SetPropertyBag({"#maximum_grid_items": len(self.rows)})
        self.visibility()
        return True

    def refresh_stock(self):
        stock = Counter()
        stacks = CF.CreateItem(GetLocalPlayerId()).GetPlayerAllItems(GetMinecraftEnum().ItemPosType.INVENTORY, False)
        for stack in stacks or ():
            if stack:
                stock[bp.material_key(stack["newItemName"], stack.get("newAuxValue", 0))] += stack["count"]
        self.stock = stock

    def OnTicking(self):
        self.ticks += 1
        if self.mode is None and self.ticks % 12 == 1:
            self.send("open")
        elif self.mode == "build":
            current = self.edit.GetText()
            if current is not None and bp.as_text(current)[:501].encode("utf-8") != self.code:
                self.change_input(current)
            if self.pending is not None and self.sent != self.pending:
                self.sent = self.pending
                self.send("edit", self.pending)
            elif self.ticks % 12 == 0:
                self.refresh_stock()

    def change_input(self, value):
        value = bp.as_text(value)[:501].encode("utf-8")
        if value == self.code:
            return
        self.code = self.pending = value
        # Pasting the previous code before the next UI tick still requires
        # a fresh reply, since the old material rows have just been removed.
        self.sent = None
        self.rows = []
        self.grid.SetPropertyBag({"#maximum_grid_items": 0})
        self.ready = False
        preview.clear()
        self.status.SetText("正在校验" if value else "请输入蓝图码")
        self.visibility()

    @Binder.binding(Binder.BF_EditChanged, "#Blueprint.edit")
    def edit_changed(self, args):
        if self.mode == "build" and not self.updating:
            self.change_input(args["Text"])

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.save")
    def save(self, _):
        if self.mode != "save":
            self.pending = None
            self.send("mode", "save")

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.build")
    def build(self, _):
        if self.mode != "build":
            self.send("mode", "build")

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.select")
    def select(self, _):
        self.send("select")

    def close_for_selection(self):
        close_screen()

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.confirm")
    def confirm(self, _):
        if self.ready and self.pending is None:
            self.send("confirm", self.code)

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.copy")
    def copy(self, _):
        if self.code and self.mode == "save":
            self.status.SetText("已复制蓝图码" if write_clipboard(self.code) else "复制失败")

    @Binder.binding(Binder.BF_ButtonClickUp, "#Blueprint.paste")
    def paste(self, _):
        value = read_clipboard()
        if value:
            self.set_input(value)
            self.change_input(value)
        else:
            if value == "":
                self.set_input("")
                self.change_input("")
            self.status.SetText("剪贴板中没有可读取的文本")

    @Binder.binding_collection(Binder.BF_BindInt, GRID, "#Blueprint.count")
    def row_count(self, _):
        return len(getattr(self, "rows", ()))

    @Binder.binding_collection(Binder.BF_BindInt, GRID, "#Blueprint.item")
    def icon(self, index):
        return self.rows[index][3] if 0 <= index < self.row_count(0) else 131072

    @Binder.binding_collection(Binder.BF_BindColor, GRID, "#Blueprint.color")
    def color(self, index):
        if 0 <= index < self.row_count(0) and self.mode == "build":
            name, aux, count, _ = self.rows[index]
            if self.stock[(name, aux)] < count:
                return (0.78, 0.24, 0.24)
        return (0.47, 0.47, 0.47)

    @Binder.binding_collection(Binder.BF_BindString, GRID, "#Blueprint.quantity")
    def quantity(self, index):
        if not 0 <= index < self.row_count(0):
            return ""
        name, aux, count, _ = self.rows[index]
        return ("%d/%d" % (self.stock[(name, aux)], count)) if self.mode == "build" else str(count)

    def OnDestroy(self):
        if self.pending is not None and self.sent != self.pending:
            self.send("edit", self.pending)
        if preview.panel is self:
            preview.panel = None
