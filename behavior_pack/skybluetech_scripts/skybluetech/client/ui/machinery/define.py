# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from mod.client.extraClientApi import GetLocalPlayerId
from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from mod.client.extraClientApi import GetMinecraftEnum

from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_FLUID_FULL,
    DEACTIVE_FLAG_FLUID_NOT_MATCH,
    DEACTIVE_FLAG_NO_INPUT,
    DEACTIVE_FLAG_NO_RECIPE,
    DEACTIVE_FLAG_OUTPUT_FULL,
    DEACTIVE_FLAG_POWER_LACK,
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.events.machinery.basic import (
    MachineStatusUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.base_machine import (
    K_DEACTIVE_FLAGS,
)
from skybluetech_scripts.tooldelta.events import CustomC2SEvent
from skybluetech_scripts.tooldelta.events.client import (
    ClientBlockUseEvent,
    OnKeyPressInGame,
)
from skybluetech_scripts.tooldelta.extensions.ui_sync import S2CSync
from skybluetech_scripts.tooldelta.ui import SCREEN_BASE_PATH, ToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault

from .utils import FormatBlockName, PlayLoop, SetHoverText

KeyEnum = GetMinecraftEnum().KeyBoardType
_ESCAPE = KeyEnum.KEY_ESCAPE
BG_PATH = SCREEN_BASE_PATH / "root_panel/bg"
MAIN_PATH = BG_PATH / "main"
TITLE_PATH = BG_PATH / "title_bar/title"
STATUS_LED_PATH = BG_PATH / "title_bar/status_led"

_LED_GREEN = (0.333, 0.761, 0.290)
_LED_AMBER = (0.949, 0.698, 0.200)
_LED_RED = (0.878, 0.282, 0.243)
# 按优先级排列: 红色 (停机) 在前, 琥珀 (待机) 在后; 状态灯取第一个命中的颜色
_LED_REASONS = (
    (DEACTIVE_FLAG_STRUCTURE_BROKEN, _LED_RED, "多方块结构不完整"),
    (DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK, _LED_RED, "多方块结构缺少方块"),
    (DEACTIVE_FLAG_POWER_LACK, _LED_RED, "能量不足"),
    (DEACTIVE_FLAG_OUTPUT_FULL, _LED_RED, "输出已满"),
    (DEACTIVE_FLAG_FLUID_FULL, _LED_RED, "流体已满"),
    (DEACTIVE_FLAG_FLUID_NOT_MATCH, _LED_RED, "流体不匹配"),
    (DEACTIVE_FLAG_NO_INPUT, _LED_AMBER, "缺少输入"),
    (DEACTIVE_FLAG_NO_RECIPE, _LED_AMBER, "无可用配方"),
)
_FLAG_COLORS = dict((flag, color) for flag, color, _ in _LED_REASONS)
# 停机原因 -> 要亮的提示圈 (控件名前缀, 由 gen_machine_ui.py 按部件生成):
#   ring_energy 能量条 / ring_in_* 输入槽 / ring_out_* 输出槽 / ring_tin_* 输入流体槽 / ring_tout_* 输出流体槽
# 通用加工机 (Processor) 缺流体 / 流体不对时设的是 NO_RECIPE (不是 NO_INPUT), 所以 NO_RECIPE 也要点亮输入流体槽
_RING_RULES = (
    (DEACTIVE_FLAG_POWER_LACK, ("ring_energy",)),
    (DEACTIVE_FLAG_OUTPUT_FULL, ("ring_out_",)),
    (DEACTIVE_FLAG_FLUID_FULL, ("ring_tout_",)),
    (DEACTIVE_FLAG_FLUID_NOT_MATCH, ("ring_tin_",)),
    (DEACTIVE_FLAG_NO_INPUT, ("ring_in_", "ring_tin_")),
    (DEACTIVE_FLAG_NO_RECIPE, ("ring_in_", "ring_tin_")),
)


def _SetSpinning(ctrls, on):
    # type: (list[UBaseCtrl], bool) -> None
    "播放 / 暂停序列帧 (齿轮 / 圆锯); 暂停停在当前帧。"
    for ctrl in ctrls:
        base = ctrl.base
        if on:
            if hasattr(base, "PlayAnimation"):
                base.PlayAnimation()
        elif hasattr(base, "PauseAnimation"):
            base.PauseAnimation()


def GetMachineStatus(deactive_flags, is_generator=False, texts=None):
    # type: (int, bool, dict[int, str] | None) -> tuple[tuple[float, float, float], str]
    "停机标志 -> (状态灯颜色, 悬停文字); texts 按标志改写原因文字 (机器自己的待机原因)。"
    if deactive_flags == 0:
        return _LED_GREEN, "§a运行中"
    color = None
    lines = []
    for flag, c, text in _LED_REASONS:
        if not deactive_flags & flag:
            continue
        if flag == DEACTIVE_FLAG_POWER_LACK and is_generator:
            # 发电机与耗电机器共用同一位: 对发电机而言是缓冲已满
            c, text = _LED_AMBER, "能量已满"
        if texts and flag in texts:
            text = texts[flag]
        color = color or c
        lines.append("§7· " + text)
    if color is None:
        return _LED_AMBER, "§e待机"
    head = "§c停机" if color is _LED_RED else "§e待机"
    return color, head + "\n" + "\n".join(lines)

class _RUNTIME:
    GPlayerId = None # type: str | None
    GPos = None # type: tuple[int, int, int, int] | None




class UIOpen(CustomC2SEvent):
    name = "skybluetech:UIOpen"

    def __init__(self, ui_key, sync_id):
        # type: (str, str) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]
        self.sync_id = data["syncId"]

    def marshal(self):
        return {"uiKey": self.ui_key, "syncId": self.sync_id}


class UIClose(CustomC2SEvent):
    name = "skybluetech:UIClose"

    def __init__(self, ui_key, sync_id):
        # type: (str, str) -> None
        self.ui_key = ui_key
        self.sync_id = sync_id

    def unmarshal(self, data):
        # type: (dict) -> None
        self.ui_key = data["uiKey"]
        self.sync_id = data["syncId"]

    def marshal(self):
        return {"uiKey": self.ui_key, "syncId": self.sync_id}


class MachinePanelUI(ToolDeltaScreen):
    EXIT_BTN_PATH = "/ExitBtn"
    allow_esc_exit = False  # type: bool

    def __init__(self, namespace, name, param):
        ToolDeltaScreen.__init__(self, namespace, name, param)
        self.inited = False
        self.dim, self.x, self.y, self.z = self.get_bound_pos()
        sync_id = "machine_%d_%d_%d_%d" % (self.dim, self.x, self.y, self.z)
        self.ui_sync = S2CSync.NewClient(sync_id).Activate()

    def get_bound_pos(self):
        # type: () -> tuple[int, int, int, int]
        return self._init_params["st:dmpos"]

    def _on_create(self):
        ToolDeltaScreen._on_create(self)
        self[self.EXIT_BTN_PATH].asButton().SetCallback(self.OnExit)
        self.inited = True

    def _on_destroy(self):
        ToolDeltaScreen._on_destroy(self)
        self.ui_sync.Deactivate()

    def OnExit(self, params):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0.1, self.RemoveUI)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == _ESCAPE and self.allow_esc_exit:
            self.OnExit(None)


