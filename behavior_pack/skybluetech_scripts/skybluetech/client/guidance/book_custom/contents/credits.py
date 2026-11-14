# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum

from ..define import (
    MainTOCPage,
    MainTOCPageSection,
    PageGroup,
    TextPage,
)

credits = PageGroup(
    "credits",
    [
        TextPage(
            "鸣谢",
            '特别感谢开发者<text color="§d" t="无名QwQ">对本模组的界面与材质的优化， 以及对 MEI 物品管理器的适配支持；\n\n感谢<text color="§1" t="游趣开发组、 苦柠、 方创工坊、 泼皮、 小波、 棱花 Arris、 酒石酸菌、 贝拉瑞尔大陆">等开发者 / 团体为本模组开发过程遇到之困难的答疑解惑。',
        ),
        TextPage(
            "鸣谢",
            '《蔚蓝科技》自 2024 年在 <text color="§9" t="Skyblue 租赁服"> 作为指令原型玩法诞生以来， 收到了各路玩家的支持与实用反馈， 感谢你们的支持：\n<text color="§9" t="恐惧的鬼魂迦叶">、 <text color="§5" t="一只屑喵鲨">、 <text color="§6" t="炉子盖儿是真没">、 <text color="§s" t="网抑云墨画">、 <text color="§2" t="清风ovo">、 <text color="§4" t="无情awa">、 <text color="§d" t="123321">、 开心的石头等曾经在蔚蓝系列租赁服长期游玩的玩家， 让《蔚蓝科技》得以升级为真正的模组玩法。',
        ),
    ],
)
