# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

alloy_furnace = PageGroup(
    "alloy_furnace_description",
    [
        TextPage(
            "合金炉",
            '合金炉可以将多种金属<item id="%s">或非金属<item id="%s">混合烧制为<style color="§5" t="合金"><item id="%s">。\n钢锭、 青铜锭、 殷钢锭等都需要合金炉进行烧制。'
            % ("minecraft:iron_ingot", id_enum.Dusts.CARBON, id_enum.Ingots.STEEL),
        ),
        MachineryWorkstationRecipePage(id_enum.ALLOY_FURNACE),
    ],
)


compressor = PageGroup(
    "compressor_description",
    [
        TextPage(
            "压缩机",
            '压缩机可将金属锭<item id="%s">压制为板材<item id="%s">， 除此以外还能对一些材料进行进一步压缩。'
            % (id_enum.Ingots.TIN, id_enum.Plates.TIN),
        ),
        MachineryWorkstationRecipePage(id_enum.COMPRESSOR),
    ],
)

distillation_chamber = PageGroup(
    "distillation_chamber_description",
    [
        TextPage(
            "小型蒸馏仓",
            '小型蒸馏仓可以使用<text color="§c" t="热能">对其中的流体进行<text color="§9" t="蒸馏">， 如生产蒸馏水和部分油类液体等。\n它的下方需要一个<text color="§4" t="热源">为其供热， 如<link text="电力加热仓" id="electric_heater">。',
            hyperlink_cbs={"electric_heater": lambda _: electric_heater.FastJump()},
        ),
        TextPage(
            "",
            "对比蒸馏塔， 无法使用过高或过低的温度， 也无法生产副产物， 但是可以进行需要精细控温的蒸馏， 相比之下产率也更高。",
        ),
        MachineryWorkstationRecipePage(id_enum.DISTILLATION_CHAMBER),
    ],
)

electric_crafter = PageGroup(
    "electric_crafter_description",
    [
        TextPage(
            "电动合成台",
            '电动合成台可按<text color="§2" t="给定模版">和输入物品消耗能量自动进行<text color="§9" t="物品合成">。\n需要先制作一个<link id="crafting_template_recipe" text="合成模版">， 手持合成模版下蹲点击地面打开模版设置界面进行合成配方设置， 然后将其插入电动合成台中， 即可进行自动合成。',
            hyperlink_cbs={
                "crafting_template_recipe": lambda _: CheckRecipe(
                    id_enum.CRAFTING_TEMPLATE
                )
            },
        ),
        MachineryWorkstationRecipePage(id_enum.ELECTRIC_CRAFTER),
    ],
)

electric_heater = PageGroup(
    "electric_heater_description",
    [
        TextPage(
            "电力加热仓",
            '通电后可按照设置的温度向上前后左右五个铜盘面输出<text color="§c" t="热能">， 供一些需热机器使用。',
        ),
        MachineryWorkstationRecipePage(id_enum.ELECTRIC_HEATER),
    ],
)

fluid_condenser = PageGroup(
    "fluid_condenser_description",
    [
        TextPage(
            "流体冷却机",
            '流体冷却机可将<text color="§c" t="高温流体">进行冷却获得物品产物。 如将熔融金属冷却为锭。',
        ),
        MachineryWorkstationRecipePage(id_enum.FLUID_CONDENSER),
    ],
)

freezer = PageGroup(
    "freezer_description",
    [
        TextPage(
            "冷冻机",
            '可按照设置将水<text color="§9" t="冷冻">为冰雪。 可以选择生产冰块<item id="minecraft:ice">、 浮冰<item id="minecraft:packed_ice">、 蓝冰<item id="minecraft:blue_ice">、 雪块<item id="minecraft:snow">或雪球<item id="minecraft:snowball">， 所需水量、 加工时间和能耗各不相同。',
        ),
        MachineryWorkstationRecipePage(id_enum.FREEZER),
    ],
)

hydroponic_base = PageGroup(
    "hydroponic_base_description",
    [
        TextPage(
            "水培基座",
            '水培基座为其上方的<style color="§2"><link text="水培床" id="hydroponic_bed"><style color="R">提供作物生长所需水源， 同时水培床的作物产出也会存放到水培基座供抽取。\n\n水培床所需水分或营养液需要输入到其下方的水培基座才能被水培床利用。',
            hyperlink_cbs={"hydroponic_bed": lambda _: hydroponic_bed.FastJump()},
        ),
        MachineryWorkstationRecipePage(id_enum.HYDROPONIC_BASE),
    ],
)

