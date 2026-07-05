# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
    CheckRecipes,
)
from ...define import (
    TextPage,
    PageGroup,
)


def jump_to_mini_miner(_):
    from ..machinery.machinery_source_extraction import mini_miner

    mini_miner.FastJump()


def jump_to_oil_extractor(_):
    from ..machinery.machinery_production import oil_extractor

    oil_extractor.FastJump()


def jump_to_distillation_chamber(_):
    from ..machinery.machinery_production import distillation_chamber

    distillation_chamber.FastJump()


mining_auto = PageGroup(
    "mining_auto",
    [
        TextPage(
            "采矿自由",
            '现在你已经得到了稳定的电力产出， 但是下矿仍然是一件苦差事。\n一个<item id="{mini_miner}"><link id="mini_miner" text="迷你采矿机">可以帮你解决所有麻烦！\n\n迷你采矿机只需要能量和润滑油就可以开始采矿。 还记得上一章里你种了很多作物吗？你可以拿多余的小麦种子放进<item id="{oil_extractor}"><link id="oil_extractor" text="榨油机">榨出植物油，'.format(
                mini_miner=id_enum.Machinery.MINI_MINER,
                oil_extractor=id_enum.Machinery.OIL_EXTRACTOR,
            ),
            hyperlink_cbs={
                "mini_miner": jump_to_mini_miner,
                "oil_extractor": jump_to_oil_extractor,
            },
        ),
        TextPage(
            "",
            '然后再将植物油送进<item id="{distillation_chamber}"><link id="distillation_chamber" text="小型蒸馏仓">， 就可以将植物油转换为润滑油供迷你采矿机使用了！'.format(
                distillation_chamber=id_enum.Machinery.DISTILLATION_CHAMBER,
            ),
            hyperlink_cbs={
                "distillation_chamber": jump_to_distillation_chamber,
            },
        ),
    ],
)
