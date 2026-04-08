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

general_intro_pages = PageGroup(
    "general_intro",
    [
        TextPage(
            "引言",
            '蔚蓝科技是一款<text color="§9" t="科技模组">， 加入了多种多样的机器、 发电机、 工具和护甲。 你可以使用机器和物流系统搭建全自动物品生产的工业流水线， 也可以制造使用红石能的装备来提升你的采集和挖掘能力！',
        ),
        TextPage(
            "",
            "未完待续 ..？",
        ),
    ],
)


energy_intro = PageGroup(
    "energy_intro",
    [
        TextPage(
            "能源",
            '作为几乎唯一通用的能源， <text color="§4" t="红石能">是整个蔚蓝科技工业系统的核心。\n几乎一切机器都需要消耗红石能以维持运行； 发电机可以产生红石能， 而各种线缆与中继塔可以传导红石能。\n<text color="§c" t="红石通量 (RedstoneFlux, 简称 RF) ">是度量红石能的能源单位。',
        ),
        TextPage(
            "",
            '可以将发电机与用电器使用线缆连接以传输红石能， 也可以将发电机与用电器紧邻放置直接传导能量。\n\n注意： 由充能方块产生的是<text color="§4" t="红石信号">， 与<text color="§4" t="红石能">存在根本差别， 所以即便是红石块也无法直接产生红石能。',
        ),
    ],
)

fluid_intro = PageGroup(
    "fluid_intro",
    [
        TextPage(
            "流体",
            '气体和液体统称为流体， 需要使用<text color="§9" t="流体管道">进行传输。\n<text color="§9" t="流体储罐">可存储液体或气体。\n手持<text color="§2" t="空桶">点击存储了流体的机器可将其中的流体进行装桶； 反之可向其装填流体。',
        )
    ],
)
