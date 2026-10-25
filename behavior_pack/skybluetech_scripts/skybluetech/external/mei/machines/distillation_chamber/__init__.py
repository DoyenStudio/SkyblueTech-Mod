# coding=utf-8
"""
小型蒸馏仓（`distillation_chamber`）—— **唯一一台既不吃电也没有耗时的机器**。

`power_cost` 与 `tick_duration` 都是 **0**：它不是「按时长跑一轮」的机器，
而是「维持在某个温度区间就持续反应」。所以布局里
**没有电力那一列，也没有进度条** —— 后者是照 minijei 改的：
它的 `distillation_chamber_recipes` 里压根没有 `progress` 控件。
（上一轮我硬塞了一根静止的箭头，那是照数据推出来的多余物。）

编排照 minijei：**两条横向流体条上下叠**（产物在上、原料在下）+
右侧一块 66×52 的温度板，三行字分别是标题 / 最适温度 / 温度区间。
温度是**可见文字不是 hover** —— 读这条配方必须看到的数就该直接写出来。

典型配方：**50 mB 水 → 45 mB 蒸馏水**，最适 353 K，区间 303~373 K。
另两条是**石油 → 润滑油**（323~333 K）与**植物油 → 润滑油**（328~343 K）
—— 同一个产物、两条不同温度带的路子，正好验温度确实是逐条不同的。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:distillation_chamber"
RECIPE_CLS = "DistillationChamberRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiDistillationChamber.RECIPES_GRID"
SORT_INDEX = 117

INPUT_KIND = convert.CATEGORY_FLUID
""" 输入格的条目种类。**写成模块常量而不是直接填参数**：
    离线探针 `probe_skyblue_machines.py` 靠读这些常量来比对
    「声明的格子」与「真实配方槽位」，填成字面量它就看不见 """

TEMPERATURE_FIELDS = ("min_temperature", "max_temperature", "fit_temperature")
""" 要搬进 `Recipe.Data` 的温度字段。**全是标量** ——
    Data 会随配方序列化出去，而引擎的事件与存盘都不收 Python 对象 """

KELVIN = "K"
""" 蔚蓝的温度单位就是开尔文（303 ≈ 30 ℃），照抄不换算 —— minijei 的
    `FormatKelvin` 也是直接加单位 """


def Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """ 把温度搬进 Data。它们在配方对象的属性上，不在 inputs/outputs 里 """
    data = parts["data"]
    for name in TEMPERATURE_FIELDS:
        value = getattr(sb_recipe, name, None)
        if value is not None:
            data[name] = int(value)


def Labels(recipe):  # type: (any) -> dict
    """
    温度板那两行数，路径对应布局里的 `board/tip_text` 与 `board/tip_text2`。

    分工照 minijei（`DistillationChamberRecipeRenderer`）：
    大字写**最适温度**，小字写**区间**。板上第一行"最适产出温度"是静态标题，
    写死在布局里，不用推。
    """
    data = getattr(recipe, "Data", None) or {}
    fit = data.get("fit_temperature")
    low, high = data.get("min_temperature"), data.get("max_temperature")
    texts = {}
    if fit is not None:
        texts["/board/tip_text"] = "%d %s" % (int(fit), KELVIN)
    if low is not None and high is not None:
        texts["/board/tip_text2"] = "%d %s ~ %d %s" % (
            int(low), KELVIN, int(high), KELVIN)
    return texts


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.distillation_chamber",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=Decorate,
        input_kind=INPUT_KIND,
        output_kind=convert.CATEGORY_FLUID,
        # 形状就是「一进一出」，通用脚本够用 —— 上一轮那份自写脚本
        # 存在的唯一理由是把温度挂 hover，现在温度改成可见 label 就不需要了
        labels=Labels,
    )
