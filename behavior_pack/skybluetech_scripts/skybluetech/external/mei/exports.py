# coding=utf-8
"""
蔚蓝侧数据的**唯一接触点**：配方、流体、加载状态一律经正式导出（`common.export.*`）取，
不直接 import `machinery_def` / `id_enum` 这些内部模块。

next 框架的重构里内部结构已经换过一次（`machinery.MACERATOR` 变成
`machinery.Machinery.MACERATOR`，旧写法直接 AttributeError，整台机器注册不上）；
导出门面才是蔚蓝对附属承诺稳定的那一层，见蔚蓝仓 `docs/reference/exports.md`。

导出没覆盖到的东西（机件加工台的工具等级表）也收在这里：顺着导出类找，
找不到就返回空、那一格留空，**不悄悄退回写死的内部路径**。
"""
import sys

WORKSTATION_RECIPE = "MachineryWorkstationRecipe"
""" 机件加工台的导出配方类名；工具等级表挂在它所在的模块上 """


def Recipes():  # type: () -> any
    """ `common.export.recipes`：配方类型、集合与查询 """
    from skybluetech_scripts.skybluetech.common.export import recipes
    return recipes


def Fluids():  # type: () -> any
    """ `common.export.fluids`：流体分类与贴图 """
    from skybluetech_scripts.skybluetech.common.export import fluids
    return fluids


def HasExports():  # type: () -> bool
    """ 当前蔚蓝是不是 next 框架（带正式导出）。不是的话整个接入都做不了 """
    try:
        Recipes()
        Fluids()
    except ImportError:
        return False
    return True


def IsClientLoaded():  # type: () -> bool
    """ 蔚蓝客户端业务是否已就绪；集合要等它加载完才建得出来 """
    from skybluetech_scripts.skybluetech.common.export import events
    return bool(events.IsClientLoaded())


def ListenClientLoaded(callback):  # type: (any) -> None
    """ 蔚蓝客户端就绪时调一次 callback（无参） """
    from skybluetech_scripts.skybluetech.common.export import events
    events.SkyblueTechClientLoaded.Listen()(lambda _event: callback())


def MachineScreens():  # type: () -> list
    """
    用共享机器框架的界面的 screen def（形如 `"AlloyFurnaceUI.main"`），给 MEI 挂载用。

    导出给了面板基类（`client.export.machinery.MachinePanelUIProxy`）但没给清单：顺着它，
    在前置 ToolDelta 的界面注册表里找所有子类代理；取不到就返回空，什么也不挂。
    没有背包的机器对话框不是代理，不在其中。
    """
    try:
        from skybluetech_scripts.skybluetech.client.export.machinery import MachinePanelUIProxy
        from skybluetech_scripts.tooldelta.ui.reg import registeredToolDeltaScreenClasses
    except ImportError:
        return []
    return sorted(
        bound_ui_name
        for screen_cls, _cls_path, bound_ui_name, is_proxy in registeredToolDeltaScreenClasses.values()
        if is_proxy and issubclass(screen_cls, MachinePanelUIProxy)
    )


def IconOf(recipe_cls_name):  # type: (str) -> str
    """ 导出配方类对应的机器（或工具）id，即它的 `recipe_icon_id` """
    cls = getattr(Recipes(), recipe_cls_name, None)
    if cls is None:
        raise LookupError("蔚蓝导出里没有配方类型 {}".format(recipe_cls_name))
    return cls.recipe_icon_id


def NamedCollection(name):  # type: (str) -> any
    """ 按名取蔚蓝的配方集合；集合在蔚蓝客户端加载时建好，取不到多半是时机太早 """
    try:
        return Recipes().RecipesCollection.get_collection(name)
    except KeyError:
        # 金属锤的表蔚蓝客户端加载时不建(只有服务端与指南点击时 import), 联机客户端上就会走到这里
        raise LookupError("蔚蓝配方集合 {} 不存在（客户端还没加载完，或蔚蓝只在服务端建了它）".format(name))


