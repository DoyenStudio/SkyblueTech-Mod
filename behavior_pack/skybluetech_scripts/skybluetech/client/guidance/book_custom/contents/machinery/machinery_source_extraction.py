# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

bedrock_lava_drill = PageGroup([
    TextPage(
        "alloy_furnace_description_1",
        "基岩熔岩钻",
        "基岩熔岩钻是一种§b多方块结构机器§r， 可以在基岩层处开采§4深层熔岩§r。 深层熔岩可以进一步被离心成几种熔岩， 进而被离心为熔融金属和其它成分。 它的钻头必须对准一块基岩。",
    ),
    TextPage(
        "alloy_furnace_description_2",
        "",
        "基岩熔岩钻需要先钻破顶层基岩才能把泵送管道送至深层熔岩层， 这意味着它在开始工作前至少需要安装一个§c耐热钻头§r到钻头槽位。\n\n钻头钻开顶层基岩层需要一定时间， §n消耗一定量耐久§r。 一旦其钻开了基岩层， 钻头的耐久就会被§2停止消耗§r， 基岩熔岩钻即开始泵出深层熔岩。",
    ),
    TextPage(
        "alloy_furnace_description_3",
        "",
        "每个区域的深层熔岩量是§n有限的§r， 你可以通过控制器界面查看该区域剩余熔岩储量。\n\n在安放机器前， 强烈推荐您先使用§d深层熔岩谐振探测器§r探明此地的大致熔岩储量再搭建好熔岩钻！",
    ),
    MachineryWorkstationRecipePage(
        "alloy_furnace_description_4", id_enum.BEDROCK_LAVA_DRILL_CONTROLLER
    ),
])

digger = PageGroup([
    TextPage(
        "digger_description_1",
        "电力挖掘钻",
        "电力挖掘钻可消耗能量挖掘其钻尖所指向的方块。\n\n建议从侧面输入能量， 背对钻头的一面提取物品。\n\n§8§o将两个面对面的钻头通电试试看？",
    ),
    MachineryWorkstationRecipePage("digger_description_2", id_enum.DIGGER),
])

farming_station = PageGroup([
    TextPage(
        "farming_station_description_1",
        "种植站",
        "种植站可§2自动收获并补种§r其上方 5x5 范围内耕地上的作物。\n支持我的世界原版及棱花农夫乐事的作物。",
    ),
    MachineryWorkstationRecipePage(
        "farming_station_description_2", id_enum.FARMING_STATION
    ),
])

forester = PageGroup([
    TextPage(
        "forester_description_1",
        "伐木机",
        "伐木机可以§2自动砍伐§r上方 5x5 范围内的树木且§2自动补种树苗§r。\n\n你可以在伐木机上方 5x1x5 的范围内填满泥土后种满树苗， 然后给伐木机通电以等待收成。",
    ),
    MachineryWorkstationRecipePage("forester_description_2", id_enum.FORESTER),
])

mini_miner = PageGroup([
    TextPage(
        "mini_miner_description_1",
        "迷你采矿机",
        "迷你采矿机是最简单的§3采矿机§r， 不需要搭建多方块结构，只需要输入能量和润滑油即可开始采矿。\n\n它可以对下方 §915x64x16§r 的范围进行采矿。 对应地， 它无法进行更高级的采矿设置， 如接受时运或精准采集设置。",
    ),
    TextPage(
        "mini_miner_description_2",
        "",
        "迷你采矿机只会采掘§8矿物和石头§r， 不会采掘泥土、 砂砾和其它方块。\n\n如果迷你采掘机被放置到了之前被采掘的区域， 会进行§6快进§r以快进到之前的采掘进度。",
    ),
    MachineryWorkstationRecipePage("mini_miner_description_2", id_enum.MINI_MINER),
])

pump = PageGroup([
    TextPage(
        "pump_description_1",
        "电动泵",
        "电动泵消耗能量§9抽取§r其下方的流体方块的流体源， 可以使用流体管道导出。\n\n泵会寻找 16 格以内的的§3流体源§r； 如果安装了§5强化： 范围扩增§r， 搜寻范围会变为原来的 4 倍！",
    ),
    MachineryWorkstationRecipePage("pump_description_2", id_enum.PUMP),
])
