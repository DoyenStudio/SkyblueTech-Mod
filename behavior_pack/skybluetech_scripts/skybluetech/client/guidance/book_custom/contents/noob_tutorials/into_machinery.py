# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
    CheckUsage,
    PushRecipeCheckerUI,
)
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)


def jump_machinery_workstation():
    from ..machinery.machinery_crafting import machinery_workstation

    machinery_workstation.FastJump()


def check_hammer_recipes():
    from skybluetech_scripts.skybluetech.common.tools_def.metal_hammer import recipes

    PushRecipeCheckerUI(recipes)


into_machinery = PageGroup(
    "into_machinery",
    [
        TextPage(
            "第一台机器",
            '将<item id="minecraft:iron_ingot">铁锭放进<item id="minecraft:blast_furnace"><text color="§9" t="高炉">可以烧制成<item id="{refined_iron_ingot}">精炼铁锭， 进而制作<item id="{machinery_workstation}"><link id="machinery_workstation" text="机件加工台">和<item id="{metal_hammer}"><link id="metal_hammer" text="金属锤">。 机件加工台能合成绝大多数你需要的机器。\n\n打开机件加工台界面， 点击<img path="textures/ui/searcher">按钮就可以看到机件加工台可以合成的所有配方。\n\n关于机件加工台的使用， <link id="lookup" text="看这里">。'.format(
                refined_iron_ingot=id_enum.Ingots.REFINED_IRON,
                machinery_workstation=id_enum.MACHINERY_WORKSTATION,
                metal_hammer=id_enum.METAL_HAMMER,
            ),
            hyperlink_cbs={
                "refined_iron_ingot": lambda _: CheckRecipe(
                    id_enum.Ingots.REFINED_IRON
                ),
                "machinery_workstation": lambda _: CheckRecipe(
                    id_enum.MACHINERY_WORKSTATION
                ),
                "metal_hammer": lambda _: CheckRecipe(id_enum.METAL_HAMMER),
                "lookup": lambda _: jump_machinery_workstation(),
            },
        ),
        TextPage(
            "",
            '把金属锭丢到地上， 手持金属锤尝试挖掘金属锭掉落物下方的方块， 就可以将金属锭<link id="hammer" text="锤成">金属板； 日后你可以用<item id="{compressor}"><link id="compressor" text="压缩机">压缩机代替金属锤， 它支持把更多之类的锭压成板。\n\n将<item id="minecraft:redstone"><text color="§c" t="红石">放进高炉可以烧制成<item id="{redstoneflux_core}"><text color="§c" t="红石通量核心">来参与机器的合成。'.format(
                compressor=id_enum.COMPRESSOR,
                redstoneflux_core=id_enum.REDSTONEFLUX_CORE,
            ),
            hyperlink_cbs={
                "hammer": lambda _: check_hammer_recipes(),
                "compressor": lambda _: CheckRecipe(id_enum.COMPRESSOR),
            },
        ),
        TextPage(
            "",
            '要致富， 先<text color="§9" t="发电">！ <item id="{thermal_generator}">火力发电机将会是你的第一台发电机， 它通过燃烧燃料发电， 燃料和熔炉使用的燃料一致<text color="§4" t="（但不能是熔岩桶）">。\n\n为了尽可能充分利用矿物， 你的当务之急是做出一台<item id="{macerator}">磨粉机， 它能把一份<item id="{raw_tin}">粗矿磨成两份<item id="{tin_dust}">矿粉， 矿粉在熔炉可以熔炼为对应的金属锭， 实现双倍产出。'.format(
                thermal_generator=id_enum.THERMAL_GENERATOR,
                macerator=id_enum.MACERATOR,
                raw_tin=id_enum.RawOres.TIN,
                tin_dust=id_enum.Dusts.TIN,
            ),
        ),
        MachineryWorkstationRecipePage(
            id_enum.THERMAL_GENERATOR,
            extra_text="把火力发电机和磨粉机紧邻放置， 火力发电机就能直接向磨粉机供电。\n\n在下一页可以查看磨粉机的合成方式！",
        ),
        MachineryWorkstationRecipePage(id_enum.MACERATOR),
    ],
)