hydroponic_bed = PageGroup(
    "hydroponic_bed_description",
    [
        TextPage(
            "水培床",
            '水培床可给予其中的作物<item id="minecraft:wheat_seeds">恒定的光照和水分， <text color="§2" t="加快作物生长">。\n为水培床下方的<link text="水培基座" id="hydroponic_base">供水， 在水培床内放置作物种子， 再在水培床上方使用线缆进行供能， 即可使作物进入生长周期。',
            hyperlink_cbs={"hydroponic_base": lambda _: hydroponic_base.FastJump()},
        ),
        TextPage(
            "",
            '水培床会<text color="§2" t="自动">从产出中收取一枚种子进行补种， 剩余产物会被存入下方的<text color="§9" t="水培基座">。',
        ),
        MachineryWorkstationRecipePage(id_enum.HYDROPONIC_BED),
    ],
)

macerator = PageGroup(
    "macerator_description",
    [
        TextPage(
            "磨粉机",
            '磨粉机能被用于物品磨粉<item id="minecraft:bone_meal">、 矿物粉碎<item id="%s">等。 它能将金属锭隔绝空气磨成金属粉， 也能对部分自然资源进行粉碎处理， 还能对粗矿甚至远古残骸进行研磨增产。'
            % id_enum.Dusts.TIN,
        ),
        MachineryWorkstationRecipePage(id_enum.MACERATOR),
    ],
)

magma_centrifuge = PageGroup(
    "magma_centrifuge_description",
    [
        TextPage(
            "高热流体离心机",
            '高热流体离心机主要用于对<text color="§4" t="熔岩"><item id="minecraft:lava_bucket">类混合物流体进行离心， 例如对深层熔岩进行离心， 再对产物进行进一步离心得到熔融矿物质。',
        ),
        MachineryWorkstationRecipePage(id_enum.MAGMA_CENTRIFUGE),
    ],
)

magma_furnace = PageGroup(
    "magma_furnace_description",
    [
        TextPage(
            "熔岩炉",
            '熔岩炉以比较高的功耗<text color="§c" t="熔化物品">， 例如将金属熔化为熔融金属， 将石头熔化为熔岩。\n\n使用<link text="特化控制电路： 高热熔岩工厂" id="magma_factory_recipe">升级可加快熔岩产出、 降低熔岩炉能耗， 但是此时熔岩炉<text color="§c" t="只能">生产熔岩。',
            hyperlink_cbs={
                "magma_factory_recipe": lambda _: CheckRecipe(
                    id_enum.Upgraders.SPEC_MAGMA_FACTORY
                )
            },
        ),
        MachineryWorkstationRecipePage(id_enum.MAGMA_FURNACE),
    ],
)

metal_press = PageGroup(
    "metal_press_description",
    [
        TextPage(
            "金属冲压机",
            '可以使用一份金属原料<item id="%s">和润滑油生产金属棒<item id="%s">。'
            % (id_enum.Ingots.TIN, id_enum.Sticks.TIN),
        ),
        MachineryWorkstationRecipePage(id_enum.METAL_PRESS),
    ],
)

mixer = PageGroup(
    "mixer_description",
    [
        TextPage(
            "固液搅拌机",
            "可以将固体与流体进行混合搅拌得到固体新产物。",
        ),
        MachineryWorkstationRecipePage(id_enum.MIXER),
    ],
)

oil_extractor = PageGroup(
    "oil_extractor_description",
    [
        TextPage(
            "榨油机",
            '可将部分植物种子<item id="minecraft:wheat_seeds">榨油以得到<text color="§a" t="植物油">。',
        ),
        MachineryWorkstationRecipePage(id_enum.OIL_EXTRACTOR),
    ],
)

redstone_furnace = PageGroup(
    "redstone_furnace_description",
    [
        TextPage(
            "红石炉",
            '红石炉将红石能这种能源作为燃料， 和熔炉<item id="minecraft:furnace">一样<text color="§c" t="烧制物品">。',
        ),
        MachineryWorkstationRecipePage(id_enum.REDSTONE_FURNACE),
    ],
)
