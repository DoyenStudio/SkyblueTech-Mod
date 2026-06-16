# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)
from . import machinery, objects

upgraders_toc = PageGroup(
    "upgraders_toc",
    [
        TextPage(
            "升级模块",
            "升级模块分为机器升级和道具升级。\n\n机器升级可以使机械设备具有更好的性能， 而道具升级可以为工具、 护甲和武器提供额外的功能或强化。",
        ),
        TOCPage([
            TOCPageSection(
                id_enum.Upgraders.BASIC_SPEED_UPGRADER,
                0,
                "机器升级",
                machinery.upgraders_machinery,
            ),
            TOCPageSection(
                id_enum.ObjectUpgraders.ATTACK, 0, "道具升级", objects.upgraders_objects
            ),
        ]),
    ],
)
