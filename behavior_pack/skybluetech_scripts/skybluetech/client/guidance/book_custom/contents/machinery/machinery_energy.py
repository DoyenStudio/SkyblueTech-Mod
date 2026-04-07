# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

battery_matrix = PageGroup([
    TextPage(
        "battery_matrix_description_1",
        "电池仓",
        "电池仓是一种§b多方块结构机器§r， 可以存入电池以用作§c存储能源§r。\n\n电池仓本身并没有储能容量， 它的储能能力完全由放置在其中的§5电池§r决定。",
    ),
    TextPage(
        "battery_matrix_description_2",
        "",
        "在电池仓控制器处可以存入或取出电池、 启用或禁用能量输入或输出功能。 \n\n电池仓所存放的电池§9最大输入输出功率总合§r决定电池仓的最大输入输出功率。",
    ),
    MachineryWorkstationRecipePage(
        "battery_matrix_description_3", id_enum.BATTERY_MATRIX_CONTROLLER
    ),
])

charger = PageGroup([
    TextPage(
        "charger_description_1",
        "充能台",
        "将需要充能的储能物品如§2电池§r和§9装备§r放入接入了电源的充能台内， 可以为其充能。 充能完成的道具会直接弹出到右边的输出槽中。\n\n储能装备需要充能后才可使用。",
    ),
    MachineryWorkstationRecipePage("charger_description_2", id_enum.CHARGER),
])

creative_power_acceptor = PageGroup([
    TextPage(
        "alloy_furnace_description_1",
        "虚空放电器",
        "§c§l本物品仅存于创造模式。§r\n虚空放电器会将输入的能量§4全部排入虚空§r， 同时也会显示实时输入功率。 你可以借此在创造模式下探查某个发电机的输出功率。 \n\n§4注意：§r 因为其具有无限的输入功率， 所以与其他机器并联接入电网时请调低虚空放电器的优先级， 以避免其他机器无法获得能源。",
    )
])


rf_repeater_plant = PageGroup([
    TextPage(
        "rf_repeater_plant_description_1",
        "能源中继塔",
        "要进行远距离传输能源， 能源中继塔是个不错的选择。\n\n能源中继塔可自动连接摆放在其基座旁边的能量线缆。",
    ),
    TextPage(
        "rf_repeater_plant_description_2",
        "",
        "要将两个能源中继塔进行连接， 只需要放置并打开能源中继塔的界面， 点击 [ §d拉线§r ] 按钮，走到另一台中继塔的旁边， 点击屏幕上的 [ §d完成 §r] 按钮即可。 两台相互连接的中继器的最大直线距离为 64 格。",
    ),
    TextPage(
        "rf_repeater_plant_description_3",
        "",
        "在中继塔界面内可以配置中继塔的能源输入输出模式， 即中继塔应该向基座的电缆供应还是接收能量。 \n\n即使能源中继网的一部分不在区块加载范围内， 只要网络的供能端和用电端都被加载， 电网就能正常工作。",
    ),
    MachineryWorkstationRecipePage(
        "rf_repeater_plant_description_2", id_enum.RF_REPEATER_PLANT
    ),
])
