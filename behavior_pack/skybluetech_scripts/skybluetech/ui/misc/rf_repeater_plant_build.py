# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import (
    GetFootPos,
    GetLocalPlayerId,
    GetBlockNameAndAux,
    GetControlMode,
    GetControlModeEnum,
    SetPopupNotice,
)
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.ui import (
    RegistToolDeltaScreen,
    UBaseCtrl,
    ToolDeltaScreen,
)
from ...define.events.machinery.rf_repeater_plant import (
    RFRepeaterPlantBuildRequest,
    RFRepeaterPlantBuildResponse,
)
from ...define.id_enum.machinery import RF_REPEATER_PLANT
from ...user_config.key_mapping import (
    RF_TRANSPORTER_PLANT_BUILD_FINISH,
    RF_TRANSPORTER_PLANT_BUILD_CANCEL,
)
from ...utils.mod_block_event import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
    asModBlockLoadedListener,
    asModBlockRemovedListener,
)

BG_NODE = "/bg"
METER_LABEL_NODE = BG_NODE + "/meter_label"
ESC_BTN_NODE = "/esc_btn"
FINISH_BTN_NODE = "/finish_btn"


@RegistToolDeltaScreen("RFRepeaterPlantBuildUI.main")
class RFRepeaterPlantBuildUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.t = 0
        self.original_x, self.original_y, self.original_z = params["pos"]
        self.active = False

    def OnCreate(self):
        self.meter_label = self.GetElement(METER_LABEL_NODE).asLabel()
        self.esc_btn = (
            self.GetElement(ESC_BTN_NODE).asButton().SetCallback(self.on_cancel_build)
        )
        self.finish_btn = (
            self
            .GetElement(FINISH_BTN_NODE)
            .asButton()
            .SetCallback(self.on_finish_build)
        )
        self.is_support_key = GetControlMode() != GetControlModeEnum().Touch
        self.nearest_machine_pos = None
        self.active = True
        self.disable_finish_btn()
        if self.is_support_key:
            self.esc_btn["key_tip"].SetVisible(True)
            self.finish_btn["key_tip"].SetVisible(True)
        else:
            self.esc_btn["key_tip"].SetVisible(False)
            self.finish_btn["key_tip"].SetVisible(False)

    def OnTicking(self):
        if not self.active:
            return
        self.t += 1
        if self.t % 5 != 0:
            return
        x, y, z = GetFootPos(GetLocalPlayerId())
        distance = hypot(x - self.original_x, y - self.original_y, z - self.original_z)
        if distance < 58:
            color = "§a"
        elif distance <= 64:
            color = "§6"
        elif distance >= 84:
            SetPopupNotice("§c布线距离过远， 已退出布线模式", "§7[§6!§7] §6警告")
            self.RemoveUI()
            return
        else:
            color = "§c"
        self.meter_label.SetText(color + "%.1f" % distance)
        self.test_is_finished()

    def OnDestroy(self):
        self.active = False

    def enable_finish_btn(self):
        self.finish_btn.SetVisible(True)

    def disable_finish_btn(self):
        self.finish_btn.SetVisible(False)

    def test_is_finished(self):
        nearest = get_nearest_plant()
        if nearest is None:
            if self.nearest_machine_pos is not None:
                self.nearest_machine_pos = None
                self.disable_finish_btn()
        else:
            if self.nearest_machine_pos is None:
                self.enable_finish_btn()
            self.nearest_machine_pos = nearest

    def on_cancel_build(self, _):
        SetPopupNotice("已退出布线模式")
        self.RemoveUI()

    def on_finish_build(self, _):
        if self.nearest_machine_pos is None:
            return
        nx, ny, nz = self.nearest_machine_pos
        RFRepeaterPlantBuildRequest(
            self.original_x, self.original_y, self.original_z, nx, ny, nz
        ).send()

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if not event.isDown:
            return
        if event.key == RF_TRANSPORTER_PLANT_BUILD_CANCEL:
            self.on_cancel_build(None)
        elif event.key == RF_TRANSPORTER_PLANT_BUILD_FINISH:
            self.on_finish_build(None)

    @ToolDeltaScreen.Listen(RFRepeaterPlantBuildResponse)
    def onRecvResponse(self, event):
        # type: (RFRepeaterPlantBuildResponse) -> None
        if event.status_code == event.STATUS_SUCC:
            SetPopupNotice(
                "已连接中继器 {} 到 {}".format(
                    (self.original_x, self.original_y, self.original_z),
                    self.nearest_machine_pos,
                ),
                "§a成功",
            )
            self.RemoveUI()
        else:
            display_conn_fail(
                {
                    event.STATUS_ALREADY_CONNECTED: "这两个中继器已连接过",
                    event.STATUS_CANT_CONNECT_SELF: "无法连接自身",
                    event.STATUS_INTERNAL_ERROR: "内部错误1",
                    event.STATUS_INTERNAL_ERROR2: "内部错误2",
                    event.STATUS_INVALID_START: "无效起始点",
                    event.STATUS_INVALID_END: "无效终点",
                    event.STATUS_TOO_FAR: "距离过远",
                    event.STATUS_TOO_FAST: "连接过快",
                }.get(event.status_code, "连接失败: %d" % event.status_code)
            )


loaded_client_machinerys = set()  # type: set[tuple[int, int, int]]


@asModBlockLoadedListener(RF_REPEATER_PLANT)
def onModBlockLoaded(event):
    # type: (ModBlockEntityLoadedClientEvent) -> None
    loaded_client_machinerys.add((event.posX, event.posY, event.posZ))


@asModBlockRemovedListener(RF_REPEATER_PLANT)
def onModBlockRemoved(event):
    # type: (ModBlockEntityRemoveClientEvent) -> None
    loaded_client_machinerys.discard((event.posX, event.posY, event.posZ))


def get_nearest_plant():
    if not loaded_client_machinerys:
        return []
    x, y, z = GetFootPos(GetLocalPlayerId())
    nx, ny, nz = min(
        loaded_client_machinerys,
        key=lambda pos: hypot(pos[0] - x, pos[1] - y, pos[2] - z),
    )
    if hypot(nx - x, ny - y, nz - z) > 4:
        return None
    _, aux = GetBlockNameAndAux((nx, ny, nz))
    layer = (aux & 0b1100) >> 2
    return (nx, ny - layer, nz)


def display_conn_fail(msg):
    # type: (str) -> None
    SetPopupNotice("§6%s" % msg, "§7[§6!§7] §6失败")


def hypot(*dis):
    # type: (float) -> float
    return sum(i**2 for i in dis) ** 0.5
