# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    PageGroup,
)

famicom = PageGroup(
    "famicom",
    [
        TextPage(
            "红白机音乐",
            '在休息时听听音乐也不错， 制作一个<item id="{famicom}"><style color="§c"><link id="famicom" text="红白机"><style color="R">听听音乐吧。 （你别管你是怎么学习到这玩意的制作方法的！）'.format(
                famicom=id_enum.FAMICOM,
            ),
            hyperlink_cbs={"famicom": lambda _: CheckRecipe(id_enum.FAMICOM)},
        ),
        TextPage(
            "",
            '如果运气好， 你可以在地牢内找到四种<item id="{cartridge}"><text color="§a" t="音乐卡带">中的一个或多个， 可以直接将其插入红白机播放卡带内的音乐。'.format(
                cartridge=id_enum.FamicomCartidges.YELLOW,
            ),
            hyperlink_cbs={
                "cartridge": lambda _: CheckRecipe(id_enum.FamicomCartidges.YELLOW)
            },
        ),
    ],
)
