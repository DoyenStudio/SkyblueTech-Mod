# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

alloy_furnace = PageGroup([
    TextPage(
        "alloy_furnace_description_1",
        "合金炉",
        "合金炉可以将多种金属或非金属混合烧制为§5合金§r。\n钢锭、 青铜锭、 殷钢锭等都需要合金炉进行烧制。",
    ),
    MachineryWorkstationRecipePage(
        "alloy_furnace_description_2", id_enum.ALLOY_FURNACE
    ),
])


compressor = PageGroup([
    TextPage(
        "compressor_description_1",
        "压缩机",
        "压缩机可将金属锭压制为板材， 除此以外还能对一些材料进行进一步压缩。",
    ),
    MachineryWorkstationRecipePage("compressor_description_2", id_enum.COMPRESSOR),
])

distillation_chamber = PageGroup([
    TextPage(
        "distillation_chamber_description_1",
        "小型蒸馏仓",
        "小型蒸馏仓可以使用§c热能§r对其中的流体进行§9蒸馏§r， 如生产蒸馏水和部分油类液体等。\n它的下方需要一个§4热源§r为其供热， 如电力加热仓。",
    ),
    TextPage(
        "distillation_chamber_description_2",
        "",
        "对比蒸馏塔， 无法使用过高或过低的温度， 也无法生产副产物， 但是可以进行需要精细控温的蒸馏， 相比之下产率也更高。",
    ),
    MachineryWorkstationRecipePage(
        "distillation_chamber_description_3", id_enum.DISTILLATION_CHAMBER
    ),
])

electric_crafter = PageGroup([
    TextPage(
        "electric_crafter_description_1",
        "电动合成台",
        "电动合成台可按§2给定模版§r和输入物品消耗能量自动进行§9物品合成§r。\n需要先制作一个合成模版， 手持合成模版下蹲点击地面打开模版设置界面进行合成配方设置， 然后将其插入电动合成台中， 即可进行自动合成。",
    ),
    MachineryWorkstationRecipePage(
        "electric_crafter_description_2", id_enum.ELECTRIC_CRAFTER
    ),
])

electric_heater = PageGroup([
    TextPage(
        "electric_heater_description_1",
        "电力加热仓",
        "通电后可按照设置的温度向上前后左右五个铜盘面输出§c热能§r， 供一些需热机器使用。",
    ),
    MachineryWorkstationRecipePage(
        "electric_heater_description_2", id_enum.ELECTRIC_HEATER
    ),
])

fluid_condenser = PageGroup([
    TextPage(
        "fluid_condenser_description_1",
        "流体冷却机",
        "流体冷却机可将§c高温流体§r进行冷却获得物品产物。 如将熔融金属冷却为锭。",
    ),
    MachineryWorkstationRecipePage(
        "fluid_condenser_description_2", id_enum.FLUID_CONDENSER
    ),
])

freezer = PageGroup([
    TextPage(
        "freezer_description_1",
        "冷冻机",
        "可按照设置将水§9冷冻§r为冰雪。 可以选择生产冰块、 浮冰、 蓝冰、 雪块或雪球， 所需水量、 加工时间和能耗各不相同。",
    ),
    MachineryWorkstationRecipePage("freezer_description_2", id_enum.FREEZER),
])

hydroponic_base = PageGroup([
    TextPage(
        "hydroponic_base_description_1",
        "水培基座",
        "水培基座为其上方的§2水培床§r提供作物生长所需水源， 同时水培床的作物产出也会存放到水培基座供抽取。\n\n水培床所需水分或营养液需要输入到其下方的水培基座才能被水培床利用。",
    ),
    MachineryWorkstationRecipePage(
        "hydroponic_base_description_2", id_enum.HYDROPONIC_BASE
    ),
])

hydroponic_bed = PageGroup([
    TextPage(
        "hydroponic_bed_description_1",
        "水培床",
        "水培床可给予其中的作物恒定稳定的光照和水分， §2加快作物生长§r。\n为水培床下方的§9水培基座§r供水， 在水培床内放置作物种子， 再在水培床上方使用线缆进行供能， 即可使作物进入生长周期。",
    ),
    TextPage(
        "hydroponic_bed_description_2",
        "",
        "水培床会§2自动§r从产出中收取一枚种子进行补种， 剩余产物会被存入下方的§9水培基座§r。",
    ),
    MachineryWorkstationRecipePage(
        "hydroponic_bed_description_3", id_enum.HYDROPONIC_BED
    ),
])

macerator = PageGroup([
    TextPage(
        "macerator_description_1",
        "磨粉机",
        "磨粉机能被用于物品磨粉、 矿物粉碎等。 它能将金属锭隔绝空气磨成金属粉， 也能对部分自然资源进行粉碎处理， 还能对粗矿甚至远古残骸进行研磨增产。",
    ),
    MachineryWorkstationRecipePage("macerator_description_2", id_enum.MACERATOR),
])

magma_centrifuge = PageGroup([
    TextPage(
        "magma_centrifuge_description_1",
        "高热流体离心机",
        "高热流体离心机主要用于对§4熔岩§r类混合物流体进行离心， 例如对深层熔岩进行离心， 再对产物进行进一步离心得到熔融矿物质。",
    ),
    MachineryWorkstationRecipePage(
        "magma_centrifuge_description_2", id_enum.MAGMA_CENTRIFUGE
    ),
])

magma_furnace = PageGroup([
    TextPage(
        "magma_furnace_description_1",
        "熔岩炉",
        "熔岩炉以比较高的功耗§c熔化物品§r， 例如将金属熔化为熔融金属， 将石头熔化为熔岩。\n\n使用§5特化控制电路： 高热熔岩工厂§r升级可加快熔岩产出、 降低熔岩炉能耗， 但是此时熔岩炉§c只能§r生产熔岩。",
    ),
    MachineryWorkstationRecipePage(
        "magma_furnace_description_2", id_enum.MAGMA_FURNACE
    ),
])

metal_press = PageGroup([
    TextPage(
        "metal_press_description_1",
        "金属冲压机",
        "可以使用一份金属原料和润滑油生产金属棒。",
    ),
    MachineryWorkstationRecipePage("metal_press_description_2", id_enum.METAL_PRESS),
])

mixer = PageGroup([
    TextPage(
        "mixer_description_1",
        "固液搅拌机",
        "可以将固体与流体进行混合搅拌得到固体新产物。",
    ),
    MachineryWorkstationRecipePage("mixer_description_2", id_enum.MIXER),
])

oil_extractor = PageGroup([
    TextPage(
        "oil_extractor_description_1",
        "榨油机",
        "可将部分植物种子榨油以得到§a植物油§r。",
    ),
    MachineryWorkstationRecipePage(
        "oil_extractor_description_2", id_enum.OIL_EXTRACTOR
    ),
])

redstone_furnace = PageGroup([
    TextPage(
        "redstone_furnace_description_1",
        "红石炉",
        "红石炉将红石能作为燃料， 和熔炉一样§c烧制物品§r。",
    ),
    MachineryWorkstationRecipePage(
        "redstone_furnace_description_2", id_enum.REDSTONE_FURNACE
    ),
])
