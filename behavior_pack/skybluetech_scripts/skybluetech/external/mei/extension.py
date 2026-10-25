# coding=utf-8
"""
MEI 扩展本体。

类定义包在 `Build()` 里是**必须的**，不是风格选择：基类要等
`CreateComponent(...).GetExtensionCls()` 拿到之后才存在，写在模块顶层必然 NameError。
"""
from . import bridge

STATIONS = (
    ("crafting_table", "skybluetech:electric_crafter"),
    ("furnace", "skybluetech:redstone_furnace"),
)
"""
[(MEI 的配方类型 id, 本模组的机器 id)] —— 让这台机器也能开那种配方。

电动合成器能做工作台配方、红石炉能做熔炉烧炼，所以玩家在那两个配方页的
工作站栏里应该看得到它们。**这不是注册新类型**，是往已有类型上加一个图标。
"""


def Build():  # type: () -> type or None
    """ 造出扩展类。没连上 MEI 返回 None """
    if not bridge.IsAvailable():
        return None

    MeiExtension = bridge.Api.GetExtensionCls()

    class SkyblueTechExtension(MeiExtension):
        """ 蔚蓝科技的机器配方 """

        ID = "skybluetech:machines"
        NAME = "skybluetech.mei.ext.name"
        DESCRIPTION = "skybluetech.mei.ext.desc"
        AUTHOR = "wuming233qwq"
        VERSION = "0.2.0"
        """ 0.2.0: 改走蔚蓝 next 框架的正式导出取数 """
        MIN_API_VERSION = bridge.MIN_API_VERSION

        def __init__(self):
            # 构造期**不碰引擎也不碰 MEI** —— 装配器控制构造时机就是为了这个,
            # 在 __init__ 里取东西会撞上时序问题
            self.Registered = []  # type: list  # 已注册的类别 id，供 OnUnload 逐条撤

        def OnInit(self, ctx):
            bridge.Bind(ctx)
            ctx.Log.info("已连上 MEI (扩展 API v{})".format(ctx.ApiVersion))

        def OnRegister(self, ctx):
            from . import machines

            self.RegisterFluidPanel(ctx)

            for name in machines.MACHINES:
                module = machines.Import(name)
                if module is None:
                    continue
                try:
                    category, source, ui_script = module.Build()
                except Exception as e:  # noqa  一台机器造不出来不该带走其余的
                    ctx.Log.error("机器 {} 构建失败: {}".format(name, bridge.ErrorText(e)))
                    continue

                ctx.Registry.SourceRegistry.RegisterCategory(category)
                ctx.Registry.SourceRegistry.RegisterSource(source)
                ctx.Registry.RecipeUIManager.RegisterScript(category.Id, ui_script)
                self.Registered.append(category.Id)

            ctx.Log.info("已注册 {} 个机器配方类型".format(len(self.Registered)))

        @staticmethod
        def RegisterFluidPanel(ctx):
            """
            把「流体」这种条目的槽位面板注册给 MEI。

            **不传 multi_cls** —— 一格流体永远是一种流体，多候选轮播对它没有意义
            （`ctx.UI.Slots.Register` 的第三个参数留空即表示不轮播）。

            用 `getattr` 探测而不是直接调：这个接口是 MEI 后加的，
            装着旧版 MEI 的玩家不该因此整个扩展加载失败 ——
            退化的表现是流体格画成物品图标，难看但能用。
            """
            register = getattr(ctx.UI.Slots, "Register", None)
            if register is None:
                ctx.Log.warn("这个版本的 MEI 没有 ctx.UI.Slots.Register, 流体格将退化成物品格")
                return
            from . import fluids
            register(fluids.KIND, fluids.PanelCls())

        def OnReady(self, ctx):
            """
            往**别人的**配方类型里挂工作站。

            必须在 OnReady 而不是 OnRegister：原版的 crafting_table / furnace
            是 `mei:vanilla` 扩展注册的，OnRegister 阶段它可能还没跑到
            （装配器是三阶段各跑完一轮再进下一阶段，跨扩展依赖只能放这里）。
            """
            for category_id, machine_id in STATIONS:
                category = ctx.Registry.SourceRegistry.GetCategory(category_id)
                if category is None:
                    ctx.Log.warn("类型 {} 不在, 跳过工作站 {}".format(
                        category_id, machine_id))
                    continue
                stacks = ctx.Registry.ItemFactory.GetStacksFromIds([machine_id])
                if not stacks:
                    ctx.Log.warn("拿不到工作站物品 {}".format(machine_id))
                    continue
                # owner 必须填自己的扩展 ID: RemoveStationsByOwner 只撤自己的,
                # 免得卸载时把原版自带的工作站也清了
                category.AddStation(stacks[0], owner=self.ID)

        def OnUnload(self, ctx):
            # OnRegister 注册的每一样都要能在这里撤掉，
            # 否则重进世界时会重复提交并被管理器拒绝
            for category_id in self.Registered:
                ctx.Registry.RecipeUIManager.UnRegisterScript(category_id)
                ctx.Registry.SourceRegistry.UnRegisterCategory(category_id)
            self.Registered = []

            # 挂到别人类型上的工作站要单独撤 —— 那些类型不是我们的, 撤不掉整个
            for category_id, _machine_id in STATIONS:
                category = ctx.Registry.SourceRegistry.GetCategory(category_id)
                if category is not None:
                    category.RemoveStationsByOwner(self.ID)
            bridge.Unbind()

    return SkyblueTechExtension
