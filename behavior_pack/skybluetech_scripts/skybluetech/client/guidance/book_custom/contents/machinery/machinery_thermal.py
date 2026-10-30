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

fuel_heater = PageGroup(
    "fuel_heater_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.FUEL_HEATER),
            '燃料加热器直接<text color="§c" t="燃烧燃料">来产生<text color="§c" t="热能">， 供一些需热机器使用。\n\n干烧时可达到 900K 的温度。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.FUEL_HEATER),
    ],
)
