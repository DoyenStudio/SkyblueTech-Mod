# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipes
from ...define import (
    TextPage,
    PageGroup,
)

upgraders_objects = PageGroup(
    "upgraders_objects",
    [
        TextPage(
            "道具升级模块",
            '你可以在<item id="{assembler}"><link id="assembler" text="装配台">内为你的道具（充能工具， 武器， 护甲等）安装道具升级模块， 升级模块可以<text color="§c" t="强化它们的属性">， 或者<text color="§9" t="添加额外功能">。'.format(
                assembler=id_enum.Machinery.ASSEMBLER
            ),
        ),
        TextPage(
            "",
            '<link id="onclick" text="点击此处">可以查看所有可用的升级模块（带 WIP 名的除外）。',
            hyperlink_cbs={
                "onclick": lambda _: CheckRecipes(list(id_enum.ObjectUpgraders.all()))
            },
        ),
    ],
)
