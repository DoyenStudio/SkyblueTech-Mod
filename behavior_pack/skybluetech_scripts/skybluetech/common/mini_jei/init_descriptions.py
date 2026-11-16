# coding=utf-8
from ...common.define import id_enum
from ...common.define import tag_enum
from .core import CategoryType
from .common import RegisterSourceDescription, RegisterUsageDescription
from ..misc.inscriber_press import EMPTY

RegisterUsageDescription(
    {CategoryType.ITEM: [EMPTY]},
    "空压印模板的用途",
    (
        "手持并使用空压印模板，打开雕刻界面。 长按一格铁块即可将该格雕刻掉。"
        "\n在配方查看界面中， 黑灰闪烁的格子需要雕掉， 保留白色格子。"
        "\n雕刻进度自动保存在模板中， 下次打开可继续； 已雕掉的格子§4无法恢复§r， 这也就意味着你必须专注于雕刻， 雕错了会让压印模板§4直接报废§r。"
        "\n图案完全匹配对应的雕刻形状时， 空模板会自动变成对应的压印模板。\n你可以在左边选择“压印模板”配方分组查看所有§2有效的§r雕刻形状。"
    ),
)

RegisterSourceDescription(
    {CategoryType.ITEM: [id_enum.Machinery.AIR_VENT]},
    "排气口",
    "支持六面向放置，仅底座面接受管道输入 CommonGas 分组的普通气体。\n单槽容量 400 mB，不能混装气体；以 20 mB/t 排气，每 5 tick 消耗最多 100 mB，余量不足时排空。\n无需能量或红石，无操作界面，不支持桶、试管交互和流体输出。排气烟雾使用所排气体的贴图。",
)

# RegisterSourceDescription(
#     {CategoryType.FLUID: [RAW_OIL]},
#     "原油获取",
#     "你可以在地下、 海上或矿洞里找到天然油井或者油田。 \n油田里的油是有限的， 可以供你装桶以便临时之需。\n油井可以提取的原油储量几乎可以认为是无限的， 你可以在油井旁就地建立一个炼油产线以提取各种油料产物。"
# )

RegisterSourceDescription(
    {CategoryType.ITEM: ["skybluetech:description_icon"]},
    "关于介绍的介绍？！",
    "这是一个介绍， 它并没有“获取途径”， 但是你却可以通过查看介绍的介绍来获取介绍的介绍。 是不是很有趣？\n\n噢不， 为什么在座各位都被冻住了？",
)

RegisterSourceDescription(
    {CategoryType.ITEM: [id_enum.INSCRIBING_TEMPLATE]},
    "刻印模版",
    (
        "刻印模版可以放入§d模版成型机§r里为机器或者道具制作升级模块。"
        # "\n对于工业研究里没有的升级模块， 你可以在一些遗迹的藏宝箱里找到刻录有正确电路格式的刻印模版。"
        "\n§c注意！§r不要修改已刻录好正确格式的刻印模版， 如果你不知道怎么将模版图改回正确的格式， 它就没办法再拿去按模版制造对应物品了。"
    ),
)

RegisterUsageDescription(
    {CategoryType.ITEM: [id_enum.Machinery.INDUSTRIAL_FAN]},
    "工业风扇",
    "储存 8800 RF，仅背面输入能量，无操作界面。\n红石 0 级停机，1～15 级对应 1～15 格/秒风速、10～150 RF/t 功耗，叶片转速从 1 倍线性增加至 5 倍。\n正面 1×1 格风道内的生物、玩家和掉落物会沿朝向吹动；射程随信号从 10 格线性增加至 20 格。实心方块会阻挡风道，只能吹动障碍前的实体。能量不足时停机。",
)

RegisterSourceDescription(
    {CategoryType.ITEM: [id_enum.TransmitBelt.DETECTOR]},
    "感应传送带",
    "沿放置朝向输送生物和掉落物，无需能量。\n生物或玩家站在带上时输出 15 级红石信号，全部离开后信号归零；掉落物和盔甲架不会触发感应。",
)

RegisterSourceDescription(
    {CategoryType.ITEM: [id_enum.Machinery.SHOCKER]},
    "电击器",
    "支持六向放置，无操作界面；每台储存 16000 RF，仅相对背面和顶部输入能量，遇水流会被摧毁。\n两台正面相对、中间间隔 1～3 格且没有实心方块时配对。任一端收到红石上升沿时电击区域内生物；红石导通期间也会电击新进入的生物。\n仅电击当前生命值低于 40 的生物，使其永久失去自主移动和攻击能力，仍可被传送带等外力推动。每个目标消耗 100 × 当前生命值 × 间隔格数 RF，双方各承担一半且都必须充足。缺电时仅产生微弱电火花并造成一次 0 点伤害；留在区域内不会因补电自动重试。",
)

RegisterSourceDescription(
    {CategoryType.FLUID: [id_enum.DeepLava.DEEPSLATE_LAVA]},
    "深层熔岩",
    (
        "深层熔岩是基岩层下储量相当丰富的、 富含矿物质的熔岩热流体资源。"
        "\n使用恰当的离心手段就可以将矿物资源以熔融的形式从熔岩中分离出来。"
        "\n\n使用§9基岩熔岩钻§r可以在基岩层采掘深层熔岩。"
    ),
)
