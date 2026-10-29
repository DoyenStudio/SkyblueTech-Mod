# coding=utf-8
"""
蔚蓝的几个「选一样物品」的界面接上 MEI 的工具模式（拿起 MEI 的一样物品，再点到界面上）。合成样板在 `crafting_template.py`，这里是另外四个：

| 界面 | 点到哪 | 做什么（都走蔚蓝自己的那条路） |
|---|---|---|
| 电动机件加工台 `ElectricMachineryWorkstationUI.main` | 机器面板任何地方 | 选「产物是这样物品」的那条加工台配方（和点右侧配方栏一样） |
| 冷冻机 `FreezerUI.main` | 机器面板任何地方 | 切到产物是这样物品的那一档（`changeMode`） |
| 物品分流器 `ItemSplitterUI.main` | 设置列表的某一行 | 那一行的物品换成它（`ItemSplitterSettingsSetItem`） |
| 连锁挖矿设置 `ObjUpVeinMinerSettingsUI.main` | 方块列表 | 是方块就加进列表（`ObjUpVeinMinerSettingsUpload`） |

前三个是机器界面，`MountScreens` 已经挂上了 MEI；连锁挖矿的设置是 `RegisterUI` + `PushScreen` 开的界面，这里登记（`ctx.UI.Screens`）。
**不改蔚蓝的代码、不打补丁**：界面类、路径、上传请求都是蔚蓝现成的，导出里没有的经 `exports.InternalModule` 取，取不到的那一个不接、日志点名。
流体分流器不接：MEI 的工具模式只拿得起物品，拿不起流体。
"""
from . import bridge, exports

ALIAS = "skybluetech"
""" 放置目标的别名前缀（回调里看得到）"""

BLOCK_TYPE = "block"
""" 物品的 ItemType 是它才算方块（连锁挖矿只收方块）"""


def Path(value):  # type: (any) -> str
    """ ToolDelta 的 UIPath（或字符串）→ str """
    text = getattr(value, "base", value)
    return text.encode("utf-8") if isinstance(text, unicode) else str(text)  # noqa: F821  py2 的 unicode


def ItemId(stack):  # type: (any) -> str or None
    """ ItemStack 的物品 id（str：蔚蓝服务端的校验只认 str）；拿的不是物品给 None """
    item = getattr(stack, "Item", None)
    return Path(item.ItemId) if item is not None else None


def Active(cls):  # type: (type) -> any
    """ 开着的这一类 ToolDelta 界面（实例）；没开着给 None """
    from skybluetech_scripts.tooldelta.ui import GetActiveToolDeltaScreens
    for screen in GetActiveToolDeltaScreens():
        if isinstance(screen, cls):
            return screen
    return None


def Rect(ctrl):  # type: (any) -> tuple or None
    """ ToolDelta 控件（或 SDK 控件）的全局矩形 (x0, y0, x1, y1)；量不出来给 None """
    control = getattr(ctrl, "base", ctrl)
    try:
        x, y = control.GetGlobalPosition()
        w, h = control.GetSize()
    except Exception:  # noqa
        return None
    if w <= 0 or h <= 0:
        return None
    return x, y, x + w, y + h


def Inside(rect, pos):  # type: (tuple, tuple) -> bool
    return rect is not None and pos is not None and rect[0] <= pos[0] < rect[2] and rect[1] <= pos[1] < rect[3]


class Mounted(object):
    """ 挂上了什么，卸载时照着撤 """

    def __init__(self):
        self.Drops = []  # type: list  # ctx.UI.Drops 的记号
        self.Screens = []  # type: list  # 这里登记的 ctx.UI.Screens


# 电动机件加工台
# ======================================================================================================================
def _Workstation():
    module = exports.InternalModule("client.ui.machinery.electric_machinery_workstation")
    return module, module.ElectricMachineryWorkstationUI


def OnDropWorkstation(_name, stack):  # type: (any, any) -> None
    """ 选产物是这样物品的那条加工台配方：和点右侧配方栏同一套（界面先画、发请求、刷新配方栏）"""
    module, cls = _Workstation()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None:
        return
    if not any(recipe.output_item_id == item_id for recipe in module.recipes):
        bridge.Info("电动机件加工台没有产物是 {} 的配方".format(item_id))
        return
    screen.selected_recipe_id = item_id
    screen.update_recipe_preview()
    _, x, y, z = screen.pos
    module.ElectricMachineryWorkstationSelectRecipe(x, y, z, item_id).send()
    screen.refresh_visible_recipes()


# 冷冻机
# ======================================================================================================================
def _Freezer():
    module = exports.InternalModule("client.ui.machinery.freezer")
    return module, module.FreezerUI


def FreezerMode(recipes, item_id):  # type: (any, str) -> int or None
    """ 产物是这样物品的那一档；没有给 None """
    for mode in range(len(recipes)):
        try:
            if Path(recipes.recipes_mapping[mode].outputs["item"][0].id) == item_id:
                return mode
        except (KeyError, IndexError, AttributeError):
            continue
    return None


def OnDropFreezer(_name, stack):  # type: (any, any) -> None
    module, cls = _Freezer()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None:
        return
    mode = FreezerMode(module.recipes, item_id)
    if mode is None:
        bridge.Info("冷冻机没有产物是 {} 的档".format(item_id))
        return
    screen.changeMode(mode)


