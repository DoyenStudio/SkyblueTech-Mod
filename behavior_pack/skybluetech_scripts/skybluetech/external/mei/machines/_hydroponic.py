# coding=utf-8
"""
两种水培床共用的部分。

配方形状一样（种子 → 收获），但**产出语义不同**。判据取自服务端 `finish_once`，
不是界面 —— minijei 那边两种床用的是同一套渲染，看不出差别：

  · 土培 `hydroponic_bed`：`OutputItem(种子, rand_seed_count()-1)` **加** 各收获物
    —— 种子会返还，只是数量随机且经常是 0；
  · 沙培 `hydroponic_bed_sand`：只有 `harvest_outputs`，**不返还种子**。

⚠ 土培的返还数量是 `概率表下标 - 1`：下标 0 那档算作 -1（等于没有），
所以「返还 0 粒」的概率是前两档之和。照抄下标当数量会整体错位一格。

⚠ 种子与收获相同时（胡萝卜、土豆）`harvest_outputs` 是**空表** ——
土培靠返还的种子撑起产物，沙培那种配方则真的零产物，会被整条丢掉。
"""
from .. import bridge, convert
from ._common import BuildBase
from . import _layouts


def MakeDecorate(return_seed, power_cost=0):  # type: (bool, int) -> any
    """
    造 decorate 钩子；`return_seed` 取自服务端语义，见模块头。

    `power_cost` 要从外面传是因为它**不在配方对象上** ——
    见 `Decorate` 里那段说明。
    """

    def _decorate(sb_recipe, parts):  # type: (any, dict) -> None
        Decorate(sb_recipe, parts, return_seed, power_cost)

    return _decorate


def Decorate(sb_recipe, parts, return_seed, power_cost=0):
    # type: (any, dict, bool, int) -> None
    """ 按机型补产物，并把生长参数与电力塞进 Data """
    seed_id = getattr(sb_recipe, "seed_item", None)
    if not seed_id:
        return

    if return_seed:
        # 种子排在最前: 它是"顺带还给你的", 收获物才是目的
        stacks = bridge.Registry.ItemFactory.GetStacksFromIds([seed_id])
        if stacks:
            parts["outputs"].insert(0, bridge.Types.Ingredient(stacks, 1))
            # 槽位键带类别前缀 —— 与 convert 里的形式必须一致,
            # 否则界面反查时 "0" 与 "item:0" 对不上
            parts["output_slots"].insert(0, convert.slot_key(convert.CATEGORY_ITEM, 0))

    data = parts["data"]
    data["crop_block_id"] = getattr(sb_recipe, "crop_block_id", "") or ""
    stages = int(getattr(sb_recipe, "stages", 0) or 0)
    if stages:
        data["crop_stages"] = stages

    # 电力与耗时都要在这里补。
    #
    # ⚠ **水培床的电力不在配方对象上** —— `HydroponicBedRecipe.__init__`
    # 给 `MachineRecipe` 传的 power_cost / tick_duration 都是 **0**，
    # 真正的值是 `machinery_def/hydroponic_bed.py` 里的**模块级常量**
    # `POWER_COST = 4`（每 tick）。
    # 只看配方对象会把它误判成「无电」。
    # ⇒ **判断一台机器吃不吃电，要同时看配方对象与 machinery_def 的模块常量。**
    if power_cost > 0:
        data["power_cost"] = power_cost
        # 一次收成的总时长 = 每阶段刻数 × 阶段数。
        # 它同时是进度条的周期（`_common.PeriodOf`）与总耗电的乘数
        ticks = int(getattr(sb_recipe, "grow_stage_ticks", 0) or 0) * stages
        if ticks > 0:
            data["tick_duration"] = ticks
    probs = getattr(sb_recipe, "seed_output_probs", None)
    if probs and return_seed:
        # 服务端是 rand_seed_count() - 1, 所以**下标 i 对应数量 i-1**,
        # 下标 0 那档算作 -1(等于没有) -> 与下标 1 合并进"0 粒"
        merged = {}
        for index, prob in enumerate(probs):
            count = max(0, index - 1)
            merged[count] = merged.get(count, 0.0) + float(prob)
        counts = sorted(merged.keys())
        # 两张平行 list 而不是 dict: Data 会被序列化, 键类型跨边界不可靠
        data["seed_counts"] = counts
        data["seed_probs"] = [merged[c] for c in counts]


def _Percent(prob):  # type: (float) -> str
    """ 0.45 -> "45.0%"; 0.398 -> "39.8%"。**一位小数 + 百分号** """
    return "%.1f%%" % (prob * 100.0)


def SeedLore(recipe):  # type: (any) -> str or None
    """
    种子格的说明：返还几粒种子的概率

    走 lore 而不是界面文字 —— 三四行概率在配方行里摆不下，
    而它本来就是「这一格会给你什么」的补充说明。
    """
    data = getattr(recipe, "Data", None) or {}
    probs = data.get("seed_probs")
    counts = data.get("seed_counts")
    if not probs or not counts:
        return None
    lines = []
    for count, prob in zip(counts, probs):
        if prob <= 0:
            continue
        lines.append("§7返还 {} 粒: §f{}".format(count, _Percent(prob)))
    if not lines:
        return None
    return "\n".join(lines)


