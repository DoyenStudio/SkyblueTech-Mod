# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

creative_generator = PageGroup(
    "creative_generator_description",
    [
        TextPage(
            "创造模式发电机",
            '<text color="§c" t="本物品仅存于创造模式。">\n创造模式发电机可以无条件提供 <text color="§5" t="2147483647 RF"> 的能量输出功率。\n如果你正在创造模式存档中试验生产流水线， 不妨直接将其作为能量源吧。',
        ),
    ],
)

geothermal_generator = PageGroup(
    "geothermal_generator_description",
    [
        TextPage(
            "地热发电机",
            '地热发电机消耗<text color="§4" t="熔岩">进行发电， 输入<text color="§9" t="水">将<text color="§2" t="大大提升地热发电机的产能效率">。\n\n如果输入水， 则地热发电机工作过程中会不定产出黑曜石粉<item id="%s">。'
            % id_enum.Dusts.OBSIDIAN,
        ),
        MachineryWorkstationRecipePage(id_enum.GEO_THERMAL_GENERATOR),
    ],
)

redstone_generator = PageGroup(
    "redstone_generator_description",
    [
        TextPage(
            "红石发电机",
            '红石发电机使用<item id="minecraft:redstone"><text color="§4" t="红石">或<item id="minecraft:redstone_block"><text color="§4" t="红石块">进行快速且大功率地产能。\n\n红石发电机提取红石或红石块中所含红石能， 被提取后的红石会转化为<item id="%s"><text color="§4" t="惰性红石">。'
            % id_enum.DEACTIVATION_REDSTONE,
        ),
        MachineryWorkstationRecipePage(id_enum.REDSTONE_GENERATOR),
    ],
)


solar_panel = PageGroup(
    "solar_panel_description",
    [
        TextPage(
            "太阳能电池板",
            '太阳能电池板可使用<text color="§e" t="阳光">产生红石能。\n\n太阳能电池板上方不能有任何方块阻挡。\n\n在晴天的中午电池板可达到<text color="§c" t="最大发电功率">， 如遇雨天则会使发电效率降低。',
        ),
        MachineryWorkstationRecipePage(id_enum.SOLAR_PANEL),
    ],
)

thermal_generator = PageGroup(
    "thermal_generator_description",
    [
        TextPage(
            "火力发电机",
            '作为最简单的供能发电机之一， 火力发电机直接<text color="§4" t="燃烧燃料">以提供能量。\n\n除<text color="§c" t="岩浆桶">以外（请改为使用地热发电机）， 燃料和熔炉可使用的的燃料一致。',
        ),
        MachineryWorkstationRecipePage(id_enum.THERMAL_GENERATOR),
    ],
)

wind_generator = PageGroup(
    "wind_generator_description",
    [
        TextPage(
            "风力发电机",
            '风力发电机可使用<text color="§9" t="风能">进行发电。\n\n高处风能更强， 意味着将风力发电机放在高处可增大发电功率。\n\n若风力发电机的扇面前后被方块挡住， 其工作效率会下降。',
        ),
        TextPage(
            "",
            '风力发电机需要使用<text color="§9" t="扇叶">进行工作。 工作时会消耗扇叶<item id="%s"><text color="§2" t="耐久度">。 不同的扇叶会提供不同的<text color="§3" t="输出功率">和耐久度。'
            % id_enum.Paddle.IRON,
        ),
        MachineryWorkstationRecipePage(id_enum.WIND_GENERATOR),
    ],
)

gas_burning_generator = PageGroup(
    "gas_burning_generator_description",
    [
        TextPage(
            "燃气发电机",
            '燃气发电机可以燃烧<text color="§d" t="气体">用于发电。\n\n一些气体在经过燃烧后会产生<text color="§7" t="废气">， 需要进行处理， 否则将堆积在燃气发电机内使其无法继续燃烧。',
        ),
        MachineryWorkstationRecipePage(id_enum.GAS_BURNING_GENERATOR),
    ],
)
