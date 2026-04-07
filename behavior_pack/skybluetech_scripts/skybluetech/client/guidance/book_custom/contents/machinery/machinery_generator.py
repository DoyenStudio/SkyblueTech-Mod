# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

creative_generator = PageGroup([
    TextPage(
        "creative_generator_description_1",
        "创造模式发电机",
        "§c§l本物品仅存于创造模式。§r\n创造模式发电机可以无条件提供 §52147483647 RF§r 的能量输出功率。\n如果你正在创造模式存档中试验生产流水线， 不妨直接将其作为能量源吧。",
    ),
])

geothermal_generator = PageGroup([
    TextPage(
        "geothermal_generator_description_1",
        "地热发电机",
        "地热发电机消耗§4§l熔岩§r进行发电， 输入§9水§r将§2大大提升地热发电机的产能效率§r。\n\n如果输入水， 则地热发电机工作过程中会不定产出石粉或黑曜石粉。",
    ),
    MachineryWorkstationRecipePage(
        "geothermal_generator_description_2", id_enum.GEO_THERMAL_GENERATOR
    ),
])


solar_panel = PageGroup([
    TextPage(
        "solar_panel_description_1",
        "太阳能电池板",
        "太阳能电池板可使用§e§l阳光§r产生红石能。\n\n太阳能电池板上方不能有任何方块阻挡。\n\n在晴天的中午电池板可达到§c最大发电功率§r， 如遇雨天则会使发电效率降低。",
    ),
    MachineryWorkstationRecipePage("solar_panel_description_2", id_enum.SOLAR_PANEL),
])

thermal_generator = PageGroup([
    TextPage(
        "thermal_generator_description_1",
        "火力发电机",
        "作为最简单的供能发电机之一， 火力发电机直接§4燃烧燃料§r以提供能量。\n\n除§c岩浆桶§r以外（请改为使用地热发电机）， 燃料和熔炉可使用的的燃料一致。",
    ),
    MachineryWorkstationRecipePage(
        "thermal_generator_description_2", id_enum.THERMAL_GENERATOR
    ),
])

wind_generator = PageGroup([
    TextPage(
        "wind_generator_description_1",
        "风力发电机",
        "风力发电机可使用§9风能§r进行发电。\n\n高处风能更强， 意味着将风力发电机放在高处可增大发电功率。\n\n若风力发电机的扇面前后被方块挡住， 其工作效率会下降。",
    ),
    TextPage(
        "wind_generator_description_2",
        "风力发电机",
        "风力发电机需要使用§9扇叶§r进行工作。 工作时会消耗扇叶§2耐久度§r。 不同的扇叶会提供不同的§3输出功率§r和耐久度。",
    ),
    MachineryWorkstationRecipePage(
        "wind_generator_description_3", id_enum.WIND_GENERATOR
    ),
])
