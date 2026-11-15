# coding=utf-8
import random
import time
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.ui import ToolDeltaScreen, RegistToolDeltaScreen, Binder, SCREEN_BASE_PATH
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from skybluetech_scripts.tooldelta.extensions.ui_pointer import GetMousePosition, SetPointerCallbacks, ShowTip
from skybluetech_scripts.tooldelta.extensions.local_audio import PlayLocalSoundLoop, StopLocalSound
from skybluetech_scripts.skybluetech.common.misc.inscriber_press import EMPTY, SCREEN, HOLD_SECONDS
from skybluetech_scripts.skybluetech.common.events.misc.inscriber_press import PressAction, PressState
from ..recipe_checker.action import CheckUsage

active_screen = None
INSCRIBING_SOUNDS = (
    "sfx.skybluetech.inscribing_press.1",
    "sfx.skybluetech.inscribing_press.2",
    "sfx.skybluetech.inscribing_press.3",
)


@RegistToolDeltaScreen(SCREEN)
class InscriberPressEditorUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.session = params["session"]
        self.graph = list(params["grid"])
        self.hold = None
        self.serial = 0
        self.pending = False
        self.closed = False
        self.last_ping = 0
        self.cells = []
        self.grid = None
        self.playing_sound = None

    def OnCreate(self):
        global active_screen
        active_screen = self
        self.sparks = self.GetElement(SCREEN_BASE_PATH / "panel/sparks")
        grid = self.GetElement(SCREEN_BASE_PATH / "panel/grid_panel_bg/grid").asGrid()
        self.grid = grid
        grid.ExecuteAfterUpdate(self.init_cells)
        ExecLater(0.1, self.init_cells)

    def init_cells(self):
        if self.closed or self.cells or self.grid is None:
            return
        if self.grid.base.GetGridItem(7, 7) is None:
            return
        for index in range(64):
            cell = self.grid.GetGridItem(index % 8, index // 8).asButton()
            SetPointerCallbacks(cell, self.on_move, self.cancel_hold)
            self.cells.append(cell)

    @Binder.binding_collection(Binder.BF_BindBool, "inscriber_cells", "#press_visible")
    def cell_visible(self, index):
        return bool(self.graph[index])

    @Binder.binding(Binder.BF_ButtonClickDown, "#press_cell")
    def on_down(self, args):
        index = args["#collection_index"]
        if self.closed or not self.cells or self.pending or self.hold is not None or not self.graph[index]:
            return
        self.serial += 1
        self.hold = (index, None)
        panel_pos = self.GetElement(SCREEN_BASE_PATH / "panel").GetRootPos()
        cell_pos = self.cells[index].GetRootPos()
        self.sparks.SetPos((cell_pos[0] - panel_pos[0] - 16, cell_pos[1] - panel_pos[1] - 16))
        self.sparks.SetVisible(True)
        self.playing_sound = random.choice(INSCRIBING_SOUNDS)
        PlayLocalSoundLoop(self.playing_sound)
        PressAction(self.session, "start", index, self.serial).send()

    @Binder.binding(Binder.BF_ButtonClickUp, "#press_cell")
    def on_up(self, args):
        self.cancel_hold()

    def cancel_hold(self, args=None):
        self.stop_sound()
        if self.hold is not None:
            PressAction(self.session, "cancel", self.hold[0], self.serial).send()
            self.hold = None
            self.sparks.SetVisible(False)

    def stop_sound(self):
        if self.playing_sound is not None:
            StopLocalSound(self.playing_sound)
            self.playing_sound = None

    def check_pointer(self, point):
        if self.hold is None or point is None:
            return
        cell = self.cells[self.hold[0]]
        x, y = cell.GetRootPos()
        width, height = cell.GetSize()
        if not (x <= point[0] < x + width and y <= point[1] < y + height):
            self.cancel_hold()

    def on_move(self, args):
        self.check_pointer((args["TouchPosX"], args["TouchPosY"]))

    def OnTicking(self):
        if self.closed:
            return
        if not self.cells:
            self.init_cells()
        now = time.time()
        if now - self.last_ping >= 3:
            PressAction(self.session, "ping").send()
            self.last_ping = now
        if self.hold is not None:
            self.check_pointer(GetMousePosition())
        if (self.hold is not None and self.hold[1] is not None
                and now - self.hold[1] >= HOLD_SECONDS):
            index = self.hold[0]
            self.hold = None
            self.pending = True
            self.sparks.SetVisible(False)
            self.stop_sound()
            PressAction(self.session, "finish", index, self.serial).send()

    @Binder.binding(Binder.BF_ButtonClickUp, "#press_close")
    def on_close(self, args):
        self.RemoveUI()

    @Binder.binding(Binder.BF_ButtonClickUp, "#press_tips")
    def on_tips(self, args):
        if self.closed:
            return
        self.end_session()
        self.RemoveUI()
        ExecLater(0, CheckUsage, EMPTY)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def on_key(self, event):
        if event.key == GetMinecraftEnum().KeyBoardType.KEY_ESCAPE and event.isDown:
            self.RemoveUI()

    def OnDeactive(self):
        self.end_session()

    def OnDestroy(self):
        self.end_session()

    def end_session(self):
        global active_screen
        self.stop_sound()
        if not self.closed:
            self.cancel_hold()
            PressAction(self.session, "close").send()
            self.closed = True
        if active_screen is self:
            active_screen = None


@PressState.Listen()
def on_state(event):
    if event.message:
        ShowTip(event.message)
    screen = active_screen
    if screen is None or event.session != screen.session:
        return
    if event.started and screen.hold is not None and event.started == screen.serial:
        # Start after server acknowledgement so packet jitter cannot shorten the hold.
        screen.hold = (screen.hold[0], time.time())
    if event.closed:
        screen.stop_sound()
        screen.closed = True
        screen.hold = None
        screen.RemoveUI()
    elif event.grid is not None:
        screen.graph = list(event.grid)
        screen.pending = False
        for index, cell in enumerate(screen.cells):
            cell.SetVisible(bool(screen.graph[index]))
