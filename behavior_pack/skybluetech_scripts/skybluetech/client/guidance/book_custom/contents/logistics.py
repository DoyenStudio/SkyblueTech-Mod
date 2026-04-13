# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ..define import (
    TextPage,
    MainTOCPage,
    MainTOCPageSection,
    PageGroup,
)
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe

# logistics_general = PageGroup(
#     "logistics_general",
#     [
#         TextPage(
#             "通用介绍",
#             "",
#         ),
#         TextPage(
#             "",
#             '裸线缆和绝缘线缆都可以传导能量。 唯一区别是裸线缆在传输能量时会<text color="§c" t="电击">触碰它的任何生物， 包括正在铺设线缆的你！ \n\n功率越大电击伤害越大。 所以在正常情况下最好使用<text color="§1" t="绝缘线缆">进行能量传输！',
#         ),
#         TextPage(
#             "",
#             '即使机器是并联入网的， 线缆也<text color="§4" t="不会">给每个机器均匀供能， 而是先给其中一个机器充满能量后再向下一个机器供能。 你可以使用<text color="§5" t="传输设置扳手">在线缆与机器连接的末端处设置线缆供电的<text color="§2" t="优先级">。\n\n如果对用电器设置优先级， 则会改变其在电网中的供电优先程度， 优先级高的机器会更先被供能； 优先级高的发电机则会优先被用于供能。',
#         ),
#     ],
# )

logistics_item = PageGroup(
    "logistics_item",
    [
        TextPage(
            "物品物流",
            '使用<text color="§9" t="物品管道">可以在两个容器或机器间传输物品。',
        ),
        TextPage(
            "",
            '对着物品管道<item id="%s">与容器的连接处使用<link text="管道扳手" id="t"><item id="%s">可以改变管道对该容器的存取模式， 默认为输入（存入物品）， 如果调整到输出模式， 管道接入容器的的一面会略微变粗一圈， 表示从这个容器中取出物品。'
            % (id_enum.Cable.STEEL, id_enum.TRANSMITTER_WRENCH),
            hyperlink_cbs={"t": lambda _: CheckRecipe(id_enum.TRANSMITTER_WRENCH)},
        ),
        TextPage(
            "",
            '使用<link text="传输设置扳手" id="t"><item id="%s">对着管道与容器的连接处使用可以打开<text color="§5" t="传输设置界面">， 调整管道的传输标志和优先级。 越高的优先级代表该容器越优先被用于物品传输。'
            % id_enum.TRANSMITTER_SETTINGS_WRENCH,
            hyperlink_cbs={
                "t": lambda _: CheckRecipe(id_enum.TRANSMITTER_SETTINGS_WRENCH)
            },
        ),
    ],
)

logistics_fluid = PageGroup(
    "logistics_fluid",
    [
        TextPage(
            "流体物流",
            '使用<text color="§9" t="流体管道">可以在两个容器或机器间传输流体。',
        ),
        TextPage(
            "",
            '对着流体管道<item id="%s">与容器的连接处使用<link text="管道扳手" id="t"><item id="%s">可以改变管道对该容器的存取模式， 默认为输入（存入物品）， 如果调整到输出模式， 管道接入容器的的一面会略微变粗一圈， 表示从这个容器中取出流体。'
            % (id_enum.Pipe.BRONZE, id_enum.TRANSMITTER_WRENCH),
            hyperlink_cbs={"t": lambda _: CheckRecipe(id_enum.TRANSMITTER_WRENCH)},
        ),
    ],
)


logistics_toc = PageGroup(
    "logistics_toc",
    [
        TextPage(
            "物流",
            '蔚蓝科技的物流系统允许你使用各种各样的<text color="§2" t="传输管道">运输物品和流体。',
        ),
        MainTOCPage(
            [
                MainTOCPageSection(id_enum.Cable.STEEL, 0, "物品物流", logistics_item),
                MainTOCPageSection(id_enum.Pipe.BRONZE, 0, "流体物流", logistics_fluid),
            ],
        ),
    ],
)
