# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ..define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)


energy_transmit = PageGroup(
    "energy_transmit",
    [
        TextPage(
            "能源传输",
            '如果你只有少量的机器需要供能， 可以直接将发电机和用电器方块<text color="§c" t="紧邻放置">， 发电机就可以给六个面的用电器直接提供能源。\n\n如果你需要为多个用电器供能， 那么就需要使用<text color="§3" t="线缆">将发电机和用电器<text color="§c" t="直接连接">起来。 \n\n线缆具有<text color="§3" t="最大传输功率">， 单位为 RF/t。',
        ),
        TextPage(
            "",
            '裸线缆和绝缘线缆都可以传导能量。 唯一区别是裸线缆在传输能量时会<text color="§c" t="电击">触碰它的任何生物， 包括正在铺设线缆的你！ \n\n功率越大电击伤害越大。 所以在正常情况下最好使用<text color="§1" t="绝缘线缆">进行能量传输！',
        ),
        TextPage(
            "",
            '即使机器是并联入网的， 线缆也<text color="§4" t="不会">给每个机器均匀供能， 而是先给其中一个机器充满能量后再向下一个机器供能。 你可以使用<text color="§5" t="传输设置扳手">在线缆与机器连接的末端处设置线缆供电的<text color="§2" t="优先级">。\n\n如果对用电器设置优先级， 则会改变其在电网中的供电优先程度， 优先级高的机器会更先被供能； 优先级高的发电机则会优先被用于供能。',
        ),
    ],
)

energy_transmit_remote = PageGroup(
    "energy_transmit_remote",
    [
        TextPage(
            "能源远距离传输",
            "当你的发电机和用电器相隔甚远时， 就不能再依赖于线缆了， 铺设长距离的线缆可能会带来相当高的铺设成本。\n\n为了解决这个问题， 你需要布设§c能源中继塔§r来进行远距离能源传输。",
        ),
        TextPage(
            "",
            "两个能源中继塔需要§2手动进行接线§r， 它们§2最大的直线相隔距离为 64 格§r。\n\n即使同一个电网中的部分能源中继塔不在加载区内， 只要供电端和接收端处于加载区， 能源中继塔电网就可以正常能源传输。\n\n不过能源中继塔无法直接将红石能传递给用电器， 需要从能源中继塔§c接出线缆§r后连接用电器。",
        ),
    ],
)


energy_toc = PageGroup(
    "energy_toc",
    [
        TextPage(
            "能源",
            '<text color="§c" t="红石能">作为整套工业系统的能源， 是保障机器持续运作的根基。',
        ),
        TOCPage(
            [
                TOCPageSection(id_enum.Wire.COPPER, 0, "能源传输", energy_transmit),
                TOCPageSection(
                    id_enum.RF_REPEATER_PLANT, 0, "能源远距传输", energy_transmit_remote
                ),
            ],
        ),
    ],
)
