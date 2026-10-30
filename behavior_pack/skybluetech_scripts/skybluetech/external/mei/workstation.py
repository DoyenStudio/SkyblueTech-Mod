# coding=utf-8
"""
机件加工台（MachineryWorkstationUI.main）接上 MEI 的配方转移（ctx.UI.Transfers 的转移处理器）：加工台界面开着时，
配方页上加工台配方的 + 把材料从背包放进加工台。发的是加工台自己的请求（MachineryWorkstationTransferRecipe：坐标 + 产物 id，
和点加工台右边的配方栏是同一个），由蔚蓝的服务端搬：先把格子里原有的退回背包，再从背包按配方放进格子、挑一把够用的扳手 / 钳；
材料不够只放有的那些。MEI 只算清单（缺什么）、管 + 亮不亮和悬停写什么：

- 产物被管理员禁用的灰掉（is_machine_banned，和加工台界面同一个判断）；
- 背包里一样材料都没有的灰掉（和加工台自己的配方栏一样：一件都没有的配方不列）；
- 材料不够照样能点（蔚蓝放有的那些），悬停写缺什么；
- 蔚蓝按产物 id 认配方，认的是这个产物的第一条：产物重复的配方悬停里提醒一句（现在的配方表没有重复）。

**不改蔚蓝的代码、不打补丁**：界面类、请求、禁用表都是蔚蓝现成的，导出里没有，经 exports.InternalModule 取；取不到就不挂，日志点名。
加工台界面本身由 extension.MountScreens 挂上 MEI（机器界面那张表）。
"""
from . import bridge, exports
from .ui_access import Active, ItemId, Path

SCREEN_MODULE = "client.ui.machinery.machinery_workstation"
""" 加工台界面的模块（相对 skybluetech 包）：界面类、它用的配方表 recipes """

EVENT_MODULE = "common.events.machinery.machinery_workstation"
""" 转移请求所在的模块 """

BANS_MODULE = "client.machinery.bans"
""" 管理员禁用表（客户端那一份）"""

CATEGORY = "skybluetech:machinery_workstation"
""" MEI 里加工台配方的类型（machines/machinery_workstation）"""

# 下面这些字进 MEI 配方页的悬停与「没成」提示，MEI 拿 unicode 拼（py2 下带中文的字节串拼不上），所以都写成 unicode
BANNED = u"§c管理员已禁用此配方"
NO_OUTPUT = u"§7这条配方认不出产物"
NOTHING = u"§7背包里一样材料都没有"
PARTIAL = u"§7材料不够的格子会空着"
DUPLICATE = u"§7这个产物有好几条配方，蔚蓝按产物认，放进去的是第一条"
CLOSED = u"§7机件加工台的界面没开着"


def OutputId(recipe):  # type: (any) -> str or None
    """ MEI 配方的主产物 id（str）"""
    try:
        output = recipe.GetPrimaryOutput()
        stacks = output.get_stacks() if output is not None else []
    except Exception:  # noqa
        return None
    return ItemId(stacks[0]) if stacks else None


def Banned(item_id):  # type: (str) -> bool
    try:
        return bool(exports.InternalModule(BANS_MODULE).is_machine_banned(item_id))
    except Exception:  # noqa  禁用表取不到当没禁（服务端照样会拦）
        return False


def SameOutput(item_id):  # type: (str) -> int
    """ 蔚蓝的加工台配方表里产物是它的有几条 """
    try:
        recipes = exports.InternalModule(SCREEN_MODULE).recipes
        return sum(1 for rcp in recipes if Path(rcp.output_item_id) == item_id)
    except Exception:  # noqa
        return 1


def _Notice(message, missing):  # type: (unicode, list) -> any
    """ 能点、但悬停里写几句（MEI 的 TransferError(blocking=False)）；老版本 MEI 没有这个类型就当能点 """
    error = getattr(bridge.Types, "TransferError", None) if bridge.Types is not None else None
    if error is None:
        return None
    return error(message=message, missing=missing, blocking=False)


class WorkstationHandler(object):
    """ 加工台的转移处理器（MEI 的 TransferHandler 形状，鸭子类型：不 import MEI）"""

    GRID = None
    """ 加工台的格子就是配方输入的下标（0~8），不用 MEI 摊 """

    CONSUMES = True
    HINT = u"§7转移至机件加工台"

    def Check(self, request):  # type: (any) -> any
        item_id = OutputId(request.Recipe)
        if item_id is None:
            return NO_OUTPUT
        if Banned(item_id):
            return BANNED
        if request.Slots and all(slot.Have <= 0 for slot in request.Slots):
            return NOTHING
        notes = []
        if SameOutput(item_id) > 1:
            notes.append(DUPLICATE)
        missing = request.Missing()
        if missing:
            notes.append(PARTIAL)
        if not notes:
            return None
        return _Notice("\n".join(notes), missing)

    def Transfer(self, request):  # type: (any) -> any
        return Send(request.Recipe, request.Complete())

    def __call__(self, recipe):  # type: (any) -> any
        """ 老版本 MEI（ctx.UI.Transfers 只认 callback(Recipe)）：照样发请求 """
        return Send(recipe, True) is True


HANDLER = WorkstationHandler()


def Send(recipe, complete):  # type: (any, bool) -> any
    """ 和点加工台配方栏同一套：界面先记下（禁用提示、材料不够的红字预览），发请求，刷新配方栏。成了给 True，没成给原因 """
    module = exports.InternalModule(SCREEN_MODULE)
    screen = Active(module.MachineryWorkstationUI)
    if screen is None:
        return CLOSED
    item_id = OutputId(recipe)
    if item_id is None:
        return NO_OUTPUT
    screen.ban_check_item_id = item_id
    if screen.update_recipe_ban_message():
        return BANNED
    screen.incomplete_preview = None if complete else item_id
    _, x, y, z = screen.pos
    exports.InternalModule(EVENT_MODULE).MachineryWorkstationTransferRecipe(x, y, z, item_id).send()
    screen.refresh_visible_recipes()
    return True


def Mount(ctx):  # type: (any) -> str or None
    """ 登记加工台界面的转移处理器，返回记号；老版本 MEI 没有 ctx.UI.Transfers、蔚蓝这边取不到都不挂 """
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is None:
        ctx.Log.warn("这个版本的 MEI 没有 ctx.UI.Transfers, 机件加工台不接配方转移")
        return None
    try:
        screen_def = Path(exports.InternalModule(SCREEN_MODULE).MachineryWorkstationUI._screen_key)
    except Exception as e:  # noqa  蔚蓝改了结构：不挂，别的照常
        ctx.Log.warn("机件加工台的界面取不到, 不接配方转移: {}".format(bridge.ErrorText(e)))
        return None
    token = transfers.Register(screen_def, HANDLER, categories=[CATEGORY])
    if token:
        ctx.Log.info("机件加工台界面 {} 接上 MEI 的配方转移".format(screen_def))
    return token or None


def Unmount(ctx, token):  # type: (any, str or None) -> None
    if not token:
        return
    transfers = getattr(ctx.UI, "Transfers", None)
    if transfers is not None:
        transfers.Unregister(token)
