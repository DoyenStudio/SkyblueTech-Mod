# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MainTOCPage,
    MainTOCPageSection,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

general_intro_pages = PageGroup([
    TextPage(
        "general_intro_1",
        "引言",
        "蔚蓝科技是一款§9科技模组§r， 加入了多种多样的机器、 发电机、 工具和护甲。 你可以使用机器和物流系统搭建全自动物品生产的工业流水线， 也可以制造使用红石能的装备来提升你的采集和挖掘能力！",
    ),
    TextPage(
        "energy_intro_2",
        "",
        "未完待续 ..？",
    ),
])


energy_intro = PageGroup([
    TextPage(
        "energy_intro_1",
        "能源",
        "作为几乎唯一通用的能源， §4红石能§r是整个蔚蓝科技工业系统的核心。\n几乎一切机器都需要消耗红石能以维持运行； 发电机可以产生红石能， 而各种线缆与中继塔可以传导红石能。\n§c红石通量 (RedstoneFlux, 简称 RF) §r是度量红石能的能源单位。",
    ),
    TextPage(
        "energy_intro_2",
        "",
        "可以将发电机与用电器使用线缆连接以传输红石能， 也可以将发电机与用电器紧邻放置直接传导能量。\n\n注意： 由充能方块产生的是§4红石信号§r， 与§4红石能§r存在根本差别， 所以即便是红石块也无法直接产生红石能。",
    ),
])

fluid_intro = PageGroup([
    TextPage(
        "fluid_intro_1",
        "流体",
        "气体和液体统称为流体， 需要使用§9流体管道§r进行传输。\n§9流体储罐§r可存储液体或气体。\n手持§2空桶§r点击存储了流体的机器可将其中的流体进行装桶； 反之可向其装填流体。",
    )
])
