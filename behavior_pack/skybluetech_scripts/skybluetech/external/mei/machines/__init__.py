# coding=utf-8
"""
一台机器一个模块。加一台机器 = 加一个文件 + 在 MACHINES 里加一个名字。

清单显式列出而不是扫目录：扫目录会把半成品、备份文件也当成机器加载进去，
出问题时还得先猜"到底加载了哪些"。这条同 MEI 自己的 `extensions/__init__.py`。

**一台机器一个包**（`macerator/__init__.py`），编排同 MEI 内置扩展的
`extensions/vanilla/<type>/`：门面在 `__init__.py`，界面自成一路的再加 `ui_script.py`。

**但每个包导出的是 `Build()` 而不是 `CATEGORY` / `SOURCE` / `UI_SCRIPT`。**
这是与 MEI 内置扩展形状上的唯一差别，原因是硬的：
内置扩展能在模块级 `from MEIScripts.api.facades.types import RecipeCategory`，
而第三方写不出这一行 —— 类型是运行期从组件上取到的对象，
`RecipeCategory(...)` 与 `class X(RecipeUIScript)` 都只能发生在函数里。
"""

MACHINES = (
    # 纯物品
    "macerator",
    "compressor",
    "alloy_furnace",
    "metal_hammer",
    "machinery_workstation",
    "hydroponic_bed",
    "hydroponic_bed_sand",
    "template_assembler",
    # 单流体（物 <-> 流）
    "oil_extractor",
    "magma_furnace",
    "fluid_condenser",
    "freezer",
    # 混合输入（流 + 物）
    "metal_press",
    "mixer",
    # 多流体产出
    "magma_centrifuge",
    # 无电
    "distillation_chamber",
    "industrial_researching",
    # 产电
    "redstone_generator",
    "gas_burning_generator",
    "reacting_thermal_generator",
)
"""
已接入 MEI 的机器，**按想要的 tab 顺序排**（各模块自己的 sort_index 才是最终判据）。
上面的分组注释按**形状**分，不按游戏里的机器分类 ——
新接一台时先看它落在哪一组，那一组里随便挑一台照抄就行。

**带标准 `inputs`/`outputs` 结构的 20 台全部接完**（2026-09-04）。
⥠ 但**不等于蔚蓝的合成方式都在这了**：另有三处数据形状不同的没接
（发酵池的 `FermenterRecipe`、热力发电机的 `FUEL_TICK_MAP` 224 项燃料、
地热发电机的四个硬编码常量），作者裁定暂不做，见 §7.13。
⥠ 第 21 台 `cyro_heat_melting_chamber` **不在待办里**：
蔚蓝自己就没启用它（`machinery_def/` 下只有 `.pyi` 存根，无 `.py`）。

逐台的形状、坑、典型配方，见 MEI 的
docs/thirdparty/skybluetech.md **§7.11 / §7.12 / §7.13**。
"""
_PACKAGE = "skybluetech_scripts.skybluetech.external.mei.machines."


def Import(name):  # type: (str) -> any
    """ 惰性导入一台机器的模块；失败返回 None（一台机器坏了不该带走其余的）"""
    from .. import bridge
    try:
        return __import__(_PACKAGE + name, {}, {}, ["Build"])
    except Exception as e:  # noqa
        bridge.Error("机器模块 {} 导入失败: {}".format(name, bridge.ErrorText(e)))
        return None
