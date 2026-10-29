# coding=utf-8
"""
合成样板（skybluetech:crafting_template）的设置界面挂上 MEI：

- 工具模式（拿起 MEI 的一样物品再点下去）：点到 3×3 的格子上，那一格就是拿着的那样物品（和在蔚蓝自己的物品选择框里选一样）；
  点到右边的产物格上，照这样物品的工作台配方把 9 格一次填好；
- 配方转移（配方页上工作台配方的 +，`ctx.UI.Transfers`）：这条配方写进样板，配方页关掉回到样板界面。

配方摊到 3×3 走 MEI 的 `resolve_input_slot`（形状对着格子摆），标签原料取第一个候选。都走蔚蓝自己的上传请求
（`CraftingTemplateSettingsUpload`，和选择框同一条路），服务端照旧认配方、回产物。
**不改蔚蓝的代码、不打补丁**：界面名、格子路径、活着的界面实例、上传请求都是蔚蓝现成的，导出里没有，经 `exports.InternalModule`
与前置 ToolDelta 的界面池取（导出补上之后换回导出，见 MEI 仓 `docs/thirdparty/skybluetech.md`）。取不到就不挂，日志点名。
界面是 `RegisterUI` + `PushScreen` 开的，照样用 `ctx.UI.Screens` 登记（SDK 的界面代理接得上 PushScreen 开的界面）。
"""
from . import bridge, exports
from .selectors import Active, Path

SCREEN_MODULE = "client.ui.misc.crafting_template_settings_ui"
""" 样板设置界面的模块（相对 skybluetech 包）"""

EVENT_MODULE = "common.events.misc.crafting_template_settings"
""" 上传请求所在的模块 """

SCREEN_PARAMS = {
    "ContentPaths": ["/panel"],
}
""" 挂 MEI 的参数：整块面板居中、两栏避开它（路径相对界面的 `$screen_content`，MEI 缺省的 RootPath）"""

GRID_SIZE = 3
""" 样板是 3×3，格子按行排：第 i 格在第 i // 3 行、第 i % 3 列 """

CRAFTING = "crafting_table"
""" 产物格按它查配方：样板只认原版工作台配方（蔚蓝服务端也只按这个类型匹配）"""

ALIAS_GRID = "grid"
ALIAS_OUTPUT = "output"


class Mounted(object):
    """ 挂上了什么，卸载时照着撤 """

    def __init__(self, screen_def):
        self.ScreenDef = screen_def  # type: str
        self.Tokens = []  # type: list  # ctx.UI.Drops 的记号
        self.Transfers = []  # type: list  # ctx.UI.Transfers 的记号
        self.ScreenRegistered = False  # type: bool


def _Screen():  # type: () -> any
    """ 样板设置界面的模块；取不到抛 LookupError """
    return exports.InternalModule(SCREEN_MODULE)


def Mount(ctx):  # type: (any) -> Mounted or None
    """
    挂上：界面登记（ctx.UI.Screens）、两个放置目标（ctx.UI.Drops）、工作台配方的转移（ctx.UI.Transfers，老版本 MEI 没有就只是没有 +）。
    老版本 MEI 没有前两样就不挂；蔚蓝这边取不到也不挂
    """
    screens = getattr(ctx.UI, "Screens", None)
    drops = getattr(ctx.UI, "Drops", None)
    if screens is None or drops is None:
        ctx.Log.warn("这个版本的 MEI 没有 ctx.UI.Screens / ctx.UI.Drops, 合成样板不接 MEI 的工具模式")
        return None
    try:
        module = _Screen()
        screen_def = Path(module.CraftingTemplateSettingsUI._screen_key)
        grid_path, output_path = Path(module.GRID_PATH), Path(module.OUT_ITEM_PATH)
    except Exception as e:  # noqa  蔚蓝改了结构：不挂，别的照常
        ctx.Log.warn("合成样板的界面取不到, 不接 MEI: {}".format(bridge.ErrorText(e)))
        return None

    mounted = Mounted(screen_def)
    mounted.ScreenRegistered = bool(screens.Register(screen_def, dict(SCREEN_PARAMS)))
    mounted.Tokens = [token for token in (
        drops.Register(screen_def, grid_path, OnDropGrid, alias=ALIAS_GRID, point=True),
        drops.Register(screen_def, output_path, OnDropOutput, alias=ALIAS_OUTPUT),
    ) if token]
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        token = transfers.Register(screen_def, OnRecipe, categories=[CRAFTING])
        if token:
            mounted.Transfers.append(token)
    ctx.Log.info("合成样板界面 {} 接上 MEI 的工具模式（放置目标 {} 个）与配方转移（{} 个）".format(
        screen_def, len(mounted.Tokens), len(mounted.Transfers)))
    return mounted


