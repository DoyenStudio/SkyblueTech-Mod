# coding=utf-8
"""
合成样板（skybluetech:crafting_template）的设置界面接上 MEI：

- **配方转移**（ctx.UI.Transfers 的转移处理器）：配方页上工作台配方的 + 把这条配方写进样板，配方页关掉回到样板界面。
  MEI 按样板的 3×3 摊好配方（形状对着格子摆），标签原料挑背包里有的那一样（蔚蓝自己的选择框也是从背包里挑）；
  样板只记配方、不拿东西（CONSUMES 假），材料够不够都能写。
- **工具模式**（ctx.UI.Drops）：拿着 MEI 的一样物品点到某一格 → 那一格换成它（按每一格自己的矩形认点中哪一格，点在缝上不收）；
  点到产物格 → 这样物品只有一条工作台配方就照它写满 9 格，有好几条就开它的配方页（工作台那一类），玩家挑一条点 +；
  没有工作台配方就不收、说为什么（手里的东西不放下）；MEI 的配方页开着（样板面板被藏起来）时两个目标都不收。

都走蔚蓝自己的上传请求（CraftingTemplateSettingsUpload，和选择框同一条路），服务端照旧认配方、回产物。
**不改蔚蓝的代码、不打补丁**：界面名、活着的界面实例、上传请求都是蔚蓝现成的，导出里没有，经 exports.InternalModule
与前置 ToolDelta 的界面池取（导出补上之后换回导出，见 MEI 仓 docs/thirdparty/skybluetech.md）。取不到就不挂，日志点名。
界面是 RegisterUI + PushScreen 开的，照样用 ctx.UI.Screens 登记（SDK 的界面代理接得上 PushScreen 开的界面）。
"""
from . import bridge, exports
from .ui_access import Active, Cell, GridCellAt, ItemName, Path, Shown

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
""" 只接这个类型：样板只认原版工作台配方（蔚蓝服务端也只按这个类型匹配）"""

ALIAS_GRID = "grid"
ALIAS_OUTPUT = "output"
""" 两个放置目标的别名（回调里看得到）"""

NO_RECIPE = "{} 没有工作台配方, 样板不改"


class TemplateHandler(object):
    """ 合成样板的转移处理器（MEI 的 TransferHandler 形状，鸭子类型：不 import MEI）"""

    GRID = (GRID_SIZE, GRID_SIZE)
    CONSUMES = False
    HINT = u"§7把这条配方写进合成样板"  # unicode：MEI 拿它拼悬停，py2 下带中文的字节串拼不上

    def Transfer(self, request):  # type: (any) -> bool
        return Write(CellsOf(request))

    def __call__(self, recipe):  # type: (any) -> bool
        """ 老版本 MEI（ctx.UI.Transfers 只认 callback(Recipe)）：标签原料取第一个候选 """
        return Write(FirstCells(recipe))


HANDLER = TemplateHandler()


class Mounted(object):
    """ 挂上了什么，卸载时照着撤 """

    def __init__(self, screen_def):
        self.ScreenDef = screen_def  # type: str
        self.Transfers = []  # type: list  # ctx.UI.Transfers 的记号
        self.Drops = []  # type: list  # ctx.UI.Drops 的记号
        self.ScreenRegistered = False  # type: bool


def _Screen():  # type: () -> any
    """ 样板设置界面的模块；取不到抛 LookupError """
    return exports.InternalModule(SCREEN_MODULE)


def Mount(ctx):  # type: (any) -> Mounted or None
    """
    挂上：界面登记（ctx.UI.Screens）、工作台配方的转移（ctx.UI.Transfers）、两个放置目标（ctx.UI.Drops）。
    老版本 MEI 没有界面登记就不挂（没有另外两样只是少那一样）；蔚蓝这边取不到也不挂
    """
    screens = getattr(ctx.UI, "Screens", None)
    if screens is None:
        ctx.Log.warn("这个版本的 MEI 没有 ctx.UI.Screens, 合成样板不接 MEI")
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
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        token = transfers.Register(screen_def, HANDLER, categories=[CRAFTING])
        if token:
            mounted.Transfers.append(token)
    drops = getattr(ctx.UI, "Drops", None)
    if drops is not None:
        for token in (drops.Register(screen_def, grid_path, OnDropGrid, alias=ALIAS_GRID, point=True),
                      drops.Register(screen_def, output_path, OnDropOutput, alias=ALIAS_OUTPUT)):
            if token:
                mounted.Drops.append(token)
    ctx.Log.info("合成样板界面 {} 接上 MEI（配方转移 {} 个、放置目标 {} 个）".format(
        screen_def, len(mounted.Transfers), len(mounted.Drops)))
    return mounted