def Collection(recipe_cls_name):  # type: (str) -> tuple
    """ (机器 id, 配方表)：集合按机器 id 命名，机器 id 取导出配方类的 recipe_icon_id """
    icon_id = IconOf(recipe_cls_name)
    return icon_id, _Complete(icon_id, NamedCollection(icon_id))


def _Complete(icon_id, collection):  # type: (str, any) -> any
    """
    登记的集合被同名集合顶掉时，以 MiniJEI 的类别索引补全；没被顶掉原样返回集合本身。

    集合**构造即登记**，而蔚蓝冷冻机 / 模版成型机的服务端类体与每个实例都会
    `RecipesCollection(同名)` 造一个空的或只含一条的 —— 两端共用模块缓存时（单机），
    客户端 `get_collection` 拿到的就是它。类别索引（GetRecipesByCategory）只增不换。
    """
    try:
        known = set(id(recipe) for recipe in collection)
        extra = [r for r in Recipes().GetRecipesByCategory(icon_id) if id(r) not in known]
    except Exception:  # noqa  索引取不到就信集合
        return collection
    if not extra:
        return collection
    from . import bridge
    bridge.Info("蔚蓝配方集合 {} 被同名集合顶掉了(登记 {} 条), 按 MiniJEI 索引补回 {} 条".format(
        icon_id, len(known), len(extra)))
    # 索引是 set, 补回的部分按内容排序 —— 顺序跟运行无关, 每次进世界一样
    return list(collection) + sorted(extra, key=_RecipeKey)


def _RecipeKey(recipe):  # type: (any) -> tuple
    """ 只看产物 / 材料 id 的排序键（GetOutputs / GetInputs 是 RecipeBase 的公共接口）"""
    try:
        return (sorted((cat, sorted(ids)) for cat, ids in recipe.GetOutputs().items()),
                sorted((cat, sorted(ids)) for cat, ids in recipe.GetInputs().items()))
    except Exception:  # noqa
        return [], []


def OwnerConstant(collection, name, default=None):  # type: (any, str, any) -> any
    """ 建出这个集合的模块上的常量；导出没给的机器级常量（如水培床的 POWER_COST）从这里取 """
    # 顺着集合对象找它的模块，而不是写死 machinery_def 的路径 —— 表搬家时常量大概率跟着走
    for module in list(sys.modules.values()):
        try:
            if module is not None and getattr(module, "recipes", None) is collection:
                return getattr(module, name, default)
        except Exception:  # noqa  个别模块的属性访问有副作用, 跳过即可
            continue
    return default


def InternalModule(relative):  # type: (str) -> any
    """
    蔚蓝的内部模块（`skybluetech_scripts.skybluetech.<relative>`）—— **只给导出缺口用**：
    发酵池的配方表、火力 / 地热发电机的常量都不在 `common.export` 里。
    取不到抛 LookupError（那一台不注册，日志点名）。导出补上之后换回导出，见 `skybluetech.md` §8.11。
    """
    name = "skybluetech_scripts.skybluetech." + relative
    module = sys.modules.get(name)
    if module is not None:
        return module
    try:
        return __import__(name, {}, {}, ["__name__"])
    except Exception as e:  # noqa
        raise LookupError("蔚蓝内部模块 {} 取不到: {}".format(name, e))


def WorkstationTools(kind, level):  # type: (str, int) -> list
    """ 机件加工台里等级不低于 level 的扳手（kind="wrench"）/ 钳子（"pincer"）id 表 """
    # 导出只给了配方类，等级 -> 工具的表在它所在模块的 WRENCH_LEVEL2ITEM / PINCER_LEVEL2ITEM 上，
    # 与蔚蓝自己的 get_spec_level_avail_* 同规则（等级 >= level 都认）
    cls = getattr(Recipes(), WORKSTATION_RECIPE, None)
    module = sys.modules.get(getattr(cls, "__module__", None) or "")
    table = getattr(module, kind.upper() + "_LEVEL2ITEM", None)
    if not isinstance(table, dict):
        return []
    return [item_id for tool_level, item_id in sorted(table.items()) if tool_level >= level]
