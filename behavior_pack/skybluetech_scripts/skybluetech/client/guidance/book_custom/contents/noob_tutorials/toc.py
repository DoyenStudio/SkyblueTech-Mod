# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

from . import (
    better_life,
    day_one,
    into_machinery,
    metal_and_tools,
    page_todo,
    mining_auto,
)

noob_tutorial_toc = PageGroup(
    "noob_tutorials",
    [
        TOCPage(
            [
                TOCPageSection("minecraft:wooden_axe", 0, "第一天", day_one.day_one),
                TOCPageSection(
                    id_enum.Machinery.MACHINERY_WORKSTATION,
                    0,
                    "第一台机器",
                    into_machinery.into_machinery,
                ),
                TOCPageSection(
                    id_enum.Machinery.ALLOY_FURNACE,
                    0,
                    "合金和工具",
                    metal_and_tools.metal_and_tools,
                ),
                TOCPageSection(
                    id_enum.SkyblueTools.PICKAXE,
                    0,
                    "步入小康",
                    better_life.better_life,
                ),
                TOCPageSection(
                    id_enum.Machinery.MINI_MINER,
                    0,
                    "采矿自由",
                    mining_auto.mining_auto,
                ),
                TOCPageSection("minecraft:barrier", 0, "未完待续", page_todo.page_todo),
            ],
        ),
    ],
)
