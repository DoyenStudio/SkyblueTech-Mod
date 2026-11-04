# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum

from ...define import (
    MachineryWorkstationRecipePage,
    PageGroup,
    TextPage,
    UnfinishedItemName,
)

electric_heater = PageGroup(
    "electric_heater_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ELECTRIC_HEATER),
            '通电后可按照设置的温度向上前后左右五个铜盘面输出<text color="§c" t="热能">， 供一些需热机器使用。\n\n适当调节输入功率和最大温度可以让其达到合适的产热温度。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ELECTRIC_HEATER),
    ],
)

infrared_heat_generator = PageGroup(
    "infrared_heat_generator_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.INFRARED_HEAT_GENERATOR),
            '红外高热发生器通电后可按照设置的温度向上前后左右五个铜盘面输出<text color="§c" t="热能">， 最高加热至 <text color="§c" t="2300 K">。\n\n与电力加热仓一样， 可以调节输入功率和目标温度。',
        ),
    ],
)

fuel_heater = PageGroup(
    "fuel_heater_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.FUEL_HEATER),
            '燃料加热器直接<text color="§c" t="燃烧燃料">来产生<text color="§c" t="热能">， 供一些需热机器使用， 相对于先发电后产热， 燃料加热器直接消耗燃料产热效率可以高数倍。\n\n干烧时可达到 900K 的温度。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.FUEL_HEATER),
    ],
)

heat_conductor = PageGroup(
    "heat_conductor_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HEAT_CONDUCTOR),
            '导热块可在<item id="{provider}"><text color="§c" t="产热机器">和<item id="{accepter}"><text color="§9" t="需热机器">间传递热量。\n\n导热块本身具有较高热容， 热能在导热块上传递需要一定时间。\n\n热能在导热块上按物理规律进行热交换， 所以你也可以在导热块路径上制造<text color="§2" t="支路">以分散热力。'.format(
                provider=id_enum.Machinery.ELECTRIC_HEATER,
                accepter=id_enum.Machinery.DISTILLATION_CHAMBER,
            ),
        ),
        TextPage(
            "",
            '在工作台以 4 份<item id="{steel_plate}">钢板、 4 份<item id="{copper_plate}">铜板和 1 个<item id="minecraft:copper_ingot">铜锭即可制作导热块。'.format(
                steel_plate=id_enum.Plates.STEEL, copper_plate=id_enum.Plates.COPPER
            ),
        )
    ],
)