class MachinePanelUIProxy(ToolDeltaScreen):
    IS_GENERATOR = False
    "发电机为 True: 能量位 (b6) 表示缓冲已满而不是能量不足"
    STATUS_TEXTS = {}  # type: dict[int, str]
    "按停机标志改写状态灯的原因文字, 用于机器自己的待机原因 (如电力加热仓的 NO_RECIPE = 已达到设定温度)"
    STATUS_RINGS = {}  # type: dict[int, tuple[str, ...]]
    "按停机标志改写要亮的提示圈前缀; 空元组 = 这个原因不亮提示圈"

    def __init__(self, screen_name, screen_instance, params=None):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        if _RUNTIME.GPos is None:
            raise RuntimeError("Player do not click machine but create UI")
        self.pid = _RUNTIME.GPlayerId
        self.pos = _RUNTIME.GPos
        sync_id = "machine_%d_%d_%d_%d" % _RUNTIME.GPos
        self.ui_sync = S2CSync.NewClient(sync_id)
        self.title_text = ""
        self._title_label = None
        self._status_led = None
        self._status_core = None
        self._status_blink = None
        self._status_flags = None  # type: int | None
        self._rings = []  # type: list[tuple[str, UImage]]
        self._spinners = []  # type: list[UBaseCtrl]
        self._spinner_paths = set()  # type: set[str]

    def _on_create(self):
        ToolDeltaScreen._on_create(self)
        self.ui_sync.Activate()
        self.inited = True
        self._init_frame()

    def _init_frame(self):
        """
        共享框架 (SkybluePanelLib.machine_screen): 标题取方块名; 状态灯 + 停机提示圈按停机标志显示。
        打开时读一次方块数据, 之后由服务端在标志变化时推送 MachineStatusUpdate (不轮询)。
        没有使用共享框架的界面 (如附属自带的整份界面) 没有这些控件, 一律跳过。
        """
        try:
            self._title_label = self.GetElement(TITLE_PATH).asLabel()
        except ValueError:
            self._title_label = None
        block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlock(tuple(self.pos[1:])) or (None, 0))[0]
        if self._title_label is not None and block_id:
            self.title_text = FormatBlockName(block_id)
            self._title_label.SetText(self.title_text)
        try:
            led = self.GetElement(STATUS_LED_PATH)
            self._status_core = led["core"].asImage()
            self._status_blink = led["blink"]
            self._status_led = led
        except ValueError:
            self._status_led = None
        self._rings = []
        try:
            main = self.GetElement(MAIN_PATH)
            names = self.base.GetChildrenName(str(main.getFullPath())) or []
        except ValueError:
            names = []
        for name in names:
            if name.startswith("ring_"):
                self._rings.append((name, main[name].asImage()))
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(tuple(self.pos[1:]))
        flags = 0
        if data is not None:
            flags = GetValueWithDefault(data["exData"], K_DEACTIVE_FLAGS, 0) or 0
        self._ApplyStatus(flags)

    @ToolDeltaScreen.Listen(MachineStatusUpdate)
    def _on_machine_status_update(self, event):
        # type: (MachineStatusUpdate) -> None
        if getattr(self, "inited", False) and (event.x, event.y, event.z) == tuple(self.pos[1:]):
            self._ApplyStatus(event.flags)

    def _ApplyStatus(self, flags):
        # type: (int) -> None
        """
        状态灯颜色 + 悬停文字; 红色 (停机) 时状态灯闪烁。
        停机原因对应的部件亮起脉动提示圈 (颜色同原因, 红色优先)。闪烁 / 脉动都是 JSON 动画自己循环,
        这里只在标志变化时 Play / Stop。
        """
        if flags == self._status_flags:
            return
        self._status_flags = flags
        color, text = GetMachineStatus(flags, self.IS_GENERATOR, self.STATUS_TEXTS)
        if self._status_led is not None:
            self._status_core.SetSpriteColor(color)
            PlayLoop(self._status_blink, color is _LED_RED)
            SetHoverText(self._status_led, text)
        want = {}
        for flag, prefixes in _RING_RULES:
            if not flags & flag:
                continue
            prefixes = self.STATUS_RINGS.get(flag, prefixes)
            if not prefixes:
                continue
            ring_color = _FLAG_COLORS[flag]
            if flag == DEACTIVE_FLAG_POWER_LACK and self.IS_GENERATOR:
                ring_color = _LED_AMBER  # 发电机: 缓冲已满
            for name, _ in self._rings:
                if name.startswith(prefixes) and want.get(name) is not _LED_RED:
                    want[name] = ring_color
        for name, ring in self._rings:
            ring_color = want.get(name)
            if ring_color is not None:
                ring.SetSpriteColor(ring_color)
            PlayLoop(ring, ring_color is not None)
        _SetSpinning(self._spinners, flags == 0)

    def RegisterSpinner(self, ctrls):
        # type: (list[UBaseCtrl]) -> None
        """
        登记会转的进度图标 (齿轮 / 圆锯, JSON 里带 spin 标记): 运行时播放序列帧, 停机时暂停。
        utils.UpdateProgress 第一次更新这类图标时自动调用, 机器脚本不用管; 同一控件只登记一次。
        """
        ctrls = [c for c in ctrls if str(c.getFullPath()) not in self._spinner_paths]
        for c in ctrls:
            self._spinner_paths.add(str(c.getFullPath()))
        self._spinners.extend(ctrls)
        if self._status_flags is not None:
            _SetSpinning(ctrls, self._status_flags == 0)

    def SetTitleSuffix(self, suffix):
        # type: (str) -> None
        "副页面标题: 「机器名 / 页面名」。"
        if self._title_label is not None and self.title_text:
            self._title_label.SetText(
                self.title_text + (" / " + suffix if suffix else "")
            )

    def _on_destroy(self):
        ToolDeltaScreen._on_destroy(self)
        self.ui_sync.Deactivate()

    def OnExit(self):
        self._exitLater()

    def _exitLater(self):
        ExecLater(0, self.RemoveUI)





@ClientBlockUseEvent.Listen()
def onClisBlockUse(event):
    # type: (ClientBlockUseEvent) -> None
    dim = CF.CreateGame(GetLocalPlayerId()).GetCurrentDimension()
    _RUNTIME.GPlayerId = event.playerId
    _RUNTIME.GPos = (dim, int(event.x), int(event.y), int(event.z))