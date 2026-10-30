# coding=utf-8
"""
蔚蓝的几个「选一样物品」的界面接上 MEI 的工具模式（拿起 MEI 的一样物品，再点到界面上）。合成样板在 `crafting_template.py`，这里是另外四个：

| 界面 | 点到哪 | 做什么（都走蔚蓝自己的那条路） |
|---|---|---|
| 电动机件加工台 `ElectricMachineryWorkstationUI.main` | 机器面板任何地方 | 选「产物是这样物品」的那条加工台配方（和点右侧配方栏一样） |
| 冷冻机 `FreezerUI.main` | 机器面板任何地方 | 切到产物是这样物品的那一档（`changeMode`） |
| 物品分流器 `ItemSplitterUI.main` | 设置列表的某一行 | 那一行的物品换成它（`ItemSplitterSettingsSetItem`） |
| 连锁挖矿设置 `ObjUpVeinMinerSettingsUI.main` | 方块列表 | 是方块就加进列表（`ObjUpVeinMinerSettingsUpload`） |

不收的（没有这个产物的配方 / 档、不是方块、列表满了、点在行与行之间、目标那块被藏起来）回调返回原因或 False：MEI 不放下玩家手里的东西，
原因提示给玩家。被藏起来指机器切到了别的页、MEI 的配方页开着（`ui_access.Shown`）。
前三个是机器界面，`MountScreens` 已经挂上了 MEI；连锁挖矿的设置是 `RegisterUI` + `PushScreen` 开的界面，这里登记（`ctx.UI.Screens`）。
**不改蔚蓝的代码、不打补丁**：界面类、路径、上传请求都是蔚蓝现成的，导出里没有的经 `exports.InternalModule` 取，取不到的那一个不接、日志点名。
流体分流器不接：MEI 的工具模式只拿得起物品，拿不起流体。
"""
from . import bridge, exports
from .ui_access import Active, Inside, ItemId, ItemName, Path, Rect, Shown

ALIAS = "skybluetech"
""" 放置目标的别名前缀（回调里看得到）"""

BLOCK_TYPE = "block"
""" 物品的 ItemType 是它才算方块（连锁挖矿只收方块）"""


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


def OnDropWorkstation(_name, stack):  # type: (any, any) -> any
    """ 选产物是这样物品的那条加工台配方：和点右侧配方栏同一套（界面先画、发请求、刷新配方栏）"""
    module, cls = _Workstation()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None or not Shown(screen, module.MAIN_PATH):
        return False
    if not any(Path(recipe.output_item_id) == item_id for recipe in module.recipes):
        return "电动机件加工台没有产物是 {} 的配方".format(ItemName(stack))
    screen.selected_recipe_id = item_id
    screen.update_recipe_preview()
    _, x, y, z = screen.pos
    module.ElectricMachineryWorkstationSelectRecipe(x, y, z, item_id).send()
    screen.refresh_visible_recipes()
    return True


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


def OnDropFreezer(_name, stack):  # type: (any, any) -> any
    """ 切到产物是这样物品的那一档（和档位按钮一样走 changeMode）；方块数据还没读到时 changeMode 什么也不做，不收 """
    module, cls = _Freezer()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None or screen.freezer_mode is None or not Shown(screen, module.MAIN_PATH):
        return False
    mode = FreezerMode(module.recipes, item_id)
    if mode is None:
        return "冷冻机没有产物是 {} 的档".format(ItemName(stack))
    screen.changeMode(mode)
    return True


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


def OnDropSplitter(_name, stack, pos):  # type: (any, any, tuple) -> any
    """ 那一行的物品换成拿着的这样（和蔚蓝自己的物品选择框发同一个请求；列表由服务端回传再画）；点在行与行之间不收 """
    module, cls = _Splitter()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None or not Shown(screen, module.SETTINGS_VIEW_PATH):
        return False
    index = SplitterRow(screen, pos)
    if index is None:
        return False
    close = getattr(screen, "close_item_selector", None)
    if callable(close):
        close()
    _, x, y, z = screen.pos
    module.ItemSplitterSettingsSetItem(x, y, z, index, item_id).send()
    return True


# 连锁挖矿设置
# ======================================================================================================================
VEIN_PARAMS = {"ContentPaths": ["/panel"]}
""" 挂 MEI 的参数：整块面板居中、两栏避开它（路径相对界面的 `$screen_content`）"""

VEIN_MAX = 256
""" 列表最多几个方块：蔚蓝服务端的 MAX_VEIN_BLOCKS（客户端没有这个常量），超了整份上传被丢掉、界面却多出一条 """


def _Vein():
    module = exports.InternalModule("client.ui.misc.object_upgrader_settings.vein_miner")
    return module, module.VeinMinerSettingsUI


def VeinPath():  # type: () -> any
    """ 方块列表的控件路径（放置目标挂在它上面）"""
    from skybluetech_scripts.tooldelta.ui import SCREEN_BASE_PATH  # noqa  界面的路径从这里算起
    return SCREEN_BASE_PATH / "panel/vein_blocks"


def IsBlock(stack):  # type: (any) -> bool
    item = getattr(stack, "Item", None)
    info = getattr(item, "Info", None) if item is not None else None
    return getattr(info, "ItemType", None) == BLOCK_TYPE


def OnDropVein(_name, stack):  # type: (any, any) -> any
    """ 是方块、列表里还没有就加到末尾、选中它，发蔚蓝自己的上传请求（服务端照旧校验）；不是方块、列表满了不收、说为什么 """
    module, cls = _Vein()
    screen = Active(cls)
    item_id = ItemId(stack)
    if screen is None or item_id is None or not Shown(screen, VeinPath()):
        return False
    if not IsBlock(stack):
        return "{} 不是方块, 连锁挖矿不收".format(ItemName(stack))
    if item_id in screen.vein_blocks:
        screen.current_section = screen.vein_blocks.index(item_id)
        return True
    if len(screen.vein_blocks) >= VEIN_MAX:
        return "最多只能添加 {} 个可连锁采掘方块".format(VEIN_MAX)
    screen.vein_blocks.append(item_id)
    screen.current_section = len(screen.vein_blocks) - 1
    module.ObjUpVeinMinerSettingsUpload(screen.vein_blocks).send()
    screen.grid.SetPropertyBag({"#maximum_grid_items": len(screen.vein_blocks)})
    return True


# 挂上 / 撤掉
# ======================================================================================================================
def Mount(ctx):  # type: (any) -> Mounted or None
    """ 四个界面的放置目标（ctx.UI.Drops），连锁挖矿的界面登记（ctx.UI.Screens）。老版本 MEI 没有这两样就不挂；哪一个取不到只跳过它 """
    drops = getattr(ctx.UI, "Drops", None)
    screens = getattr(ctx.UI, "Screens", None)
    if drops is None or screens is None:
        return None
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
        return Path(cls._screen_key), Path(VeinPath()), OnDropVein, False

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
