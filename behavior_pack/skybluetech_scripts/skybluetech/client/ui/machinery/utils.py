# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.fluids import (
    texture as fluid_texture,
)
from skybluetech_scripts.skybluetech.common.define.fluids.define import (
    BasicFluidTexture,
)
from skybluetech_scripts.skybluetech.common.define.id_enum.fluids import Gas
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STRUCTURE_LACKED_BLOCK_POSES,
    K_STRUCTURE_LACKED_BLOCKS,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    AIR_BLOCK_ID,
)
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl, UImage
from skybluetech_scripts.tooldelta.utils.nbt import (
    NBT2Py,
)

# TYPE_CHECKING
if 0>1:
    import typing

    T = typing.TypeVar("T")
    BtnCb = typing.Callable[[], T]
# TYPE_CHECKING END

INFINITY = float("inf")

FLUID_SMOOTH_FACTOR = 0.05
FLUID_SMOOTH_EPSILON = 0.001
FLUID_FRAME_SIZE = 16

PREVIEW_MASK_GRAY = 0x8F * 1.0 / 0xFF
PREVIEW_MASK_EMPTY_FACTOR = 0.5


def FormatNum(n, fmt="%.2f %s"):
    # type: (float, str) -> str
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    if n == INFINITY:
        return "无限"
    while d < len(suffixes) and n >= 1000:
        d += 1
        n /= 1000.0
    return fmt % (n, suffixes[d])


def FormatRF(rf):
    # type: (float) -> str
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    if rf == INFINITY:
        return "无限 RF"
    while d < len(suffixes) and rf >= 1000:
        d += 1
        rf /= 1000.0
    return "%.2f %sRF" % (rf, suffixes[d])


def FormatFluidVolume(vol):
    # type: (float) -> str
    if vol == INFINITY:
        return "无限"
    elif vol >= 10000:
        return "%.2f B" % (float(vol) / 1000)
    else:
        return "%.0f mB" % vol


def FormatKelvin(k):
    # type: (float) -> str
    if k == INFINITY:
        return "Inf"
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    while d < len(suffixes) and k >= 1000:
        d += 1
        k /= 1000.0
    return "%.2f %sK" % (k, suffixes[d])


def SetHoverText(ctrl, text):
    # type: (UBaseCtrl, str) -> None
    """
    新组件的悬停提示 (子控件 info = SkybluePanelLib.hover_info, 仿原版 highlight_slot + hover_text):
    鼠标悬停 / 触屏按住时由原版 hover_text 渲染器显示; 这里只在文字变化时写 property_bag。
    """
    cache = ctrl._vars
    if cache.get("hover_text") == text:
        return
    cache["hover_text"] = text
    targets = cache.get("hover_targets")
    if targets is None:
        targets = cache["hover_targets"] = [
            ctrl["info/hover/hover_text"],
            ctrl["info/pressed/hover_text"],
        ]
    for target in targets:
        target.SetPropertyBag({"#hover_text": text})


def PlayLoop(ctrl, on):
    # type: (UBaseCtrl, bool) -> None
    """
    显示并播放 / 停止并隐藏一个带 JSON 循环动画的控件 (闪烁层、停机提示圈)。
    动画在 JSON 里自己循环, 这里只在状态变化时调用一次; StopAnimation 会把透明度恢复到首段的 from。
    """
    base = ctrl.base
    if on:
        ctrl.SetVisible(True)
        if hasattr(base, "PlayAnimation"):
            base.PlayAnimation()
    else:
        if hasattr(base, "StopAnimation"):
            base.StopAnimation()
        ctrl.SetVisible(False)


def _FormatEnergy(rf):
    # type: (float) -> str
    return ("%d RF" % rf) if 0 <= rf < 1000 else FormatRF(rf)


ENERGY_LOW = 0.15
"低于此比例: 经典分段能量条换琥珀色贴图"
ENERGY_CRITICAL = 0.05
"低于此比例: 换红色贴图"
# 带电部分: 蔚蓝原有材质 + 两张换色贴图 (gen_textures.py 按原材质的明暗逐像素重画, 不用 color 着色)
_ENERGY_FILLS = (
    "textures/ui/energy_bar_top",
    "textures/ui/skybluetech/energy/orig_fill_amber",
    "textures/ui/skybluetech/energy/orig_fill_red",
)
_ENERGY_LEVEL_TIPS = ("", "\n§e电量偏低", "\n§c电量告急")


