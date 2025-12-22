from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl, UImage
from skybluetech_scripts.tooldelta.api.client.item import GetItemHoverName
from ...utils.fmt import FormatRF as _formatRF, FormatFluidVolume as _formatFluidVolume
from ...define.fluids import texture as fluid_texture
from ...ui_sync.machines.basic_machine_ui_sync import FluidSlotSync

# TYPE_CHECKING
if 0:
    from typing import Callable, TypeVar

    T = TypeVar("T")
    BtnCb = Callable[[], T]
# TYPE_CHECKING END

INFINITY = float("inf")


def UpdatePowerBar(ui, rf_now, rf_max):
    # type: (UBaseCtrl, int, int) -> None
    if rf_max <= 0:
        return
    top = ui["bar/mask"]
    label = ui["label"]
    top.SetFullSize(
        "y", {"followType": "parent", "relativeValue": min(2, float(rf_now) / rf_max)}
    )
    label.asLabel().SetText(_formatRF(rf_now))


def UpdateFlame(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromTopToBottom", 1 - percent)


def UpdateGenericProgressL2R(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - percent)


def UpdateFluidDisplay(ui, fluid_id, fluid_volume, max_volume):
    # type: (UBaseCtrl, str | None, float, float) -> None
    fluid_img = ui["fluid"].asImage()
    volume_disp = ui["text"].asLabel()
    if fluid_id is None:
        fluid_img.SetFullSize("y", {"followType": "parent", "relativeValue": 0})
    else:
        texture, color = fluid_texture.getBaseTexture(fluid_id)
        texture_path = texture
        fluid_img.SetSprite(texture_path)
        if color is not None:
            r, g, b = color
            if r == 255 and g == 255 and b == 255:
                pass
            else:
                color = (float(r) / 255, float(g) / 255, float(b) / 255)
                fluid_img.SetSpriteColor(color)
    if fluid_volume == INFINITY:
        prgs = 1
    elif max_volume == INFINITY:
        prgs = 0
    else:
        prgs = float(fluid_volume) / max_volume
    volume_disp.SetText(
        "%s / %s" % (_formatFluidVolume(fluid_volume), _formatFluidVolume(max_volume))
    )
    fluid_img.SetFullSize("y", {"followType": "parent", "relativeValue": min(2, prgs)})


def InitFluidDisplay(ctrl, data_cb):
    # type: (UBaseCtrl, BtnCb[tuple[str | None, float, float]]) -> Callable[[], None]
    btn = ctrl["data_btn"].asButton()
    screen_vars = ctrl._root._vars
    current_ctrl = [None]  # type: list[UBaseCtrl | None]

    def get_last_ui_board():
        # type: () -> UBaseCtrl | None
        return screen_vars.get("disp_board")

    def _updateHook():
        elem = get_last_ui_board()
        fluid_id, fluid_vol, max_vol = data_cb()
        UpdateFluidDisplay(ctrl, fluid_id, fluid_vol, max_vol)
        if elem is None or elem is not current_ctrl[0]:
            return
        (elem / "image/label").asLabel().SetText(
            "§d流体类型： §f"
            + (
                (GetItemHoverName(fluid_id) or fluid_id)
                if fluid_id is not None and fluid_id != "加载中.."
                else "空"
            )
            + "\n"
            + "§a体积： §f"
            + _formatFluidVolume(fluid_vol)
            + "\n"
            + "§6容器体积： §f"
            + _formatFluidVolume(max_vol)
        )

    # def onRollOver(params):
    #     prev_board = get_last_ui_board()
    #     if prev_board is not None:
    #         return
    #     e = ctrl._root.AddElement("SkybluePanelLib.DataTextScreen", "fluid_hover_text")
    #     e.SetPos(ctrl.GetRootPos())
    #     e.SetLayer(100)
    #     screen_vars["disp_fluid_databoard"] = e
    #     current_ctrl[0] = e
    #     _updateHook()

    # def onRollOut(params):
    #     prev_board = get_last_ui_board()
    #     if prev_board is not None:
    #         prev_board.Remove()
    #         del screen_vars["disp_fluid_databoard"]
    #     current_ctrl[0] = None

    def onRelease(params):
        prev_board = get_last_ui_board()
        if prev_board is not None:
            prev_board.Remove()
            del screen_vars["disp_board"]
            if screen_vars.get("disp_board_src") is ctrl:
                screen_vars.pop("disp_board_src")
                return
        e = ctrl._root.AddElement("SkybluePanelLib.DataTextScreen", "fluid_hover_text")
        e.SetPos(ctrl.GetRootPos())
        e.SetLayer(100)
        screen_vars["disp_board"] = e
        screen_vars["disp_board_src"] = ctrl
        current_ctrl[0] = e
        _updateHook()
            

    # btn.SetOnRollOverCallback(onRollOver)
    # btn.SetOnRollOutCallback(onRollOut)
    btn.SetCallback(onRelease)
    return _updateHook


def InitFluidsDisplay(ui, fluid_slots, index):
    # type: (UBaseCtrl, list[FluidSlotSync], int) -> Callable[[], None]
    def get_data():
        if len(fluid_slots) == 0:
            fluid_id = "加载中.."
            fluid_volume = 0
            max_volume = 0
        elif len(fluid_slots) <= index:
            fluid_id = None
            fluid_volume = -128
            max_volume = -128
        else:
            fluid = fluid_slots[index]
            fluid_id = fluid.fluid_id
            fluid_volume = fluid.volume
            max_volume = fluid.max_volume
        return fluid_id, fluid_volume, max_volume

    return InitFluidDisplay(ui, get_data)

def UpdateImageTransformColor(
    img, raw_r, raw_g, raw_b, new_r, new_g, new_b, transform_pc
):
    # type: (UImage, float, float, float, float, float, float, float) -> None
    r = raw_r + (new_r - raw_r) * transform_pc
    g = raw_g + (new_g - raw_g) * transform_pc
    b = raw_b + (new_b - raw_b) * transform_pc
    img.SetSpriteColor((r / 255, g / 255, b / 255))


