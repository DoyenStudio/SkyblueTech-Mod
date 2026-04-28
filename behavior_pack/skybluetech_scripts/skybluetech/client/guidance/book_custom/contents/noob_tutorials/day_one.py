# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
    CheckUsage,
)
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

day_one = PageGroup(
    "day_one",
    [
        TextPage(
            "第一天",
            '和《我的世界》中正常的第一天一样， 你仍然需要砍树、 挖矿、 建造基地！ 只不过在砍树时， <text color="§c" t="记得保留几棵橡树">， 在其树干的侧面摆上<item id="{resin_collector}"><link id="a" text="树脂采集斗">， 它们可以在你做其它事时帮你收集<item id="{resin}"><link id="b" text="生树脂">， 在之后你可能需要大量的生树脂。\n\n<item id="minecraft:light_block" aux=15>小提示： <text color="§2" t="点击">带<link id="test" text="下划线">的文本可以跳转到对应的超链接哦。'.format(
                resin_collector=id_enum.RESIN_COLLECTOR, resin=id_enum.RESIN
            ),
            hyperlink_cbs={
                "a": lambda _: CheckRecipe(id_enum.RESIN_COLLECTOR),
                "b": lambda _: CheckUsage(id_enum.RESIN),
                "test": lambda _: None,
            },
        ),
        TextPage(
            "",
            '在地下可以挖到<item id="{tin_ore}"><link id="tin_ore" text="锡矿石">、 <item id="{lead_ore}"><link id="lead_ore" text="铅矿石">、 <item id="{nickel_ore}"><link id="nickel_ore" text="镍矿石">、 <item id="{silver_ore}"><link id="silver_ore" text="银矿石">和<item id="{platinum_ore}"><link id="platinum_ore" text="铂矿石">， 把挖掘矿物所得的粗矿送入熔炉进行熔炼得到金属锭， 它们将大量参与机械等配方的合成。\n\n<item id="minecraft:copper_ingot"><text color="§6" t="铜">和<item id="minecraft:redstone"><text color="§c" t="红石">也是你日后会大量使用的工业必需品， 尽量多收集些吧。'.format(
                tin_ore=id_enum.Ore.TIN,
                lead_ore=id_enum.Ore.LEAD,
                nickel_ore=id_enum.Ore.NICKEL,
                silver_ore=id_enum.Ore.SILVER,
                platinum_ore=id_enum.Ore.PLATINUM,
            ),
            hyperlink_cbs={
                "tin_ore": lambda _: CheckUsage(id_enum.Ore.TIN),
                "lead_ore": lambda _: CheckUsage(id_enum.Ore.LEAD),
                "nickel_ore": lambda _: CheckUsage(id_enum.Ore.NICKEL),
                "silver_ore": lambda _: CheckUsage(id_enum.Ore.SILVER),
                "platinum_ore": lambda _: CheckUsage(id_enum.Ore.PLATINUM),
            },
        ),
    ],
)
