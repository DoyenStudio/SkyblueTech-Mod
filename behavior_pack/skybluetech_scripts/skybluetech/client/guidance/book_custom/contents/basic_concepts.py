# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MainTOCPage,
    MainTOCPageSection,
    PageGroup,
)

from . import intros


basic_concepts_toc = PageGroup([
    TextPage(
        "basic_concepts_desc",
        "基础概念",
        "本章将介绍有关《蔚蓝科技》的基本概念，便于您理解本模组的专有名词和玩法机制等内容。",
    ),
    MainTOCPage(
        "basic_concepts_toc",
        [
            MainTOCPageSection(
                id_enum.Batteries.JUNIOR, 0, "能源", intros.energy_intro
            ),
            MainTOCPageSection("minecraft:water_bucket", 0, "流体", intros.fluid_intro),
        ],
    ),
])