# 物品分流器
# ======================================================================================================================
def _Splitter():
    module = exports.InternalModule("client.ui.machinery.item_splitter")
    return module, module.ItemSplitterUI


def SplitterRow(screen, pos):  # type: (any, tuple) -> int or None
    """ 点下去的那一点落在设置列表的第几行（按每一行控件的矩形，列表滚动了也对）"""
    grid = screen.settings_grid
    try:
        rows = grid.GetGridDimension()[1]
    except Exception:  # noqa
        return None
    for index in range(rows):
        try:
            row = grid.GetGridItem(0, index)
        except Exception:  # noqa
            continue
        if row is not None and Inside(Rect(row), pos):
            return index
    return None


def OnDropSplitter(_name, stack, pos):  # type: (any, any, tuple) -> None
    """ 那一行的物品换成拿着的这样（和蔚蓝自己的物品选择框发同一个请求；列表由服务端回传再画）"""
    module, cls = _Splitter()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None:
        return
    index = SplitterRow(screen, pos)
    if index is None:
        return
    close = getattr(screen, "close_item_selector", None)
    if callable(close):
        close()
    _, x, y, z = screen.pos
    module.ItemSplitterSettingsSetItem(x, y, z, index, item_id).send()


# 连锁挖矿设置
# ======================================================================================================================
VEIN_PARAMS = {"ContentPaths": ["/panel"]}
""" 挂 MEI 的参数：整块面板居中、两栏避开它（路径相对界面的 `$screen_content`）"""


def _Vein():
    module = exports.InternalModule("client.ui.misc.object_upgrader_settings.vein_miner")
    return module, module.VeinMinerSettingsUI


def IsBlock(stack):  # type: (any) -> bool
    item = getattr(stack, "Item", None)
    info = getattr(item, "Info", None) if item is not None else None
    return getattr(info, "ItemType", None) == BLOCK_TYPE


def OnDropVein(_name, stack):  # type: (any, any) -> None
    """ 是方块、列表里还没有就加到末尾、选中它，发蔚蓝自己的上传请求（服务端照旧校验）"""
    module, cls = _Vein()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None:
        return
    if not IsBlock(stack):
        bridge.Info("{} 不是方块, 连锁挖矿不收".format(item_id))
        return
    if item_id in screen.vein_blocks:
        screen.current_section = screen.vein_blocks.index(item_id)
        return
    screen.vein_blocks.append(item_id)
    screen.current_section = len(screen.vein_blocks) - 1
    module.ObjUpVeinMinerSettingsUpload(screen.vein_blocks).send()
    screen.grid.SetPropertyBag({"#maximum_grid_items": len(screen.vein_blocks)})


# 挂上 / 撤掉
# ======================================================================================================================
def Mount(ctx):  # type: (any) -> Mounted or None
    """ 四个界面的放置目标（ctx.UI.Drops），连锁挖矿的界面登记（ctx.UI.Screens）。老版本 MEI 没有这两样就不挂；哪一个取不到只跳过它 """
    drops = getattr(ctx.UI, "Drops", None)
    screens = getattr(ctx.UI, "Screens", None)
    if drops is None or screens is None:
        return None
    from skybluetech_scripts.tooldelta.ui import SCREEN_BASE_PATH  # noqa  机器界面的路径从这里算起
    mounted = Mounted()

    def add(label, build):
        try:
            screen_def, path, callback, point = build()
        except Exception as e:  # noqa  蔚蓝改了结构：这一个不接，别的照常
            ctx.Log.warn("{} 接不上 MEI 的工具模式: {}".format(label, bridge.ErrorText(e)))
            return None
        token = drops.Register(screen_def, path, callback, alias="{}:{}".format(ALIAS, label), point=point)
        if token:
            mounted.Drops.append(token)
        return screen_def

    def workstation():
        module, cls = _Workstation()
        return Path(cls._screen_key), Path(module.MAIN_PATH), OnDropWorkstation, False

    def freezer():
        module, cls = _Freezer()
        return Path(cls._screen_key), Path(module.MAIN_PATH), OnDropFreezer, False

    def splitter():
        module, cls = _Splitter()
        return Path(cls._screen_key), Path(module.SETTINGS_VIEW_PATH), OnDropSplitter, True

    def vein():
        _module, cls = _Vein()
        return Path(cls._screen_key), Path(SCREEN_BASE_PATH / "panel/vein_blocks"), OnDropVein, False

    add("workstation", workstation)
    add("freezer", freezer)
    add("splitter", splitter)
    vein_def = add("vein_miner", vein)
    if vein_def and screens.Register(vein_def, dict(VEIN_PARAMS, ContentPaths=list(VEIN_PARAMS["ContentPaths"]))):
        mounted.Screens.append(vein_def)
    ctx.Log.info("蔚蓝的物品选择界面接上 MEI 的工具模式（放置目标 {} 个）".format(len(mounted.Drops)))
    return mounted


def Unmount(ctx, mounted):  # type: (any, Mounted or None) -> None
    if mounted is None:
        return
    drops = getattr(ctx.UI, "Drops", None)
    if drops is not None:
        for token in mounted.Drops:
            drops.Unregister(token)
    screens = getattr(ctx.UI, "Screens", None)
    if screens is not None:
        for screen_def in mounted.Screens:
            screens.Unregister(screen_def)
