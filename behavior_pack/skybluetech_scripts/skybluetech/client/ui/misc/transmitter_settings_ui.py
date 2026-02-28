# coding=utf-8
import random
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import (
    ToolDeltaScreen,
    UBaseCtrl,
    Binder,
    RegistToolDeltaScreen,
    SCREEN_BASE_PATH,
)
from ....common.events.misc.transmitter_settings import (
    TransmitterSetLabel,
    TransmitterSetPriority,
)

INDEX_GRID_NODE = SCREEN_BASE_PATH / "network_label_selector_stack"
CLOSE_BTN_NODE = SCREEN_BASE_PATH / "close_btn"
MAIN_LABEL_NODE = SCREEN_BASE_PATH / "main_label"
PRIOR_EDITOR_NODE = SCREEN_BASE_PATH / "prior_editor"
PRIOR_SUB_BTN_NODE = SCREEN_BASE_PATH / "prior_sub_btn"
PRIOR_ADD_BTN_NODE = SCREEN_BASE_PATH / "prior_add_btn"


def rand_rgb_by_index(index):
    # type: (int) -> tuple[float, float, float]
    random.seed(index)
    r = random.random() * 256 * 256 * 256
    return (
        float(r // 256 // 256) / 256,
        float(r // 256 % 256) / 256,
        float(r % 256) / 256,
    )


def get_opposite_color(r, g, b):
    # type: (float, float, float) -> tuple[float, float, float]
    light = 0.299 * r + 0.587 * g + 0.114 * b
    if light > 0.5:
        return 0, 0, 0
    else:
        return 1, 1, 1


@RegistToolDeltaScreen("TransmitterSettingsUI.main")
class TransmitterSettingsUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.priority_value = params["priority"]  # type: int
        self.label_value = params["label"]  # type: int
        self.dim = params["dim"]  # type: int
        self.x = params["x"]  # type: int
        self.y = params["y"]  # type: int
        self.z = params["z"]  # type: int
        self.ap_side = params["side"]

    def OnCreate(self):
        self.stack = self.GetElement(INDEX_GRID_NODE)
        self.close_btn = (
            self.GetElement(CLOSE_BTN_NODE).asButton().SetCallback(self.onClose)
        )
        self.main_label = self.GetElement(MAIN_LABEL_NODE)
        self.prior_editor = self.GetElement(PRIOR_EDITOR_NODE).asTextEditBox()
        self.prior_add_btn = (
            self.GetElement(PRIOR_ADD_BTN_NODE).asButton().SetCallback(self.onAddPrior)
        )
        self.prior_sub_btn = (
            self.GetElement(PRIOR_SUB_BTN_NODE).asButton().SetCallback(self.onSubPrior)
        )
        self.updateIndexBox(self.main_label, self.label_value)
        self.updateStack()
        self.updatePriority(self.priority_value)

    def updateStack(self):
        stack_sizex, _ = self.stack.GetSize()
        for i in range(24):
            e = self.stack.AddElement(
                "TransmitterSettingsUI.index_selector", "index_selector%d" % i
            )
            xsize, ysize = e.GetSize()
            e.SetPos((i * xsize % stack_sizex, i // (stack_sizex // xsize) * ysize))
            self.updateIndexBox(e, i)

    def updateIndexBox(
        self,
        ctrl,  # type: UBaseCtrl
        i,  # type: int
    ):
        r, g, b = rand_rgb_by_index(i)
        if i < 0:
            ctrl["color_img"].asImage().SetSpriteColor((0, 0, 0))
            ctrl["index_num"].asLabel().SetColor((1, 1, 1))
        else:
            ctrl["color_img"].asImage().SetSpriteColor((r, g, b))
            ctrl["index_num"].asLabel().SetColor(get_opposite_color(r, g, b))
            ctrl["index_num"].asLabel().SetText("§l%d" % i)
        if i is not None:
            ctrl["btn"].SetPropertyBag({"#index": i})

    def updatePriority(self, priority):
        # type: (int) -> None
        self.priority_value = max(min(priority, 10000), -10000)
        self.prior_editor.SetText(str(self.priority_value))
        TransmitterSetPriority(
            self.dim, self.x, self.y, self.z, self.ap_side, self.priority_value
        ).send()

    @Binder.binding(Binder.BF_ButtonClick, "#transmitter_settings_ui.label_selected")
    def onLabelSelected(self, params):
        # print params
        if params["ButtonState"] != 0:
            return
        button_path = params["ButtonPath"][len("main/") :]
        idx = self.GetElement(button_path).GetPropertyBag().get("#index", -1)
        if idx == -1:
            return
        self.updateIndexBox(self.main_label, idx)
        TransmitterSetLabel(self.dim, self.x, self.y, self.z, self.ap_side, idx).send()

    @Binder.binding(Binder.BF_EditFinished, "#transmitter_settings_ui.prior_editor")
    def onTextEdited(self, params):
        try:
            val = int(params["Text"])
        except ValueError:
            self.prior_editor.SetText(str(self.priority_value))
            return
        self.updatePriority(val)

    def onAddPrior(self, _):
        self.updatePriority(self.priority_value + 1)

    def onSubPrior(self, _):
        self.updatePriority(self.priority_value - 1)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == event.KeyBoardType.KEY_ESCAPE and event.isDown:
            self.RemoveUI()

    def onClose(self, _):
        self.RemoveUI()
