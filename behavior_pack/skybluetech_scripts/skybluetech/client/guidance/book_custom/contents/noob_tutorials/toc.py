# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

from . import day_one, into_machinery

noob_tutorial_toc = PageGroup(
    "noob_tutorials",
    [
        TOCPage(
            [
                TOCPageSection("minecraft:wooden_axe", 0, "第一天", day_one.day_one),
                TOCPageSection(
                    id_enum.MACHINERY_WORKSTATION,
                    0,
                    "第一台机器",
                    into_machinery.into_machinery,
                ),
            ],
        ),
    ],
)
