# coding=utf-8
"""
通用机器配方页 —— 一台「N 进 1 出」的机器要的东西全在这里。

有了它，接一台机器 = 一个 5 行的模块 + 4 行 JSON（`ui/mei_recipes/`）。
蔚蓝有 22 台机器，一台一份布局和一份脚本是不可接受的。

**槽位映射是唯一有实质逻辑的地方**：蔚蓝的槽位号可以是**稀疏**的
（合金炉有 `{0: 铁粉, 2: 碳粉}` 这种，中间空一格），所以格子与输入
**不能按列表位置对应**，必须按 `Data["input_slots"]` 记下的真实槽位号反查。
按位置对应的话，合金炉的碳粉会显示到第 1 格上。
"""
from .. import bridge, convert, runtime

_UI_SCRIPTS = {}
""" category_id -> 配方页脚本类。只造一次 —— MEI 的 RecipeBinder._RULES_CACHE
    是按类缓存的，每次进世界重造一个新类会让它每进一次世界多留一条 """


def BuildMachine(
        category_id,        # type: str
        icon_id,            # type: str
        name_key,           # type: str
        control_def,        # type: str
        recipes,            # type: any
        input_cells=1,      # type: int
        sort_index=100,     # type: int
        decorate=None,      # type: any
        ui_script=None,     # type: type
        input_kind=convert.CATEGORY_ITEM,    # type: str
        output_kind=convert.CATEGORY_ITEM,   # type: str
        input_slots=None,                    # type: any
        output_slots=None,                   # type: any
        labels=None,                         # type: any
        lores=None,                          # type: any
):  # type: (...) -> tuple
    """
    造出 (CATEGORY, SOURCE, UI_SCRIPT)。机器模块只需要填这几个参数

    **同构机器**（所有输入格同一种类）填 `input_cells` + `input_kind` 就够。

    **异构机器**填 `input_slots` —— 按格的 `(种类, 槽位号)` 表。
    为什么必须是两元组而不是只给一张种类表：蔚蓝的槽位号**按类别分命名空间**，
    金属压印机的两个输入是 `fluid:0` 与 `item:0`，**两个 0**。
    只给种类表的话第 1 格会去问 `item:1`（格子下标被当成了槽位号），
    落空成空格 —— 物品那格永远不出现。见 `skybluetech.md` §7.11.3。

    `output_slots` 同理，给了就是多产物（前缀 `output0..N`）；
    不给则沿用单产物（前缀 `output`，取 `GetPrimaryOutput()`）。
    **已上线的布局全写着那个单数前缀，所以默认分支不能动。**
    """
    category = bridge.Types.RecipeCategory(
        category_id=category_id,
        name_key=name_key,
        icon=(icon_id, 0),
        control_def=control_def,
        # 工作站就是这台机器本身: 玩家在 tab 上看到的图标与要去合成的方块是同一个
        stations=bridge.Registry.ItemFactory.GetStacksFromIds([icon_id]),
        sort_index=sort_index,
    )
    source = runtime.Build().MachineRecipeSource(category_id, recipes, decorate)
    # ui_script 显式传入 = 这台机器的界面**不是** N 进 1 出那个形状,
    # 自己另写一份(机件加工台就是: 3x3 + 工具 + 等级文字)
    return category, source, ui_script or _UIScriptFor(
        category_id,
        SlotTable(input_cells, input_kind, input_slots),
        output_kind,
        SlotTable(0, output_kind, output_slots) if output_slots else None,
        labels, lores)


def SlotTable(cells, kind, table):  # type: (int, str, any) -> tuple
    """
    归一成按格的 `((种类, 槽位号), ...)`

    没给表就按「所有格同一种类、格子下标即槽位号」展开 —— 那正是
    同构机器的情形（磨粉机的三格就是 `item:0/1/2`），**也是老参数的语义**，
    所以旧调用一个字都不用改。
    """
    if table is not None:
        return tuple((str(k), int(s)) for k, s in table)
    return tuple((kind, i) for i in range(cells))


