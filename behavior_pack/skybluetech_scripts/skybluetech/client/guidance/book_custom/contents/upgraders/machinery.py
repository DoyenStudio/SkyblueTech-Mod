# coding=utf-8
# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipes
from ...define import (
    TextPage,
    PageGroup,
)

upgraders_machinery = PageGroup(
    "upgraders_machinery",
    [
        TextPage(
            "机器升级模块",
            '在机器的<text color="§6" t="右上角">可以安装<item id="{upgrader}">升级模块， 只需要把升级模块放入带<img path="textures/ui/skybluetech/slot_upgrader_bg">图标的槽位里就可以直接生效了， 多余的升级模块会直接弹出为掉落物。\n\n目前一个机器对于每种类型的升级模块<text color="§c" t="最多只能接受一个">， 至多接受 4 个升级模块。'.format(
                upgrader=id_enum.Upgraders.EMPTY
            ),
        ),
        TextPage(
            "",
            '<link id="onclick" text="点击此处">可以查看所有可用的升级模块（带 WIP 名的除外）。',
            hyperlink_cbs={
                "onclick": lambda _: CheckRecipes(list(id_enum.Upgraders.all()))
            },
        ),
    ],
)
