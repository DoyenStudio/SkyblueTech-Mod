# coding=utf-8
from skybluetech_scripts.tooldelta.events.event_bus import GetMCClientEventBus
from skybluetech_scripts.tooldelta.events.service import EventListenerService
from skybluetech_scripts.skybluetech.common.events.machinery.fluid_output_faces import (
    FluidOutputFacesGet,
    FluidOutputFacesSet,
    FluidOutputFacesUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.fluid_output_faces import (
    ALL_OUTPUT_FACES,
    OUTPUT_FACES,
    OUTPUT_FACE_LABELS,
    OUTPUT_SLOT_COLORS,
)

from .base_page import PageBase


class FluidOutputSettingsPage(PageBase, EventListenerService):
    """复用主界面槽位布局的输出面配置页；宿主声明 fluid_output_slot_paths。"""

    def __init__(self, base, machine_pos):
        PageBase.__init__(self, base, machine_pos)
        EventListenerService.__init__(self, GetMCClientEventBus())
        self.buttons = {}
        self.masks = {}
        self.revision = -1
        self.selected_slot = None
        self.ready = False
        self.pending = False

    @classmethod
    def CaptureMainLayout(cls, main):
        origin = main.GetRootPos()
        parent_origin = main._parent.GetRootPos()
        slots = {}
        for slot, path in main._root.fluid_output_slot_paths.items():
            control = main[path]
            pos = control.GetRootPos()
            slots[slot] = ((pos[0] - origin[0], pos[1] - origin[1]), control.GetSize())
        return {
            "position": (origin[0] - parent_origin[0], origin[1] - parent_origin[1]),
            "size": main.GetSize(),
            "slots": slots,
        }

    def Init(self):
        self.status = self.base["status"].asLabel()
        self.dialog = self.base._root.AddElement(
            "MachinePanelExPages.fluid_output_face_dialog", "fluid_output_faces_dialog"
        )
        self.dialog.SetVisible(False)
        self.dialog["blocker"].asButton().SetCallback(lambda _: self.close_dialog())
        self.dialog_panel = self.dialog["panel"]
        self.dialog_panel["cancel"].asButton().SetCallback(lambda _: self.close_dialog())
        self.dialog_panel["apply"].asButton().SetCallback(lambda _: self.apply())
        self.dialog_panel["cancel/caption"].asLabel().SetText("取消")
        self.dialog_panel["apply/caption"].asLabel().SetText("保存")
        for name in ("cancel", "apply"):
            self.dialog_panel[name + "/fill"].asImage().SetAlpha(1.0)
            self.dialog_panel[name + "/fill"].asImage().SetSpriteColor((0.77, 0.83, 0.90))
        self.face_buttons = []
        for index in range(len(OUTPUT_FACES)):
            button = self.dialog_panel["face%d" % index].asButton()
            button.SetCallback(lambda _, index=index: self.toggle_face(index))
            self.face_buttons.append(button)

    def Active(self):
        self.enable_listeners()
        self.ready = False
        self.pending = False
        self.close_dialog()
        layout = self.base._root._main_page_layouts[self.__class__]
        parent_origin = self.base._parent.GetRootPos()
        background_origin = self.base._parent._parent.GetRootPos()
        self.base.SetAnchorFrom("top_left")
        self.base.SetAnchorTo("top_left")
        self.base.SetSize(layout["size"])
        self.base.SetPos((
            layout["position"][0] - parent_origin[0] + background_origin[0],
            layout["position"][1] - parent_origin[1] + background_origin[1],
        ))
        for index, slot in enumerate(sorted(layout["slots"])):
            if slot not in self.buttons:
                button = self.base.AddElement(
                    "MachinePanelExPages.fluid_output_btn", "output_slot%d" % slot
                ).asButton()
                button.SetCallback(lambda _, slot=slot: self.open_dialog(slot))
                button["fill"].asImage().SetSpriteColor(
                    OUTPUT_SLOT_COLORS[index % len(OUTPUT_SLOT_COLORS)]
                )
                button["caption"].asLabel().SetColor((0.12, 0.15, 0.20))
                self.buttons[slot] = button
            position, size = layout["slots"][slot]
            self.buttons[slot].SetPos(position).SetSize(size, resize_children=True)
            self.buttons[slot]["caption"].asLabel().SetText("…")
        self.status.SetText("正在读取配置…")
        FluidOutputFacesGet(*self.machine_pos[1:]).send()

    def Deactive(self):
        self.close_dialog()
        self.disable_listeners()

    def Destroy(self):
        self.disable_listeners()

    @EventListenerService.Listen(FluidOutputFacesUpdate)
    def on_faces_update(self, event):
        if event.pos != tuple(self.machine_pos) or event.revision < self.revision:
            return
        self.masks = dict(event.masks)
        self.revision = event.revision
        self.ready = True
        self.pending = False
        for slot, button in self.buttons.items():
            mask = self.masks[slot]
            labels = [label for index, label in enumerate(OUTPUT_FACE_LABELS) if mask & (1 << index)]
            text = "\n".join("".join(labels[i:i + 2]) for i in range(0, len(labels), 2))
            if mask == ALL_OUTPUT_FACES:
                text = "全部"
            button["caption"].asLabel().SetText(text or "禁用", sync_size=True)
        self.status.SetText("点击输出槽设置方向")
        if event.status == "saved":
            self.close_dialog()
            self.status.SetText("输出面已保存")
        elif event.status in ("conflict", "invalid"):
            self.status.SetText("配置已变化，请重新确认")
            if self.selected_slot is not None:
                self.open_dialog(self.selected_slot)

    def open_dialog(self, slot):
        if not self.ready or self.pending:
            return
        self.selected_slot = slot
        self.draft_mask = self.masks[slot]
        self.draft_revision = self.revision
        index = sorted(self.buttons).index(slot)
        self.selected_color = OUTPUT_SLOT_COLORS[index % len(OUTPUT_SLOT_COLORS)]
        self.dialog_panel["accent"].asImage().SetSpriteColor(self.selected_color)
        self.dialog_panel["title"].asLabel().SetText("流体输出槽 %d" % slot)
        self.dialog_panel["apply/caption"].asLabel().SetText("保存")
        self.refresh_faces()
        self.dialog.SetVisible(True)

    def close_dialog(self):
        self.dialog.SetVisible(False)
        self.selected_slot = None

    def toggle_face(self, index):
        if not self.pending:
            self.draft_mask ^= 1 << index
            self.refresh_faces()

    def refresh_faces(self):
        for index, button in enumerate(self.face_buttons):
            selected = bool(self.draft_mask & (1 << index))
            button["fill"].asImage().SetAlpha(1.0)
            button["fill"].asImage().SetSpriteColor(
                self.selected_color if selected else (0.28, 0.30, 0.34)
            )
            button["caption"].asLabel().SetColor(
                (0.12, 0.15, 0.20) if selected else (1.0, 1.0, 1.0)
            )
            button["caption"].asLabel().SetText(
                OUTPUT_FACE_LABELS[index] + ("：开" if selected else "：关")
            )

    def apply(self):
        if self.pending or self.selected_slot is None:
            return
        self.pending = True
        self.dialog_panel["apply/caption"].asLabel().SetText("保存中")
        x, y, z = self.machine_pos[1:]
        FluidOutputFacesSet(
            x, y, z, self.selected_slot, self.draft_mask, self.draft_revision
        ).send()

    @staticmethod
    def GetIconPath():
        return "textures/items/transmitter_settings_wrench"

    @staticmethod
    def GetControlDef():
        return "MachinePanelExPages.fluid_output_settings"

    @staticmethod
    def GetTitle():
        return "流体输出面"