def IngredientForCell(recipe, slot, kind=convert.CATEGORY_ITEM, outputs=False):
    # type: (any, int, str, bool) -> any
    """
    第 `slot` 号槽位该渲染哪个 Ingredient；这一格空着返回 None

    **按真实槽位号反查，不按列表位置。** 见模块头的说明。

    ⚠ 第二个参数是**槽位号**，不是格子下标 —— 同构机器里两者恰好相等
    （`item:0/1/2` 对应第 0/1/2 格），异构机器里不等：金属压印机第 1 格
    要的是 `item:0`。调用方从 `SlotTable` 拿 `(种类, 槽位号)` 再传进来。

    `kind` 是条目种类：槽位号**按类别分命名空间**，金属压印机的
    「物品第 0 格」与「流体第 0 格」是两格不同的东西，不带类别就会取错。
    """
    data = getattr(recipe, "Data", None) or {}
    if outputs:
        slots = data.get("output_slots") or []
        entries = recipe.GetOutputs()
    else:
        slots = data.get("input_slots") or []
        entries = recipe.GetInputs()
    wanted = convert.slot_key(kind, slot)
    for position, key in enumerate(slots):
        if key == wanted and position < len(entries):
            return entries[position]
    return None


POWER_PREFIX = "mei_ui.recipe.power"
""" 电力槽的绑定前缀。与 `common.json` 里 `power_slot` 的默认值必须一致 """

_NL = chr(10)
""" hover 文本的换行。取个名是为了不在别处写转义 """


def FormatRF(value):  # type: (float) -> str
    """ 4800 -> "4.8k RF"；紧凑，给 hover 文本用 """
    value = float(value or 0)
    if value >= 1000000:
        return "%.2fM RF" % (value / 1000000.0)
    if value >= 1000:
        return "%.1fk RF" % (value / 1000.0)
    return "%d RF" % int(value)


def PowerInfo(data):  # type: (dict) -> str
    """
    电力条的 hover 文本。没有电力信息返回空串（无电机型不会走到这儿）。

    ⚠ 蔚蓝的 `power_cost` 是**每 tick 的功率**，不是一次的总量：
    服务端 `ReducePower(running_power)` 每 tick 调一次
    （`server/machinery/basic/upgrade_control.py:88`）。
    磨粉机的 30 实际是 30 × 160 = 4800 RF 一次 —— 差两个数量级，
    所以两个数**都要给**，只给功率会误导。

    条本身不写字（作者裁定：电力条只要那个条），数字全部落在这里。

    > **发电机不走这里**：它们照 minijei 的编排用 `output_power_displayer`
    > + `tick_power` 两个 label 把 RF 直接写出来，布局里压根没有电力条。
    > 见 `GeneratorLabels`。
    """
    if not data:
        return ""
    try:
        cost = int(data.get("power_cost") or 0)
        ticks = int(data.get("tick_duration") or 0)
    except (TypeError, ValueError):
        return ""
    if cost <= 0:
        return ""

    lines = ["§e电力消耗", "§7功率: §f%s/t" % FormatRF(cost)]
    if ticks > 0:
        lines.append("§7耗时: §f%.1f 秒" % (ticks / 20.0))
        lines.append("§7合计: §f%s" % FormatRF(cost * ticks))
    return _NL.join(lines)


def GeneratorLabels(recipe):  # type: (any) -> dict
    """
    发电机的两个 RF 标签，照 minijei 的分工：
    `output_power` 写**一次运行的总量**、`tick_power` 写**功率**。

    minijei 的原文是
    `RFOutputDisplayer(panel["output_power"], output_power * tick_duration)`
    与 `panel["tick_power"].SetText(FormatRF(output_power) + "/t")`
    （`client/mini_jei/machinery/define.py:GeneratorRecipeRenderer`）。
    两个数缺一不可：只给功率看不出一次能发多少，只给总量看不出快慢。
    """
    data = getattr(recipe, "Data", None) or {}
    try:
        rate = int(data.get("output_power") or 0)
        ticks = int(data.get("tick_duration") or 0)
    except (TypeError, ValueError):
        return {}
    if rate <= 0:
        return {}
    return {
        "/rfout/rf/rf_label": FormatRF(rate * ticks) if ticks else FormatRF(rate),
        "/rfout/tick_power": FormatRF(rate) + "/t",
    }


