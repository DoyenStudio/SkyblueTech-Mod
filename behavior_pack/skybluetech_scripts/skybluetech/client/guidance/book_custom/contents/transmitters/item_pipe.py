# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    PageGroup,
)


item_pipe_entry = PageGroup(
    "item_pipe_entry",
    [
        TextPage(
            "物品管道",
            "物品管道可以代替漏斗运送物品， 支持原版的大部分容器和《蔚蓝科技》里的机器设备。\n\n不同物品管道的区别只在于其运送物品的速度。",
        ),
        TextPage(
            "配方查询",
            '<item id="{steel}"><link id="steel" text="钢制物品管道">'.format(
                steel=id_enum.ItemPipe.STEEL
            ),
            hyperlink_cbs={"steel": lambda _: CheckRecipe(id_enum.ItemPipe.STEEL)},
        ),
    ],
)
