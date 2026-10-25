# coding=utf-8
"""
小型燃气发电机（`gas_burning_generator`）—— **唯一一台没有实体产物的机器**：
烧甲烷，只出 RF。

这台逼出了一处框架改动：`runtime._Convert` 原先见到「产物一个都解析不出」
就整条丢弃，而它的 outputs 里**本来就只有 `energy:0`**，
一条配方都留不下来 ⇒ 整台机器 0 条。现在的判据改成
「产物为空**且** `extra_outputs` 也为空」才算解析失败。

它在 MEI 里仍然查得到 —— 「按材料查用途」走的是**输入**侧，
玩家点甲烷照样能看到「能在燃气发电机里烧成电」。
只是反过来查不到（没有产物可查），那是对的。

布局照 minijei：流体格 → 火焰 → RF 两行数字，**不画产物格**。
minijei 在 `output_gas_id is None` 时显示一条「无废气」，
而实测唯一那条配方的副产气就是 `None` ⇒ 这条提示恒显示，
写死在布局里即可，不用 Python 去切可见性。
"""
from .._common import BuildMachine, GeneratorLabels
from ... import convert, exports

CATEGORY_ID = "skybluetech:gas_burning_generator"
RECIPE_CLS = "GasBurningGeneratorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiGasBurningGenerator.RECIPES_GRID"
INPUT_CELLS = 1
SORT_INDEX = 121

INPUT_KIND = convert.CATEGORY_FLUID
""" 输入格的条目种类。**写成模块常量而不是直接填参数**：
    离线探针 `probe_skyblue_machines.py` 靠读这些常量来比对
    「声明的格子」与「真实配方槽位」，填成字面量它就看不见 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.gas_burning_generator",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        # 气体的液面**从上往下**长，FluidPanel 按 IsGas 自己处理，这里只管种类
        input_kind=INPUT_KIND,
        # RF 两个数直推成可见文字（照 minijei），不用电力条
        labels=GeneratorLabels,
    )