def _EnergySegments(ui):
    # type: (UBaseCtrl) -> int
    "经典分段的段数: 内高 = 3 x 段数 + 1 (2u 段 + 1u 缝, 顶上多一道缝); 量不出来就返回 0 (不取整)。"
    try:
        h = int(round(ui["bar"].GetSize()[1]))
    except Exception:
        return 0
    if 10 <= h <= 400 and (h - 1) % 3 == 0:
        return (h - 1) // 3
    return 0


def _QuantizeEnergy(ratio, segments):
    # type: (float, int) -> float
    "按整段显示 (有电至少亮一段), 返回填充层应显示的高度比例。"
    if segments <= 0:
        return ratio
    k = int(ratio * segments + 0.5)
    if ratio > 0 and k == 0:
        k = 1
    return 3.0 * k / (3 * segments + 1)


def UpdatePowerBar(ui, rf_now, rf_max, hover=None):
    # type: (UBaseCtrl, int, int, str | None) -> None
    """
    更新能量条 (SkybluePanelLib.energy_meter_*): 悬停显示储能 / 容量。经典分段 (energy_meter_classic) 的带电层
    写法同原版 PowerBar: 底部锚定的平铺图, 用 SetFullSize 按电量改高度并按整段取整; 低于 15% 换琥珀、
    低于 5% 换红色贴图 (发电机的缓冲见底不算异常, 不变色)。
    hover: 配方页 (MiniJEI) 用, 悬停改写耗能 / 产能, 不写储能。
    """
    if rf_max <= 0:
        return
    cache = ui._vars
    ratio = max(0.0, min(1.0, float(rf_now) / rf_max))
    if "mask" not in cache:
        cache["mask"] = ui["bar/mask"].asImage()
        try:
            ui["classic_style"]  # 经典分段的标记子控件
            cache["classic"] = True
        except ValueError:
            cache["classic"] = False
        cache["segments"] = _EnergySegments(ui) if cache["classic"] else 0
    shown = _QuantizeEnergy(ratio, cache["segments"])
    if cache.get("shown") != shown:
        cache["shown"] = shown
        if cache["classic"]:
            # 同原版 PowerBar: 平铺图不吃 clip, 直接按比例改填充层高度 (底部锚定)
            cache["mask"].SetFullSize("y", UICtrlPosData("parent", relative_value=shown))
        else:
            cache["mask"].SetSpriteClipRatio("fromTopToBottom", 1.0 - shown)
    level = 0
    # 配方页 (hover 非空) 的能量条只表示耗能 / 产能, 随进度增减时不换低电量颜色
    if cache["classic"] and hover is None and not getattr(ui._root, "IS_GENERATOR", False):
        level = 2 if ratio < ENERGY_CRITICAL else (1 if ratio < ENERGY_LOW else 0)
        if cache.get("level") != level:
            cache["level"] = level
            cache["mask"].SetSprite(_ENERGY_FILLS[level])
    if hover is not None:
        SetHoverText(ui, hover)
        return
    SetHoverText(
        ui,
        "§b储能： §f%s\n§7容量： §f%s%s"
        % (_FormatEnergy(rf_now), _FormatEnergy(rf_max), _ENERGY_LEVEL_TIPS[level]),
    )