def BuildUIScript(category_id, animated):  # type: (str, bool) -> type
    """
    造水培床的配方页脚本。

    `animated` 为真时按生长阶段轮播作物模型（土培有 stages，沙培没有）。
    参数从各自的 `__init__.py` 传进来，两边都不反向 import。
    """
    RecipeBinder = bridge.UI.Binding.RecipeBinder
    render_slot = bridge.UI.Slots.render_slot

    OUTPUT_CELLS = 3
    """ 产物格数。种子 + 最多两样收获 —— 现有配方最多就这么多 """

    output_prefixes = ["mei_ui.recipe.output%d" % i for i in range(OUTPUT_CELLS)]

    class HydroponicUIScript(BuildBase()):
        """
        种子 → 作物模型 → 产物。布局见 ui/mei_recipes/Hydroponic.json（由生成器的 `emit_hydroponic` 输出）

        **继承 `BuildBase()`** 而不是裸的 `RecipeUIScript`：水培床也吃电
        （`POWER_COST = 4`/tick，在 machinery_def 的模块常量里），
        基类把进度条、电力条、内容根解析都包了。
        """

        TYPE = category_id
        ANIMATED = animated
        LAYOUT = _layouts.HAND.get("hydroponic")
        """ 新版控件（与其他机器的配方页一致）：能量条、进度、两个悬停走基类的 `LAYOUT` 那一套，
            值由生成器写进 `_layouts.HAND`，与 JSON 同一次生成 """

        CROP_PATH = "/shell/crop"
        """ 作物模型控件的路径，**相对内容根**（`self.Child`）。
            它嵌在 shell(床的贴图)里面 —— 布局挪了位置就要同步改这里，
            找不到会在日志里报出来 """

        STAGE_TICKS = 6
        """ 每多少拍换一个生长阶段。节拍 0.2 秒 ⇒ 6 拍 = 1.2 秒一阶段 """

        def __init__(self, recipe):
            BuildBase().__init__(self, recipe)
            self.SeedControl = None
            self.OutputControls = {}
            self.CropDoll = None
            self.CropStages = 0
            self.LastStage = -1

        def InitControls(self):
            self.SeedControl = self.Child("/seed/0")
            for i in range(OUTPUT_CELLS):
                self.OutputControls[i] = self.Child("/outputs/{}".format(i))

            data = getattr(self.Recipe, "Data", None) or {}
            self.CropStages = int(data.get("crop_stages") or 0)
            crop = self.Child(self.CROP_PATH)
            if crop is None:
                # **不要静默** —— 这条路径与 layout 是硬耦合的(§2.7-2 记的那类债),
                # 布局一嵌套就断, 而"少一个模型"在界面上看不出是报错还是本来就没有。
                # 实机: shell 把 crop 包进去之后模型消失
                bridge.Error("找不到作物模型控件 {} —— 布局改过?".format(self.CROP_PATH))
            self.CropDoll = crop.asNeteasePaperDoll() if crop else None
            self.RenderCrop(0)

        # 作物模型
    # ==================================================================================================================
        def RenderCrop(self, stage):  # type: (int) -> None
            """
            把作物方块渲染成 3D 模型。**失败就算了** —— 少一个预览远好过整页崩

            `RenderBlockGeometryModel` **收一个 dict**，不是关键字参数：
            minijei 那边看着像关键字，那是 ToolDelta 的包装器
            （`engineering.md` §5.1b 记的同一类坑）。
            """
            if self.CropDoll is None:
                return
            data = getattr(self.Recipe, "Data", None) or {}
            block_id = data.get("crop_block_id")
            if not block_id:
                return
            try:
                from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
                # 单方块调色板：生长阶段就是方块的 aux
                palette = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
                palette.DeserializeBlockPalette({
                    "extra": {},
                    "void": False,
                    "actor": {},
                    "volume": (1, 1, 1),
                    "common": {(block_id, stage): [0]},
                    "eliminateAir": True,
                })
                geo = CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
                    palette, "geometry.mei_crop." + block_id.replace(":", "_"))
                self.CropDoll.RenderBlockGeometryModel({
                    "block_geometry_model_name": geo,
                    "scale": 4.6,
                    "init_rot_x": -90,
                    "init_rot_y": 0,
                    "init_rot_z": 90,
                    "rotation_axis": (0, 1, 0),
                })
                self.LastStage = stage
            except Exception as e:  # noqa
                bridge.Error("作物模型渲染失败 {}: {}".format(block_id, bridge.ErrorText(e)))
                self.CropDoll = None      # 别每拍再试一次

        def OnAnimTick(self, ticks):
            """
            先让基类推进度条与电力条，再推作物。

            生长阶段**与进度条同周期**：一条进度走完正好长熟一轮。
            两者各走各的话，进度条满了作物却才长一半，看着就是两件事。
            拿不到周期（无耗时数据）时回退到固定节拍。
            """
            BuildBase().OnAnimTick(self, ticks)
            if not self.ANIMATED or self.CropStages <= 1 or self.CropDoll is None:
                return
            if self.ProgressPeriod:
                progress = float(ticks % self.ProgressPeriod) / self.ProgressPeriod
                stage = min(self.CropStages - 1, int(progress * self.CropStages))
            else:
                stage = (ticks // self.STAGE_TICKS) % self.CropStages
            if stage != self.LastStage:
                self.RenderCrop(stage)

        # 槽位
    # ==================================================================================================================
        @RecipeBinder.Group(["mei_ui.recipe.input"])
        def SeedPanelCallback(self, index):
            _ = index
            inputs = self.Recipe.GetInputs()
            panel = render_slot(self.SeedControl, inputs[0] if inputs else None)
            return panel.SetLore(SeedLore(self.Recipe))

        @RecipeBinder.Group(output_prefixes)
        def OutputPanelCallback(self, index):
            control = self.OutputControls.get(index)
            if control is None:
                return None
            outputs = self.Recipe.GetOutputs()
            return render_slot(control, outputs[index] if index < len(outputs) else None)

        # OnCreate / OnDestroy 交给基类 —— 它还要做 ResolveContent /
        # InitProgress / InitPower，自己覆写会把那三样漏掉

    return HydroponicUIScript
