# coding=utf-8
"""
MEI 接入的**唯一接触点** —— 本包以外的任何地方都不许碰 MeiApi 组件。

为什么要收口成一个模块（而不是谁要用谁去 CreateComponent）：

  1. **写不出 `import MEIScripts.xxx`。** Python 的 import 只在本 addon 的包根下解析，
     MEI 在另一个 addon 里。它的每一样东西 —— 包括扩展基类本身 ——
     都只能从组件实例上取。散点取用等于把这条约束抄很多遍。
  2. **拿不到组件是正常情况。** 玩家没装 MEI 时 CreateComponent 给不出实例，
     这是**软依赖**：不需要在 netease_require.json 里声明 MEI，也不需要为它开分支包。
     判空只在这里做一次。
  3. 门面（ctx.Registry / ctx.Types / …）只存在于生命周期方法的 ctx 上，
     而配方类型子包是在模块级写代码的。Bind() 把它们摊成模块级名字，
     子包 `from ..bridge import Types` 即可。
"""

COMP_NAMESPACE = "MoreEnoughItems"
COMP_NAME = "MeiApi"

MIN_API_VERSION = 2
"""
本扩展要求的最低 MEI 扩展 API 版本。

v2 起才有 RegisterCategory / RegisterSource（v1 是 RegisterProcessor 那套）。
声明高了会被老版本 MEI 拒绝加载，声明低了会在老版本上撞到缺失的接口。
"""

Api = None
""" MeiApi 组件实例。None = 玩家没装 MEI，或还没到能取组件的时机 """

# ctx 的五个门面 + 日志，由 Bind() 在 OnInit 阶段填上。
# **模块级而不是传参**：配方类型子包在模块级就要用到 Types/Registry。
Registry = None
Types = None
UI = None
Utils = None
Const = None
Log = None

Scripts = None
"""
⚠ 逃生舱：整个 MEIScripts 包，**不承诺任何稳定性**。

MEI 任意一次内部重构都可能让基于它写的代码失效，且那是预期行为不是 bug。
本扩展**一处都不该用它** —— 真要用到了，说明公共面缺东西，
该去 MEI 那边把它变成 API，而不是在这里默默依赖内部结构。
留着只是为了排查问题时能临时看一眼。
"""


def Connect():  # type: () -> bool
    """
    取组件。**拿不到返回 False 而不是抛** —— 玩家没装 MEI 是正常情况。

    调用时机有硬要求：`CreateComponent` 要本地玩家 id，
    所以不能在客户端系统构造期调，得挂到 UiInitFinished 这类稍晚的事件上。
    """
    global Api
    if Api is not None:
        return True

    import mod.client.extraClientApi as clientApi
    try:
        player_id = clientApi.GetLocalPlayerId()
        if not player_id:
            return False
        component = clientApi.CreateComponent(player_id, COMP_NAMESPACE, COMP_NAME)
    except Exception:  # noqa  MEI 缺席时引擎的表现未必统一, 一律当"没装"
        return False

    if not component:
        return False
    Api = component
    return True


def IsAvailable():  # type: () -> bool
    return Api is not None


def ApiVersion():  # type: () -> int
    """ 当前 MEI 的扩展 API 版本；没连上返回 0 """
    return int(Api.GetApiVersion()) if Api is not None else 0


def Bind(ctx):  # type: (any) -> None
    """
    把 ctx 拆成模块级名字。由扩展的 OnInit 调一次。

    ctx 是**按扩展实例缓存**的（装配器 `_ContextOf`），四个生命周期方法拿到的是同一个，
    所以绑一次就够，不必每个阶段都绑。
    """
    global Registry, Types, UI, Utils, Const, Log, Scripts
    Registry = ctx.Registry
    Types = ctx.Types
    UI = ctx.UI
    Utils = ctx.Utils
    Const = ctx.Const
    Log = ctx.Log
    Scripts = ctx.Scripts


def Unbind():
    """ 撤掉门面引用。由 OnUnload 调 —— 它们指向的对象属于上一个世界 """
    global Registry, Types, UI, Utils, Const, Log, Scripts
    Registry = Types = UI = Utils = Const = Log = Scripts = None
    # Api 不清: 组件挂在本地玩家上, 跨世界重取的代价没必要付,
    # 且 Connect() 本身是幂等的


def Info(message):  # type: (str) -> None
    """
    日志。**Log 可能还没绑上**（Connect 失败、或在 OnInit 之前），故不能直接用 Log。

    退化到 mod_log 而不是静默丢弃 —— 接不上 MEI 时那几行恰恰是唯一的线索。
    """
    if Log is not None:
        Log.info(message)
        return
    from mod_log import logger
    logger.info("[SkyblueTech/mei] " + str(message))


def ErrorText(error):  # type: (any) -> str
    """ 异常转日志文本，自身绝不抛 —— except 里拼日志一律用它 """
    # py2 的 "{}".format(e) 会走 str(e)，消息是非 ASCII 的 unicode 时抛 UnicodeEncodeError，
    # 于是本该兜住的异常在 except 里换个样子冲出去（MEI engineering.md §7-9 同一条）
    try:
        return str(error)
    except Exception:  # noqa
        try:
            return unicode(error).encode("utf-8")  # noqa
        except Exception:  # noqa
            return repr(error)


def Error(message):  # type: (str) -> None
    if Log is not None:
        Log.error(message)
        return
    from mod_log import logger
    logger.error("[SkyblueTech/mei] " + str(message))
