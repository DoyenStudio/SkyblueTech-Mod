# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ..define import (
    TextPage,
    PageGroup,
)


def on_open_minijei(_):
    from skybluetech_scripts.skybluetech.client.ui.recipe_checker.minijei_items_page import (
        MiniJEIItemListUI,
    )

    MiniJEIItemListUI.PushUI()


mini_jei_desc = PageGroup(
    "mini_jei_intro",
    [
        TextPage(
            "内置配方表",
            '为了方便游戏内查询《蔚蓝科技》的相关配方， 模组内置了配方查看器， 称为 <text color="§2" t="“Mini JEI”">。 \n\n在机器的操作界面通常都会有一个<img path="textures/ui/skybluetech/searcher">按钮， 点击后可以看到这台机器可以参与制作的所有配方。\n\n<style color="§d"><link id="mini_jei" text="[点我打开 MiniJEI]">',
            hyperlink_cbs={
                "mini_jei": on_open_minijei,
            },
        ),
        TextPage(
            "",
            '<text color="§2" t="点击">配方表中的原料可以查看<text color="§1" t="物品的获取方式">和<text color="§3" t="物品的用途">， 还可以把物品添加到左侧的<text color="§g" t="收藏夹">。\n\n点击<img path="textures/ui/skybluetech/back_button">按钮可以返回上层配方。\n点击[ \\< ] 或 [ \\> ] 按钮可以查看上一页 / 下一页配方。',
        ),
    ],
)