def UpdateFlame(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromTopToBottom", 1 - percent)


# 进度控件的填充方向标记 (JSON 里 0x0 的隐藏子控件) -> SetSpriteClipRatio 的裁剪方向; 没有标记 = 自左向右
_PROGRESS_MARKERS = (
    ("fill_up", "fromTopToBottom"),
    ("fill_down", "fromBottomToTop"),
    ("fill_left", "fromLeftToRight"),
)


def _HasChild(ui, name):
    # type: (UBaseCtrl, str) -> bool
    try:
        ui[name]
    except ValueError:
        return False
    return True


def UpdateProgress(ui, percent):
    # type: (UBaseCtrl, float) -> None
    """
    通用进度更新 (机器与附属统一用这个): 进度控件 = bg + mask, 填充方向由 JSON 用标记子控件声明 ——
    fill_up 自下而上 / fill_down 自上而下 / fill_left 自右向左, 没有标记为自左向右 (原版箭头、内凹管道)。
    换进度条样式 (箭头 / 内凹管道 / 雪花 / 齿轮 ...) 只改 JSON, 不用改 Python。
    带 spin 标记的图标 (齿轮 / 圆锯) 第一次更新时自动登记到所在界面: 运行时转动, 停机时暂停。
    进度没变时不重复调用引擎接口。
    """
    cache = ui._vars
    clip = cache.get("progress_clip")
    if clip is None:
        clip = "fromRightToLeft"
        for name, direction in _PROGRESS_MARKERS:
            if _HasChild(ui, name):
                clip = direction
                break
        cache["progress_clip"] = clip
        cache["progress_mask"] = ui["mask"].asImage()
        register = getattr(ui._root, "RegisterSpinner", None)
        if register is not None and _HasChild(ui, "spin"):
            register([ui["bg"], ui["mask"]])
    percent = max(0.0, min(1.0, percent))
    if cache.get("progress") != percent:
        cache["progress"] = percent
        cache["progress_mask"].SetSpriteClipRatio(clip, 1 - percent)


def UpdateGenericProgressL2R(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromRightToLeft", 1 - percent)


def UpdateGenericProgressT2B(ui, percent):  # -> Any:
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromTopToBottom", 1 - percent)


def UpdateGenericProgressB2T(ui, percent):
    # type: (UBaseCtrl, float) -> None
    ui["mask"].asImage().SetSpriteClipRatio("fromBottomToTop", 1 - percent)


def GetPreviewMaskColor(id_aux):
    # type: (int | None) -> tuple[float, float, float]
    "槽位虚影遮罩的灰度: 有虚影物品时亮, 缺物品时压暗。"
    gray = PREVIEW_MASK_GRAY * (
        1.0 if id_aux is not None else PREVIEW_MASK_EMPTY_FACTOR
    )
    return (gray, gray, gray)


def GetStructureLackedBlocks(data):
    # type: (dict) -> dict[str, int]
    lacked_blocks = NBT2Py(data.get(K_STRUCTURE_LACKED_BLOCKS, {}))
    if isinstance(lacked_blocks, dict) and lacked_blocks:
        return {str(k): int(v) for k, v in lacked_blocks.items()}
    return {}


def GetStructureLackedBlockPoses(data):
    # type: (dict) -> list[dict]
    """从方块实体数据中解析缺失方块的具体位置列表."""
    raw = NBT2Py(data.get(K_STRUCTURE_LACKED_BLOCK_POSES, []))
    poses = []
    if not isinstance(raw, list):
        return poses
    for item in raw:
        if not isinstance(item, dict):
            continue
        x = item.get("x")
        y = item.get("y")
        z = item.get("z")
        if x is None or y is None or z is None:
            continue
        expected = item.get("expected")
        if isinstance(expected, str):
            expected = [expected]
        if not isinstance(expected, list):
            continue
        actual = item.get("actual")
        poses.append({
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "expected": [str(v) for v in expected],
            "actual": str(actual) if actual else "",
        })
    return poses


def FormatBlockName(block_id):
    # type: (str) -> str
    "把方块 ID 转成玩家能看懂的名字; 空气没有物品名, 单独处理。"
    if not block_id:
        return "未知方块"
    if block_id == AIR_BLOCK_ID:
        return "空气"
    item_name = CF.CreateItem(LEVEL_ID).GetItemHoverName(block_id) or block_id
    return item_name.replace("§r", "").replace("§f", "")


def FormatStructureLackedBlockPoses(poses):
    # type: (list[dict]) -> str
    """将缺失方块位置列表格式化为 '(x, y, z) 应为xxx, 目前xxx' 的多行文本."""
    lines = []
    for pose in poses:
        expected = " / ".join(FormatBlockName(v) for v in pose["expected"])
        actual = FormatBlockName(pose.get("actual") or "")
        lines.append(
            "(%d, %d, %d) 应为%s, 当前为%s"
            % (pose["x"], pose["y"], pose["z"], expected, actual)
        )
    return "\n".join(lines)


def UpdateImageTransformColor(
    img, raw_r, raw_g, raw_b, new_r, new_g, new_b, transform_pc
):
    # type: (UImage, float, float, float, float, float, float, float) -> None
    r = raw_r + (new_r - raw_r) * transform_pc
    g = raw_g + (new_g - raw_g) * transform_pc
    b = raw_b + (new_b - raw_b) * transform_pc
    img.SetSpriteColor((r / 255, g / 255, b / 255))


class FluidDisplayer(object):
    def __init__(self, ctrl, enable_interact=True):
        # type: (UBaseCtrl, bool) -> None
        """
        流体槽 (SkybluePanelLib.fluid_tank): 液面 + 悬停提示 (子控件 info)。
        enable_interact=False: 只画液面, 悬停文字由调用方写 (MiniJEI 配方页写的是配方用量, 不是储罐容量)。
        """
        self.ctrl = ctrl
        self.fluid_id = None
        self.fluid_volume = None
        self.max_volume = None
        self.rendered_display_fluid_id = None
        self.rendered_display_fluid_relative_volume = 0.0
        self.flipbook_frame = 0
        self.flipbook_tick = 0
        self.first_update = True
        self.enable_interact = enable_interact

    def update(self, fluid_id, fluid_volume, max_volume):
        # type: (str | None, float, float) -> None
        self.fluid_id = fluid_id
        self.fluid_volume = fluid_volume
        self.max_volume = max_volume

        self.ctrl["text"].asLabel().SetText(
            "%s / %s"
            % (
                FormatFluidVolume(fluid_volume),
                FormatFluidVolume(max_volume),
            )
        )
        self._update_fluid_img()
        if self.enable_interact:
            self._update_hover()

    def _get_target_relative_volume(self):
        # type: () -> float
        if (
            self.fluid_id is None
            or self.fluid_volume is None
            or self.max_volume is None
        ):
            return 0.0
        elif self.fluid_volume == INFINITY:
            return 1.0
        elif self.max_volume == INFINITY:
            return 0.0
        return float(self.fluid_volume) / self.max_volume

    def _update_fluid_img(self):
        # type: () -> None
        fluid_img = self.ctrl["fluid/img"].asImage()
        target = self._get_target_relative_volume()

        if self.first_update:
            self.first_update = False
            self.rendered_display_fluid_id = self.fluid_id
            rendered = target
        else:
            if self.fluid_id != self.rendered_display_fluid_id:
                if self.rendered_display_fluid_relative_volume <= FLUID_SMOOTH_EPSILON:
                    self.rendered_display_fluid_id = self.fluid_id
                    self.flipbook_frame = 0
                    self.flipbook_tick = 0
                else:
                    target = 0.0
            rendered = self.rendered_display_fluid_relative_volume
            rendered += (target - rendered) * FLUID_SMOOTH_FACTOR
            if abs(target - rendered) <= FLUID_SMOOTH_EPSILON:
                rendered = target
        self.rendered_display_fluid_relative_volume = rendered

        rendered_fluid_id = self.rendered_display_fluid_id
        if rendered_fluid_id is None:
            fluid_img.SetFullSize("y", UICtrlPosData("parent", relative_value=0))
            return

        texture = fluid_texture.GetFluidTexture(rendered_fluid_id)
        fluid_img.SetSprite(texture.texture_path)
        self._update_flipbook(fluid_img, texture)

        if rendered_fluid_id in Gas.all_sub():
            fluid_img.SetAnchorFrom("top_middle")
            fluid_img.SetAnchorTo("top_middle")
        else:
            fluid_img.SetAnchorFrom("bottom_middle")
            fluid_img.SetAnchorTo("bottom_middle")
            fluid_img.SetFullPos("y", UICtrlPosData("none", relative_value=0))
        fluid_img.SetFullSize(
            "y", UICtrlPosData("parent", relative_value=min(1, rendered))
        )

    def _update_flipbook(self, fluid_img, basic_texture):
        # type: (UImage, BasicFluidTexture) -> None
        if basic_texture.flipbook_frames > 1:
            self.flipbook_tick += 1
            if self.flipbook_tick >= basic_texture.ticks_per_frame:
                self.flipbook_tick = 0
                self.flipbook_frame = (
                    self.flipbook_frame + 1
                ) % basic_texture.flipbook_frames
        fluid_img.SetUV(
            (0, self.flipbook_frame * FLUID_FRAME_SIZE),
            (FLUID_FRAME_SIZE, FLUID_FRAME_SIZE),
        )

    def _update_hover(self):
        # type: () -> None
        text = (
            "§d流体类型： §f"
            + (
                (CF.CreateItem(LEVEL_ID).GetItemHoverName(self.fluid_id) or self.fluid_id)
                if self.fluid_id is not None
                else ("未知" if self.max_volume is None else "空")
            )
            + "\n"
            + "§a体积： §f"
            + (
                FormatFluidVolume(self.fluid_volume)
                if self.fluid_volume is not None
                else "未知"
            )
            + "\n"
            + "§6容器体积： §f"
            + (
                FormatFluidVolume(self.max_volume)
                if self.max_volume is not None
                else "未知"
            )
        )
        SetHoverText(self.ctrl, text)
