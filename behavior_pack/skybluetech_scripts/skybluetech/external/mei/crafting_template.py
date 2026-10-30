# coding=utf-8
"""
合成样板（skybluetech:crafting_template）的设置界面挂上 MEI 的配方转移：
配方页上工作台配方的 +（`ctx.UI.Transfers`）把这条配方写进样板，配方页关掉回到样板界面。

配方摊到 3×3 走 MEI 的 `resolve_input_slot`（形状对着格子摆），标签原料取第一个候选。走蔚蓝自己的上传请求
（`CraftingTemplateSettingsUpload`，和选择框同一条路），服务端照旧认配方、回产物。
**不改蔚蓝的代码、不打补丁**：界面名、活着的界面实例、上传请求都是蔚蓝现成的，导出里没有，经 `exports.InternalModule`
与前置 ToolDelta 的界面池取（导出补上之后换回导出，见 MEI 仓 `docs/thirdparty/skybluetech.md`）。取不到就不挂，日志点名。
界面是 `RegisterUI` + `PushScreen` 开的，照样用 `ctx.UI.Screens` 登记（SDK 的界面代理接得上 PushScreen 开的界面）。
"""
from . import bridge, exports

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
""" 配方转移只接这个类型：样板只认原版工作台配方（蔚蓝服务端也只按这个类型匹配）"""


def Path(value):  # type: (any) -> str
    """ ToolDelta 的 UIPath（或字符串）→ str """
    text = getattr(value, "base", value)
    return text.encode("utf-8") if isinstance(text, unicode) else str(text)  # noqa: F821  py2 的 unicode


def Active(cls):  # type: (type) -> any
    """ 开着的这一类 ToolDelta 界面（实例）；没开着给 None """
    from skybluetech_scripts.tooldelta.ui import GetActiveToolDeltaScreens
    for screen in GetActiveToolDeltaScreens():
        if isinstance(screen, cls):
            return screen
    return None


class Mounted(object):
    """ 挂上了什么，卸载时照着撤 """

    def __init__(self, screen_def):
        self.ScreenDef = screen_def  # type: str
        self.Transfers = []  # type: list  # ctx.UI.Transfers 的记号
        self.ScreenRegistered = False  # type: bool


def _Screen():  # type: () -> any
    """ 样板设置界面的模块；取不到抛 LookupError """
    return exports.InternalModule(SCREEN_MODULE)


def Mount(ctx):  # type: (any) -> Mounted or None
    """
    挂上：界面登记（ctx.UI.Screens）、工作台配方的转移（ctx.UI.Transfers，老版本 MEI 没有就只是没有 +）。
    老版本 MEI 没有界面登记就不挂；蔚蓝这边取不到也不挂
    """
    screens = getattr(ctx.UI, "Screens", None)
    if screens is None:
        ctx.Log.warn("这个版本的 MEI 没有 ctx.UI.Screens, 合成样板不接 MEI")
        return None
    try:
        screen_def = Path(_Screen().CraftingTemplateSettingsUI._screen_key)
    except Exception as e:  # noqa  蔚蓝改了结构：不挂，别的照常
        ctx.Log.warn("合成样板的界面取不到, 不接 MEI: {}".format(bridge.ErrorText(e)))
        return None

    mounted = Mounted(screen_def)
    mounted.ScreenRegistered = bool(screens.Register(screen_def, dict(SCREEN_PARAMS)))
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        token = transfers.Register(screen_def, OnRecipe, categories=[CRAFTING])
        if token:
            mounted.Transfers.append(token)
    ctx.Log.info("合成样板界面 {} 接上 MEI 的配方转移（{} 个）".format(screen_def, len(mounted.Transfers)))
    return mounted


def Unmount(ctx, mounted):  # type: (any, Mounted or None) -> None
    if mounted is None:
        return
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        for token in mounted.Transfers:
            transfers.Unregister(token)
    screens = getattr(ctx.UI, "Screens", None)
    if screens is not None and mounted.ScreenRegistered:
        screens.Unregister(mounted.ScreenDef)


# 配方转移
# ======================================================================================================================
def ActiveScreen():  # type: () -> any
    """ 开着的样板设置界面（ToolDelta 的界面实例）；没开着给 None """
    try:
        cls = _Screen().CraftingTemplateSettingsUI
    except LookupError:
        return None
    return Active(cls)


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


def Cells(recipe):  # type: (any) -> list
    """ 一条工作台配方摊到 3×3 上：空格是 None，标签原料取第一个候选 """
    resolve = bridge.UI.Slots.resolve_input_slot
    cells = []
    for index in range(GRID_SIZE * GRID_SIZE):
        ingredient = resolve(recipe, index, GRID_SIZE)
        stacks = ingredient.get_stacks() if ingredient is not None else []
        cells.append(Cell(stacks[0]) if stacks else None)
    return cells


def OnRecipe(recipe):  # type: (any) -> bool
    """ 配方页上点了工作台配方的 +（样板界面开着时）：整条写进样板；写成了 MEI 关掉配方页 """
    screen = ActiveScreen()
    if screen is None or recipe is None:
        return False
    screen.template_slot_items[:] = Cells(recipe)
    Upload(screen)
    return True
