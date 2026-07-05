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


def jump_to_assembler(_):
    from ..machinery.machinery_crafting import assembler

    assembler.FastJump()


def jump_to_farming_station(_):
    from ..machinery.machinery_source_extraction import farming_station

    farming_station.FastJump()


def jump_tp_forester(_):
    from ..machinery.machinery_source_extraction import forester

    forester.FastJump()


better_life = PageGroup(
    "better_life",
    [
        TextPage(
            "步入小康",
            '还在担心粮食和原木紧缺的问题吗？没关系， <item id="{farming_station}"><link id="farming_station" text="种植站">和<item id="{forester}"><link id="forester" text="伐木机">能帮你解决这些问题！ 它们只需要几台太阳能就可以持续工作了。\n\n种植站和伐木机会把产物存放到机器内供收取。 收取木头可以帮助你进行规模化的火力发电， 作物则可以让你告别饥饿。'.format(
                farming_station=id_enum.Machinery.FARMING_STATION,
                forester=id_enum.Machinery.FORESTER,
            ),
            hyperlink_cbs={
                "farming_station": jump_to_farming_station,
                "forester": jump_tp_forester,
            },
        ),
        TextPage(
            "",
            '工具耐久经常耗尽？做一套《蔚蓝科技》系列的工具吧！<item id="{axe}"><item id="{pickaxe}"><item id="{shovel}"><item id="{hoe}"><item id="{sword}"><style color="§9">蔚蓝系列的<link id="tools" text="工具"><style color="R">只需要消耗充能即可修复工具。\n\n你可以在<item id="{charger}"><link id="charger" text="充能台">为工具补充能量， 或者随身携带<item id="{battery}"><link id="battery" text="电池">为工具充能。'.format(
                axe=id_enum.SkyblueTools.AXE,
                pickaxe=id_enum.SkyblueTools.PICKAXE,
                shovel=id_enum.SkyblueTools.SHOVEL,
                hoe=id_enum.SkyblueTools.HOE,
                sword=id_enum.SkyblueTools.SWORD,
                charger=id_enum.Machinery.CHARGER,
                battery=id_enum.Batteries.JUNIOR,
            ),
            hyperlink_cbs={
                "tools": lambda _: CheckRecipes([
                    id_enum.SkyblueTools.AXE,
                    id_enum.SkyblueTools.PICKAXE,
                    id_enum.SkyblueTools.SHOVEL,
                    id_enum.SkyblueTools.HOE,
                    id_enum.SkyblueTools.SWORD,
                ]),
                "charger": lambda _: CheckRecipe(id_enum.Machinery.CHARGER),
                "battery": lambda _: CheckRecipe(id_enum.Batteries.JUNIOR),
            },
        ),
        TextPage(
            "",
            '在《蔚蓝科技》接下来的更新中会逐步开放工具的升级模块的合成方式和使用方法， 当然你也可以在<text color="§5" t="创造物品栏">拿出工具升级使用<item id="{assembler}"><link id="assembler" text="装配站">抢先体验。'.format(
                assembler=id_enum.Machinery.ASSEMBLER,
            ),
            hyperlink_cbs={
                "assembler": jump_to_assembler,
            },
        ),
    ],
)