class PowerPanel(object):
    """
    电力条这一格交给绑定读的东西。**不是 ItemPanel** —— 这一格没有物品。

    绑定读的是属性名（`GetBindingValue` 就是 `getattr(panel, attr, default)`），
    所以只要把用到的那几个摆出来即可：
      · `HoverText`            <- `.overlay.btn.hover_text`
      · `OverlayControlVisible` <- `.overlay.visible`，**默认是 False，
        不显式给 True 的话 overlay 整个不可见 ⇒ 没有 hover**
    其余（renderer / label / background 的可见性）保持默认 False 就对了：
    这一格压根没有那些子控件。
    """

    __slots__ = ("HoverText", "OverlayControlVisible")

    def __init__(self, hover_text):
        self.HoverText = hover_text
        self.OverlayControlVisible = True

    def Destroy(self):
        """
        拆除钩子。本面板不持有任何控件，没东西要放。

        **不能不写**：MEI 拆面板时会调它（`RemoveGroupByIndex` →
        `__DestroyPanelByKey`），而那条路径是从绑定/点击回调里进来的 ——
        少一个方法就是 `AttributeError`，把那条绑定当场带走且零日志
        （引擎结论 §15）。2026-09-05 实机：切个 TypeTab 整页就死了。
        MEI 那边已经改成 `getattr` 探测，这里仍然显式写一个：
        它是面板契约的一部分，不该指望对方宽容。
        """
        pass


_BASE = None


