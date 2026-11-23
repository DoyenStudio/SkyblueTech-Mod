# coding=utf-8
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
)
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.common.machinery_def.battery_matrix import (
    STRUCTURE_PALETTE,
)

from ...define import (
    MachineryWorkstationRecipePage,
    MultiBlockStructureModelPage,
    PageGroup,
    TextPage,
    UnfinishedItemName,
)

battery_matrix = PageGroup(
    "battery_matrix_description",
    [
        TextPage(
            "电池仓",
            '电池仓是一种<text color="§b" t="多方块结构机器">， 可以存入电池以用作<text color="§c" t="存储能源">。 使用<link id="scepter" text="多方块结构手杖">可快速建造。\n\n'
            '电池仓本身并没有储能容量， 它的储能能力完全由放置在其中的<text color="§5" t="电池">决定。\n\n'
            "搭建时须在中央放置储能核心， 并至少各装一个能量输入口和能量输出口。"
            '电池仓可通过<text color="§c" t="多个输入输出口">同时进行能量输入或输出。',
            hyperlink_cbs={
                "scepter": lambda _: CheckRecipe(id_enum.MULTIBLOCK_STRUCTURE_SCEPTER)
            },
        ),
        TextPage(
            "",
            '在电池仓控制器处可以存入或取出电池、 启用或禁用能量输入或输出功能。 \n\n电池仓所存放的电池<text color="§9" t="最大输入输出功率总合">决定电池仓的最大输入输出功率。',
        ),
        MultiBlockStructureModelPage(
            id_enum.Machinery.BATTERY_MATRIX_CONTROLLER, STRUCTURE_PALETTE
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.BATTERY_MATRIX_CONTROLLER),
    ],
)

charger = PageGroup(
    "charger_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.CHARGER),
            '将需要充能的储能物品如<text color="§2" t="电池">和<text color="§9" t="装备">放入接入了电源的充能台内， 可以为其充能。 充能完成的道具会直接弹出到右边的输出槽中。\n\n储能装备需要充能后才可使用。'
            "\n\n充能台可以将惰性红石还原为红石粉， 也可以将惰性红石块还原为红石块。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.CHARGER),
    ],
)

creative_power_acceptor = PageGroup(
    "creative_power_acceptor_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.CREATIVE_POWER_ACCEPTOR),
            '<text color="§c" t="本物品仅存于创造模式。">\n虚空放电器会将输入的能量<text color="§4" t="全部排入虚空">， 同时也会显示实时输入功率。 你可以借此在创造模式下探查某个发电机的输出功率。 \n\n<text color="§4" t="注意："> 因为其具有无限的输入功率， 所以与其他机器并联接入电网时请调低虚空放电器的优先级， 以避免其他机器无法获得能源。',
        )
    ],
)


energy_cube_junior = PageGroup(
    "energy_cube_junior_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ENERGY_CUBE_JUNIOR),
            "能量立方可用作单方块简易储能装置， 也可以用于转接不同的能量线缆。\n\n"
            "默认从顶面输入能量， 其余五面输出。 在界面中可逐面切换输入或输出。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ENERGY_CUBE_JUNIOR),
    ],
)

redstoneflux_brake = PageGroup(
    "redstoneflux_brake_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.REDSTONEFLUX_BRAKE),
            '能源控制闸可以查看<text color="§9" t="所有">邻接电网的平均功率或使用<item id="minecraft:redstone"><text color="§4" t="红石信号">控制电它们的启停。'
            "\n可在界面内设置红石信号的控制模式。"
            '\n\n能源控制闸控制电网的方式是与其他普通用电器一样并联入网， <text color="§c" t="不要尝试将其串联到电缆线路上">。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.REDSTONEFLUX_BRAKE),
    ],
)

rf_repeater_plant = PageGroup(
    "rf_repeater_plant_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.RF_REPEATER_PLANT),
            "要进行远距离传输能源， 能源中继塔是个不错的选择。\n\n能源中继塔可自动连接摆放在其基座旁边的能量线缆。",
        ),
        TextPage(
            "",
            '要将两个能源中继塔进行连接， 只需要放置并打开能源中继塔的界面， 点击 [ <text color="§d" t="拉线"> ] 按钮， 走到另一台中继塔的旁边， 点击屏幕上的 [ <text color="§d" t="完成 ">] 按钮即可。 两台相互连接的中继器的最大直线距离为 64 格。',
        ),
        TextPage(
            "",
            "在中继塔界面内可以配置中继塔的能源输入输出模式， 即中继塔应该向基座的电缆供应还是接收能量。 \n\n即使能源中继网的一部分不在区块加载范围内， 只要网络的供能端和用电端都被加载， 电网就能正常工作。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.RF_REPEATER_PLANT),
    ],
)

tesla_plant = PageGroup(
    "tesla_plant_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.TESLA_PLANT),
            '<text color="§c" t="特斯拉电塔属于实验性机器。">\n特斯拉电塔可以消耗能量并按指定设置通过电击<text color="§4" t="攻击">生物或玩家。\n'
            "电塔可以在能源充足的情况下一次性攻击多个目标。 攻击目标越远， 耗能越高。\n\n"
            "放置时在基座上方留出两格， 将电源接到基座。 电塔默认只攻击怪物， 可在界面调整目标和范围。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.TESLA_PLANT),
    ],
)
