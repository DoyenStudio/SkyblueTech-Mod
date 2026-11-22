# coding=utf-8
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    PushRecipeCheckerUI,
)
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.common.machinery_def.chunk_anchor import (
    ANCHOR as CHUNK_ANCHOR,
)
from skybluetech_scripts.skybluetech.common.machinery_def.chunk_anchor import (
    STRUCTURE_PALETTE as CHUNK_ANCHOR_SP,
)
from skybluetech_scripts.skybluetech.common.machinery_def.effluent_outfall import (
    recipes as EFFLUENT_OUTFALL_RECIPES,
)

from ...define import (
    MachineryWorkstationRecipePage,
    MultiBlockStructureModelPage,
    PageGroup,
    TextPage,
    UnfinishedItemName,
)

air_vent = PageGroup(
    "air_vent_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.AIR_VENT),
            "对于反应产生的副产物气体， 可通过排气口排放到环境中。\n\n"
            "将流体管道接到排气口的底座面， 该面只接收普通气体和二氧化碳。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.AIR_VENT),
    ],
)

chunk_anchor = PageGroup(
    "chunk_anchor_description",
    [
        TextPage(
            "区块锚",
            '区块锚可<text color="§2" t="常加载世界区块">， 使你不在产线附近时机器也能继续运转。'
            '\n常加载区域受游戏限制， 整个世界<text color="§d" t="最多同时保留 10 个常加载区域">， 与其他使用常加载区域的模组共用上限。\n'
            '\n\n区块锚<text color="§4" t="默认关闭">， 可在界面中调整加载范围以启动。 每区块消耗 50 RF/t。',
        ),
        MultiBlockStructureModelPage(CHUNK_ANCHOR, CHUNK_ANCHOR_SP),
        MachineryWorkstationRecipePage(CHUNK_ANCHOR),
    ],
)

deepslate_lava_vibrator = PageGroup(
    "deepslate_lava_vibrator_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.DEEPSLATE_LAVA_VIBRATOR),
            '深层熔岩谐振勘探器用于在建造<text color="§d" t="基岩熔岩钻">开采<text color="§4" t="深层熔岩">之前先行探明此地的深层熔岩储量。',
        ),
        TextPage(
            "",
            "将深层熔岩谐振勘探器放置到地面， 为其输入能量就可以启动探测。 勘探进度越多， 勘探到的深层熔岩储量也越准确。 勘探进度到达百分百后探测到的深层熔岩储量就几乎是百分百准确了。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.DEEPSLATE_LAVA_VIBRATOR),
    ],
)

effluent_outfall = PageGroup(
    "effluent_outfall_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.EFFLUENT_OUTFALL),
            "废液排放口可向大面积水体排放废液， 处理反应产生的部分废液。排放口本身必须浸在水中， 以排放口为中心的 3×5×3 范围内至少要有 27 格水， 包括排放口所在格。\n\n"
            '不同群系可处理的废液和排放速率见<link id="fluids" text="这里">。\n\n'
            '<text color="§7" t="但是我们还是希望你能回收部分废液， 这很环保主义。">',
            hyperlink_cbs={
                "fluids": lambda _: PushRecipeCheckerUI(EFFLUENT_OUTFALL_RECIPES)
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.EFFLUENT_OUTFALL),
    ],
)

hover_text_displayer = PageGroup(
    "hover_text_displayer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HOVER_TEXT_DISPLAYER),
            '悬浮文本投影器通过消耗能量来将<text color="§5" t="悬浮文本">投射到世界上， 类似 NPC 头顶的悬浮字效果。\n文本的长度和是否带颜色会影响最终功耗。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HOVER_TEXT_DISPLAYER),
    ],
)

industrial_fan = PageGroup(
    "industrial_fan_description",
    [
        TextPage(
            "工业风扇",
            '工业风扇可以消耗能量<text color="§9" t="吹飞面前的实体">。\n\n使用不同强度的<item id="minecraft:redstone"><text color="§4" t="红石信号">可控制<text color="§9" t="风扇功率">， 进而获得不同的鼓风范围与风力强度。 不提供红石信号时风扇<text color="§9" t="完全不工作">。\n\n风道会被实心方块<text color="§6" t="阻挡">， 只能吹动障碍前的实体。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.INDUSTRIAL_FAN),
    ],
)


lexical_transmuter = PageGroup(
    "lexical_transmuter_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.LEXICAL_TRANSMUTER),
            '矿词转换机使不同模组间相同物品名或 ID 的物品得以相互转换， 例如本模组和其他科技模组的锡锭。\n将目标物品放入模版物品槽（右上角）， 再将需要转换的物品放入输入槽（左下角）， 即可瞬间转换为目标物品。 整个过程<text color="§2" t="无需任何能量供应">。\n\n<text color="§c" t="不支持转换带 NBT 的物品， "> 如工具和武器类物品。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.LEXICAL_TRANSMUTER),
    ],
)

shocker = PageGroup(
    "shocker_description",
    [
        TextPage(
            "电击器",
            '将两台电击器尖端<text color="§3" t="面对面放置">， 可组成一对电击器， 此时可对生命值少于 40 的生物进行<text color="§4" t="昏死电击">， 使其无法自主行动， 但仍能被重力、 水流和传送带推动。\n\n两台电击器都需要供电， 可从各自后面或上面输入能量。 其中一台被红石激活时即可自动电击这对电击器放电尖端之间的生物。',
        ),
        TextPage(
            "",
            '一对电击器之间可以留出 1~3 格空间， 耗电倍率与距离成正比。 如果中间有实心方块， 两台电击器就<text color="§4" t="无法再进行配对">了。\n\n电击器目前不会电击玩家， 放心穿过两个电击器中间吧。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.SHOCKER),
    ],
)
