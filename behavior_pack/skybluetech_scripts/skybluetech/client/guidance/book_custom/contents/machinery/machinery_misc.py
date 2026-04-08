# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

deepslate_lava_vibrator = PageGroup(
    "deepslate_lava_vibrator_description",
    [
        TextPage(
            "深层熔岩谐振探测器",
            '深层熔岩谐振探测器用于在建造<text color="§d" t="基岩熔岩钻">开采<text color="§4" t="深层熔岩">之前先行探明此地的深层熔岩储量。',
        ),
        TextPage(
            "",
            "将深层熔岩谐振探测器放置到地面， 为其输入能量就可以启动探测。 勘探进度越多， 勘探到的深层熔岩储量也越准确。 勘探进度到达百分百后探测到的深层熔岩储量就几乎是百分百准确了。",
        ),
        MachineryWorkstationRecipePage(id_enum.DEEPSLATE_LAVA_VIBRATOR),
    ],
)

hover_text_displayer = PageGroup(
    "hover_text_displayer_description",
    [
        TextPage(
            "悬浮文本投影器",
            '悬浮文本投影器通过消耗能量来将<text color="§5" t="悬浮文本">投射到世界上， 类似 NPC 头顶的悬浮字效果。\n文本的长度和是否带颜色会影响最终功耗。',
        ),
        MachineryWorkstationRecipePage(id_enum.HOVER_TEXT_DISPLAYER),
    ],
)