def Unmount(ctx, mounted):  # type: (any, Mounted or None) -> None
    if mounted is None:
        return
    drops = getattr(ctx.UI, "Drops", None)
    if drops is not None:
        for token in mounted.Tokens:
            drops.Unregister(token)
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        for token in mounted.Transfers:
            transfers.Unregister(token)
    screens = getattr(ctx.UI, "Screens", None)
    if screens is not None and mounted.ScreenRegistered:
        screens.Unregister(mounted.ScreenDef)


# 放置
# ======================================================================================================================
def ActiveScreen():  # type: () -> any
    """ 开着的样板设置界面（ToolDelta 的界面实例）；没开着给 None """
    try:
        cls = _Screen().CraftingTemplateSettingsUI
    except LookupError:
        return None
    return Active(cls)


def CellAt(screen, pos):  # type: (any, tuple) -> int or None
    """ 点下去的那一点（全局坐标）落在 3×3 的第几格；按网格控件的矩形均分，不靠格子的名字 """
    if pos is None:
        return None
    try:
        control = screen.grid.base
        x0, y0 = control.GetGlobalPosition()
        width, height = control.GetSize()
    except Exception:  # noqa
        return None
    if width <= 0 or height <= 0 or not (x0 <= pos[0] < x0 + width and y0 <= pos[1] < y0 + height):
        return None
    col = int((pos[0] - x0) * GRID_SIZE / width)
    row = int((pos[1] - y0) * GRID_SIZE / height)
    if not (0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE):
        return None
    return row * GRID_SIZE + col


def Cell(stack):  # type: (any) -> tuple or None
    """ 一格存的样子：(物品 id 的 str, aux 的 int)；蔚蓝服务端的校验只认这两种类型 """
    item = getattr(stack, "Item", None)
    if item is None:
        return None
    return Path(item.ItemId), int(item.AuxValue or 0)


def Upload(screen):  # type: (any) -> None
    """ 和蔚蓝自己的选择框一样：界面上画出来、发给服务端（服务端写进手里的样板、回产物），开着的选择框收起 """
    screen.update_template_slots()
    exports.InternalModule(EVENT_MODULE).CraftingTemplateSettingsUpload(screen.template_slot_items).send()
    close = getattr(screen, "close_item_selector", None)
    if callable(close):
        close()


def OnDropGrid(_name, stack, pos):  # type: (any, any, tuple) -> None
    """ 拿着的物品点到 3×3 的某一格：那一格换成它 """
    screen = ActiveScreen()
    index = CellAt(screen, pos) if screen is not None else None
    cell = Cell(stack)
    if index is None or cell is None:
        return
    screen.template_slot_items[index] = cell
    Upload(screen)


def Cells(recipe):  # type: (any) -> list
    """ 一条工作台配方摊到 3×3 上：空格是 None，标签原料取第一个候选 """
    resolve = bridge.UI.Slots.resolve_input_slot
    cells = []
    for index in range(GRID_SIZE * GRID_SIZE):
        ingredient = resolve(recipe, index, GRID_SIZE)
        stacks = ingredient.get_stacks() if ingredient is not None else []
        cells.append(Cell(stacks[0]) if stacks else None)
    return cells


def RecipeCells(item):  # type: (any) -> list or None
    """ 这样物品的第一条工作台配方摊到 3×3 上（没有配方给 None）"""
    result = bridge.Registry.RecipeManager.QueryRecipe(item, "output", types=[CRAFTING])
    recipes = result.get(CRAFTING) or []
    return Cells(recipes[0]) if recipes else None


def OnRecipe(recipe):  # type: (any) -> bool
    """ 配方页上点了工作台配方的 +（样板界面开着时）：整条写进样板；写成了 MEI 关掉配方页 """
    screen = ActiveScreen()
    if screen is None or recipe is None:
        return False
    screen.template_slot_items[:] = Cells(recipe)
    Upload(screen)
    return True


def OnDropOutput(_name, stack):  # type: (any, any) -> None
    """ 拿着的物品点到产物格：照它的工作台配方填满 9 格（没有工作台配方就什么都不做）"""
    screen = ActiveScreen()
    item = getattr(stack, "Item", None)
    if screen is None or item is None:
        return
    cells = RecipeCells(item)
    if cells is None:
        bridge.Info("{} 没有工作台配方, 样板不改".format(item.ItemId))
        return
    screen.template_slot_items[:] = cells
    Upload(screen)