def BuildBase():  # type: () -> type
    """
    所有机器配方页的基类。**进度条驱动在这里，子类继承就自动有。**

    自定义界面的机器（加工台、模板机）原先各写各的 `RecipeUIScript` 子类，
    于是布局里有进度条、却没人去裁它的 mask —— 动画不动
    （2026-09-04 实机，模板机换了进度条美术后暴露）。
    ⇒ 驱动收进基类，子类只管 `InitControls` 抓自己的槽位。
    """
    global _BASE
    if _BASE is not None:
        return _BASE

    RecipeUIScript = bridge.UI.Binding.RecipeUIScript
    RecipeBinder = bridge.UI.Binding.RecipeBinder

    class MachineUIScriptBase(RecipeUIScript):
        """ 带进度条与电力驱动的配方页基类 """

        CONTENT_CANDIDATES = ("/wrapper/content/body", "/wrapper/content")
        """
        内容根的候选，**按顺序试第一个存在的**。

        有电的布局把三格收进了 `body`（左边让出 20px 给电力条），无电的没有那一层。
        在这里解析一次之后，子类一律用 `self.Child("/input/0")`
        —— **子类因此不必知道自己带不带电**，那是布局的事。
        少一处「Python 与 JSON 都要声明一遍」就少一处会不一致的地方。
        """

        POWER_BAR_PATH = "/wrapper/content/power/bar/bar/mask"
        """
        电力条 mask 的路径。**电力条在 `body` 外面**，所以是固定的绝对路径。

        `/power/bar/bar/mask` 是两层 `bar`：外层是 `power_slot` 里那个
        `bar@SkybluePanelLib.PowerBar` 实例，它内部又有一个叫 `bar` 的面板
        装着 bg/mask/frame。

        **找不到就跳过 —— 这就是「有电 / 无电」的唯一判据**：
        无电机型的布局里压根没有 `power` 控件，所以 Python 侧不必再声明一遍。
        """

        def __init__(self, recipe):
            RecipeUIScript.__init__(self, recipe=recipe)
            self.ContentPath = self.CONTENT_CANDIDATES[-1]
            self.ProgressMaskImage = None
            self.ProgressPeriod = None  # type: int or None
            self.PowerMaskImage = None

        def Find(self, path):  # type: (str) -> any
            """
            按**绝对路径**取控件（相对配方行）。

            `RecipeControl` 可能是 `None` —— grid 子控件首次渲染前不可访问
            （MEI 引擎结论 §5）。MEI 侧已经守住不拿 None 调 `OnCreate`，
            但这里再守一道：这是第三方都会碰的公共契约，
            而失败发生在绑定回调里 —— 抛出去就是那条绑定当场失效且零日志。
            """
            control = self.RecipeControl
            return control.GetChildByPath(path) if control is not None else None

        def Child(self, relative):  # type: (str) -> any
            """ 取内容区里的控件。相对内容根（`body` 或 `content`），子类都走这个 """
            return self.Find(self.ContentPath + relative)

        # 子类只管这个: 抓自己的槽位控件
        def InitControls(self):
            pass

        LABELS = None
        """
        `(recipe) -> {相对路径: 文字}`。给**逐条配方各不相同的自由文字**用。

        **为什么可以直推 label 而不必走绑定**：MEI 是
        `RecipeUIScriptList.append(cls(recipe))` —— **每条配方一个脚本实例**，
        `OnCreate` 各跑一次且拿到的就是自己那一行的控件
        （`recipe_details/script.py:808` 与 :1114）。翻页/切类型会
        `ClearRecipeUIScripts` 全销毁重建，所以不存在"控件复用了但文字还是旧的"。
        这也正是 minijei 的做法（`panel["tick_power"].asLabel().SetText(...)`）。

        > 与槽位 hover 的分工：**hover 放补充说明，label 放读配方必须看到的数**。
        > 发电机的 RF、蒸馏仓的温度、工业研究的经验都属后者 —— minijei 把它们
        > 画成可见文字是对的，藏进 hover 等于让玩家先猜再验证。
        """

        LORES = None
        """
        `(recipe) -> {绑定前缀: lore}`。给**格子的补充说明**用。

        与 `LABELS` 的分工（§7.14.5 定的那条）：
          · `LABELS` —— **读这条配方必须看到的数**，画成可见 label；
          · `LORES`  —— **补充说明**，进 hover，不占版面。
        冷冻机那句「需在机器里设置对应产物」属后者。

        键是**绑定前缀**（`mei_ui.recipe.output`）而不是控件路径：
        lore 是面板对象的属性，不是控件上的文字。
        """

        def LoreFor(self, prefix):  # type: (str) -> str or None
            """ 取某个前缀的 lore。没声明就返回 None（不碰 lore）"""
            if not self.LORES:
                return None
            try:
                return (self.LORES(self.Recipe) or {}).get(prefix)
            except Exception as e:  # noqa  一句说明不该带走整页
                bridge.Error("lore 取值失败: {}".format(bridge.ErrorText(e)))
                return None

        def ApplyLabels(self):
            """ 把 `LABELS` 算出的文字推到控件上。**由基类的 OnCreate 调** """
            if not self.LABELS:
                return
            try:
                texts = self.LABELS(self.Recipe) or {}
            except Exception as e:  # noqa  文字算错不该带走整页
                bridge.Error("标签取值失败: {}".format(bridge.ErrorText(e)))
                return
            for path, text in texts.items():
                control = self.Child(path)
                if control is None:
                    # 布局改过而 Python 没跟上。不出声的话表现只是"少一行字",
                    # 与"这条配方本来就没有这个数"分不出来
                    bridge.Error("找不到标签控件 {} —— 布局改过?".format(path))
                    continue
                try:
                    control.asLabel().SetText(text)
                except Exception as e:  # noqa
                    bridge.Error("标签 {} 写入失败: {}".format(path, bridge.ErrorText(e)))

        _POWER_CACHE = {}
        """ 配方类型 -> 有没有电力控件。理由同 _CONTENT_CACHE """

        _CONTENT_CACHE = {}
        """ 配方类型 -> 内容根路径。**按类型缓存**，不按行。

            布局是每个配方类型固定的，没必要每行都探一遍；
            **而且引擎对每次取不到的 `GetChildByPath` 都会打一条 WARN**
            （实机日志里刷屏的 `can't not get ctrl ... /content/body` 就是它）。
            按类型缓存之后，每种机器最多只探一次。 """

        def ResolveContent(self):
            """ 定位内容根。**必须在 InitControls 之前** —— 那里要用 self.Child """
            cached = self._CONTENT_CACHE.get(self.TYPE)
            if cached is not None:
                self.ContentPath = cached
                return
            for path in self.CONTENT_CANDIDATES:
                if self.Find(path) is not None:
                    self.ContentPath = path
                    break
            self._CONTENT_CACHE[self.TYPE] = self.ContentPath

        def InitProgress(self):
            """ 抓进度条并把裁剪方向设一次。**由基类的 OnCreate 调，子类不用管** """
            mask = self.Child("/progress/mask")
            self.ProgressMaskImage = mask.asImage() if mask else None
            if self.ProgressMaskImage is not None:
                # 方向是控件的静态属性, 只设一次。JSON 里的 clip_direction 与这里的
                # 枚举**不是同一套词**, 所以显式设, 不指望 layout 那个值
                self.ProgressMaskImage.SetClipDirection("fromRightToLeft")
            self.ProgressPeriod = self.PeriodOf(self.Recipe)
            # ⚠ **不要**在这里给无耗时的配方推一个"满进度"。
            # 2026-09-04 试过 `SetSpriteClipRatio(0)`，想让静止的箭头看起来完整，
            # 结果是**箭头整根变白** —— mask 那张图是高亮层，推满就等于全程高亮，
            # 比"半截箭头"难看得多（作者实测）。
            # 无耗时就让它停在布局给的初值上，那才是"这条配方没有时长"的样子。

        def InitPower(self):
            """
            抓电力条并把裁剪方向设一次。无电机型没有这个控件，整段跳过。

            方向是控件的静态属性，只设一次；电从上往下消 ⇒ `fromTopToBottom`。
            """
            has_power = self._POWER_CACHE.get(self.TYPE)
            if has_power is None:
                has_power = self.Find("/wrapper/content/power") is not None
                self._POWER_CACHE[self.TYPE] = has_power
            if not has_power:
                return                       # 无电机型, 本来就没这个控件
            mask = self.Find(self.POWER_BAR_PATH)
            if mask is None:
                # **有 power 却没 mask = 布局改过**。不出声的话,
                # 表现只是"条不动", 与"调用被引擎忽略"完全分不出来 ——
                # 2026-09-06 就是卡在这个分岐上猜了好几轮
                bridge.Error("电力条缺少 {} —— 布局改过?".format(self.POWER_BAR_PATH))
                return
            # 不用 asImage(): SetFullSize 是 BaseUIControl 的方法
            self.PowerMaskImage = mask

        @RecipeBinder.Group([POWER_PREFIX])
        def PowerPanelCallback(self, index):
            """
            电力条的 hover 文本。

            走 `RecipeBinder.Group` 而不是自己注册绑定：hover 那一整套
            （高亮框 + `#<prefix>.overlay.btn.hover_text`）都在
            `mei_common.slot_overlay` 里，白送。

            **规则挂在基类上，所有机器都继承**，无电的也不例外 —— 但它们的布局里
            没有 `power_slot`，没有控件引用那些绑定名，引擎就永远不会拉取，
            回调一次都不会跑。⇒ 不需要在 Python 侧再声明一遍"我有没有电"。

            **一定要返回面板对象，不能返回 None**：`__EnsureItemPanelVisible`
            拿到空值会记一条错并把这一格判为不可见（旧版本是直接 raise，
            那会在绑定回调里当场炸掉整条绑定且零日志）。
            """
            _ = index
            return PowerPanel(PowerInfo(getattr(self.Recipe, "Data", None)))

        @staticmethod
        def PeriodOf(recipe):  # type: (any) -> int or None
            """
            走完一格进度要几拍；这条配方没有耗时就返回 None（进度条静止）

            `tick_duration` 是**游戏刻**（20/秒），而节拍是 0.2 秒 = 4 游戏刻。
            上限 100 拍(20 秒)：几分钟的配方按真实时长走，进度条看着就是不动的。
            """
            data = getattr(recipe, "Data", None) or {}
            duration = data.get("tick_duration")
            if not duration:
                return None
            return max(1, min(100, int(duration) // 4))

        def OnAnimTick(self, ticks):
            """
            推进进度条。

            传 **1 - 进度**：官方示例明说"模拟进度时裁剪比例需设为(1-进度)"。
            ⚠ `SetSpriteClipRatio` 是**单参数**方法，方向另有 `SetClipDirection` ——
            minijei 那边看着像两参数，那是 ToolDelta 的包装器把两个引擎调用
            合成了一个（`engineering.md` §5.1b）。
            """
            if not self.ProgressPeriod:
                return
            # **周期取 P+1 帧而不是 P 帧**：`ticks % P / P` 只能取到
            # 0, 1/P … (P-1)/P —— **永远到不了 100%**。
            # 慢机型看不出（磨粉机 P=40，缺 2%），快机型很难看：
            # 金属冲压机 P=10 ⇒ 箭头走到 90% 就啪地弹回去，
            # 观感是"动画坏了"而不是"这一轮结束了"（2026-09-04 作者反馈）。
            # 多走一帧就能停在满格上一拍再归零。
            period = self.ProgressPeriod
            ratio = float(ticks % (period + 1)) / period
            if self.ProgressMaskImage is not None:
                self.ProgressMaskImage.SetSpriteClipRatio(1 - ratio)
            if self.PowerMaskImage is not None:
                # **满 → 空**, 与进度条同一个周期: 一次合成正好放完一格电。
                # (发电机没有这个控件 —— 它们用 minijei 那两个 RF label)
                #
                # 裁剪而不是改高度: 控件在 grid item 里, 改布局会让引擎去更新
                # 控件集合, 走到 grid 的**模板**控件上就断言(CLAUDE.md 引擎结论 §17)。
                # 为此 mask 在布局里已改成满高($mask_size), 靠裁剪表现电量。
                try:
                    # PowerBar 的 mask 写了字面 `clip_ratio`, 裁剪比例被钉死
                    # (引擎结论 §19) ⇒ 只能撑高度。
                    # 机器界面的 UpdatePowerBar 用的也是它。
                    self.PowerMaskImage.SetFullSize(
                        "y", {"followType": "parent", "relativeValue": 1.0 - ratio})
                except Exception as e:  # noqa  一格动画不该带走整条绑定(引擎结论 §15)
                    bridge.Error("电力条动画失败: {}".format(bridge.ErrorText(e)))
                    self.PowerMaskImage = None

        def OnCreate(self):
            self.ResolveContent()      # 必须最先: 后面几步都按内容根取控件
            self.InitControls()
            self.InitProgress()
            self.InitPower()
            self.ApplyLabels()

        def OnDestroy(self):
            self.DestroyBindings()

    _BASE = MachineUIScriptBase
    return _BASE


def _UIScriptFor(category_id, input_table, output_kind, output_table,
                 labels=None, lores=None):
    # type: (str, tuple, str, any, any, any) -> type
    """
    通用「N 进 M 出」配方页。进度条与电力条驱动来自 `BuildBase()`

    `input_table` 是按格的 `(种类, 槽位号)`，因此同一份脚本能覆盖
    「物 ⇄ 流体」四种组合（榨油机 物→流 / 冷凝器 流→物），
    也能覆盖**一格流体 + 一格物品**（金属压印机、搅拌机、热反应发电机）。

    `output_table` 为 `None` 时是单产物（旧行为，前缀 `mei_ui.recipe.output`）；
    给了表就是多产物（前缀 `output0..N`），岩浆离心机用它。
    """
    cached = _UI_SCRIPTS.get(category_id)
    if cached is not None:
        return cached

    RecipeBinder = bridge.UI.Binding.RecipeBinder
    render_slot = bridge.UI.Slots.render_slot

    input_prefixes = ["mei_ui.recipe.input%d" % i for i in range(len(input_table))]
    # 单产物沿用**单数**前缀: 已上线的九台布局全写着 `mei_ui.recipe.output`,
    # 改成 output0 会让它们的产物格集体失联(绑定名对不上, 且零报错)
    output_prefixes = (["mei_ui.recipe.output%d" % i for i in range(len(output_table))]
                       if output_table else ["mei_ui.recipe.output"])

    class MachineUIScript(BuildBase()):
        """ N 进 M 出的机器配方页。布局见 ui/mei_recipes/common.json """

        TYPE = category_id
        INPUT_TABLE = input_table
        OUTPUT_TABLE = output_table
        OUTPUT_KIND = output_kind
        LABELS = staticmethod(labels) if labels else None
        LORES = staticmethod(lores) if lores else None
        """ **必须 staticmethod**: 直接挂函数会被 py2 当成未绑定方法,
            调用时第一个参数变成 self（`unbound method ... must be called with
            instance as first argument`）"""

        def __init__(self, recipe):
            BuildBase().__init__(self, recipe)
            self.InputControls = {}
            self.OutputControls = {}
            self.MaxVolume = {}
            """ (是否产物) -> 该方向流体格的体积分母。见 CacheMaxVolume """

        def InitControls(self):
            for i in range(len(self.INPUT_TABLE)):
                self.InputControls[i] = self.Child("/input/{}".format(i))
            for i in range(len(self.OUTPUT_TABLE or (None,))):
                self.OutputControls[i] = self.Child("/output/{}".format(i))
            self.CacheMaxVolume()

        def CacheMaxVolume(self):
            """
            算出每个方向流体格的**体积分母**：同方向里最大的那个体积。

            这是 minijei 的约定（`define.py::RenderInit`）—— 多流体产出时
            靠液面高低看出相对多少。高热流体离心机一次出 18/60/18/4 mB，
            不归一的话四格全是满的，那个「谁多谁少」就丢了。

            **只有一格时返回 None（画满）**：单流体格的分母就是它自己。

            在 `InitControls` 里算一次而不是每次回调算：绑定回调是**每帧**路径
            （`binding_cost.md`），而一条配方的体积不会变。
            """
            for outputs in (False, True):
                table = self.OUTPUT_TABLE if outputs else self.INPUT_TABLE
                amounts = []
                for kind, slot in (table or ()):
                    if kind != convert.CATEGORY_FLUID:
                        continue
                    entry = IngredientForCell(self.Recipe, slot, kind, outputs)
                    if entry is not None:
                        amounts.append(entry.get_amount() or 0)
                self.MaxVolume[outputs] = max(amounts) if len(amounts) > 1 else None

        @RecipeBinder.Group(input_prefixes)
        def InputPanelCallback(self, index):
            control = self.InputControls.get(index)
            if control is None or index >= len(self.INPUT_TABLE):
                return None
            kind, slot = self.INPUT_TABLE[index]
            # kind 显式传: 空格时没有 Stack 可问, 而"这个控件是流体槽"
            # 是本脚本的界面事实 —— 框架不该去猜
            return self.Normalize(render_slot(
                control, IngredientForCell(self.Recipe, slot, kind), kind=kind),
                False)

        @RecipeBinder.Group(output_prefixes)
        def OutputPanelCallback(self, index):
            control = self.OutputControls.get(index)
            if control is None:
                return None
            if not self.OUTPUT_TABLE:
                panel = render_slot(control, self.Recipe.GetPrimaryOutput(),
                                    kind=self.OUTPUT_KIND)
                lore = self.LoreFor("mei_ui.recipe.output")
                return panel.SetLore(lore) if lore else panel
            kind, slot = self.OUTPUT_TABLE[index]
            return self.Normalize(render_slot(
                control, IngredientForCell(self.Recipe, slot, kind, outputs=True),
                kind=kind), True)

        def Normalize(self, panel, outputs):  # type: (any, bool) -> any
            """
            给流体格设液面分母，返回原面板（接在 render_slot 后面写）。

            **鸭子探测而不是判 kind**：物品面板没有 `SetMaxVolume`，
            探不到就原样返回。这样第三方将来注册别的种类也不用改这里。
            """
            setter = getattr(panel, "SetMaxVolume", None)
            if setter is not None and self.MaxVolume.get(outputs):
                return setter(self.MaxVolume[outputs])
            return panel

    _UI_SCRIPTS[category_id] = MachineUIScript
    return MachineUIScript
