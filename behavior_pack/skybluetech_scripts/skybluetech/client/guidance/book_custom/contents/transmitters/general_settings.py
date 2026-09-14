# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

general_settings = PageGroup(
    "transmitter_general_settings",
    [
        TextPage(
            "传输管道通用设置",
            '使用<item id="{wrench}"><link id="wrench" text="管道扳手">可以调整管道对容器的<text color="§3" t="提取/存入模式">， 手持管道扳手对准<text color="§2" t="容器与管道的连接处">点击即可。\n\n<text color="§2" t="潜行">后点击管道朝向容器、 管道的一面， 可以<text color="§3" t="断开或恢复">这一面的连接， 机器一侧的管道插座会一起收起或伸出； 对准<text color="§2" t="管道之间的连接处">点击也可以直接切断两根管道之间的连接。\n\n处于<text color="§4" t="提取">模式下， 管道会从容器内提取物品或流体； 处于<text color="§2" t="存入">模式下则会向容器内输入物品或流体。'.format(
                wrench=id_enum.TRANSMITTER_WRENCH
            ),
            hyperlink_cbs={"wrench": lambda _: CheckRecipe(id_enum.TRANSMITTER_WRENCH)},
        ),
        TextPage(
            "",
            '使用<item id="{wrench}"><link id="wrench" text="传输设置扳手">可以调整容器处于传输管网中的优先级， 手持管道扳手对准<text color="§2" t="容器与管道的连接处">点击即可。\n\n<text color="§2" t="优先级更高的容器会更先被用于提取/存入">。'.format(
                wrench=id_enum.TRANSMITTER_SETTINGS_WRENCH
            ),
            hyperlink_cbs={
                "wrench": lambda _: CheckRecipe(id_enum.TRANSMITTER_SETTINGS_WRENCH)
            },
        ),
    ],
)