def Unmount(ctx, mounted):  # type: (any, Mounted or None) -> None
    if mounted is None:
        return
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        for token in mounted.Transfers:
            transfers.Unregister(token)
    drops = getattr(ctx.UI, "Drops", None)
    if drops is not None:
        for token in mounted.Drops:
            drops.Unregister(token)
    screens = getattr(ctx.UI, "Screens", None)
    if screens is not None and mounted.ScreenRegistered:
        screens.Unregister(mounted.ScreenDef)


def ActiveScreen():  # type: () -> any
    """ 开着的样板设置界面（ToolDelta 的界面实例）；没开着给 None """
    try:
        cls = _Screen().CraftingTemplateSettingsUI
    except LookupError:
        return None
    return Active(cls)


def Upload(screen):  # type: (any) -> None
    """ 和蔚蓝自己的选择框一样：界面上画出来、发给服务端（服务端写进手里的样板、回产物），开着的选择框收起 """
    screen.update_template_slots()
    exports.InternalModule(EVENT_MODULE).CraftingTemplateSettingsUpload(screen.template_slot_items).send()
    close = getattr(screen, "close_item_selector", None)
    if callable(close):
        close()


def Write(cells):  # type: (list) -> bool
    """ 9 格写进开着的样板并上传；样板界面没开着给 False """
    screen = ActiveScreen()
    if screen is None or cells is None:
        return False
    screen.template_slot_items[:] = cells
    Upload(screen)
    return True


def CellsOf(request):  # type: (any) -> list
    """ MEI 算好的清单（按 3×3 摊开、挑了背包里有的）→ 9 格；空格是 None """
    cells = []
    for index in range(GRID_SIZE * GRID_SIZE):
        slot = request.Cell(index)
        cells.append(Cell(slot.Stack) if slot is not None and slot.Stack is not None else None)
    return cells


def FirstCells(recipe):  # type: (any) -> list
    """ 没有 MEI 的清单可用时（老版本 MEI）：自己摊到 3×3，标签原料取第一个候选 """
    resolve = bridge.UI.Slots.resolve_input_slot
    cells = []
    for index in range(GRID_SIZE * GRID_SIZE):
        ingredient = resolve(recipe, index, GRID_SIZE)
        stacks = ingredient.get_stacks() if ingredient is not None else []
        cells.append(Cell(stacks[0]) if stacks else None)
    return cells


def RecipeCells(recipe):  # type: (any) -> list
    """ 一条工作台配方摊到 3×3：MEI 有 ctx.UI.Transfers.Request 就用它（挑背包里有的），没有就取第一个候选 """
    make = getattr(getattr(bridge.UI, "Transfers", None), "Request", None)
    if callable(make):
        return CellsOf(make(recipe, grid=(GRID_SIZE, GRID_SIZE)))
    return FirstCells(recipe)


def OnDropGrid(_name, stack, pos):  # type: (any, any, tuple) -> any
    """ 拿着的物品点到某一格：那一格换成它、上传；点在格子之间的缝上不收（手里的东西不放下）"""
    screen = ActiveScreen()
    cell = Cell(stack)
    if screen is None or cell is None or not Shown(screen, _Screen().GRID_PATH):
        return False
    index = GridCellAt(screen.grid, GRID_SIZE, GRID_SIZE * GRID_SIZE, pos)
    if index is None:
        return False
    screen.template_slot_items[index] = cell
    Upload(screen)
    return True


def OnDropOutput(_name, stack):  # type: (any, any) -> any
    """ 拿着的物品点到产物格：只有一条工作台配方就照它写满；好几条开它的配方页让玩家挑；没有就不收、说为什么 """
    item = getattr(stack, "Item", None)
    screen = ActiveScreen()
    if item is None or screen is None or not Shown(screen, _Screen().OUT_ITEM_PATH):
        return False
    result = bridge.Registry.RecipeManager.QueryRecipe(item, "output", types=[CRAFTING])
    recipes = result.get(CRAFTING) or []
    if not recipes:
        return NO_RECIPE.format(ItemName(stack))
    actions = getattr(bridge.UI, "Actions", None)
    if len(recipes) > 1 and actions is not None and actions.ShowRecipes(item, CRAFTING):
        return True
    return Write(RecipeCells(recipes[0]))
