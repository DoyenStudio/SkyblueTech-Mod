# coding=utf-8
from ..define import id_enum
from .define import ItemQuest

INIT_REQUEST = ItemQuest(
    "skybluetech_start",
    "入门",
    "获取一个工作台",
    {"minecraft:crafting_table": 1},
).SetNextQuests(lambda: [GET_IRON_INGOT, GET_TIN_INGOT, GET_REDSTONEFLUX_CORE])

GET_IRON_INGOT = ItemQuest(
    "get_iron_ingot",
    "获取铁锭",
    "获取一些铁锭",
    {"minecraft:iron_ingot": 1},
).SetNextQuests(lambda: [GET_REFINED_IRON_INGOT])

GET_REFINED_IRON_INGOT = (
    ItemQuest(
        "get_refined_iron_ingot",
        "获取精炼铁锭",
        "通过高炉烧制铁锭得到精炼铁锭",
        {id_enum.Ingots.REFINED_IRON: 1},
    )
    .SetPrevQuests([GET_IRON_INGOT])
    .SetNextQuests(lambda: [MAKE_MACHINERY_WORKSTATION])
)

GET_TIN_INGOT = ItemQuest(
    "get_tin_ingot",
    "获取锡锭",
    "通过浅层采矿获取粗锡烧制成锡锭",
    {id_enum.Ingots.TIN: 1},
).SetNextQuests(lambda: [MAKE_MACHINERY_WORKSTATION, MAKE_MACHINERY_FRAME])

GET_REDSTONEFLUX_CORE = ItemQuest(
    "get_redstoneflux_core",
    "获取红石通量核心",
    "获取红石粉， 通过高炉熔炼红石粉得到红石通量核心",
    {id_enum.REDSTONEFLUX_CORE: 1},
).SetNextQuests(lambda: [MAKE_MACHINERY_FRAME])

MAKE_MACHINERY_FRAME = (
    ItemQuest(
        "make_machinery_frame",
        "制作机器框架",
        "通过工作台合成得到机械框架， 用于机器制造",
        {id_enum.MACHINERY_FRAME: 1},
    )
    .SetPrevQuests(lambda: [GET_IRON_INGOT, GET_TIN_INGOT, GET_REDSTONEFLUX_CORE])
    .SetNextQuests(lambda: [MAKE_MACHINERY_WORKSTATION])
)

MAKE_IRON_WRENCH = ItemQuest(
    "make_iron_wrench",
    "制作铁工具扳手",
    "通过工作台合成铁工具扳手， 用于机件加工",
    {id_enum.Wrench.IRON: 1},
).SetNextQuests(lambda: [MAKE_MACHINERY_WORKSTATION])

MAKE_IRON_PINCER = ItemQuest(
    "make_iron_pincer",
    "制作铁工具钳",
    "通过工作台合成铁工具钳， 用于机件加工",
    {id_enum.Pincer.IRON: 1},
).SetNextQuests(lambda: [MAKE_MACHINERY_WORKSTATION])

MAKE_MACHINERY_WORKSTATION = ItemQuest(
    "make_machinery_workstation",
    "制作机件加工台",
    "合成机件加工台， 用于制造各种机械",
    {id_enum.MACHINERY_WORKSTATION: 1},
)

MAKE_THERMAL_GENERATOR = (
    ItemQuest(
        "make_thermal_generator",
        "你的入门发电机",
        "使用机件加工台制造一个火力发电机",
        {id_enum.THERMAL_GENERATOR: 1},
    )
    .SetPrevQuests(
        lambda: [
            MAKE_MACHINERY_WORKSTATION,
            MAKE_MACHINERY_FRAME,
            MAKE_IRON_WRENCH,
            MAKE_IRON_PINCER,
        ]
    )
    .SetNextQuests(lambda: [])
)
