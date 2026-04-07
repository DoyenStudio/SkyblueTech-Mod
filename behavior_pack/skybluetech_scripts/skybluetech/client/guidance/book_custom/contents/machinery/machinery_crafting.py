# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.guidance.book_custom.define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

assembler = PageGroup([
    TextPage(
        "assembler_description_1",
        "装配站",
        "装配站可以为蔚蓝科技系列的§9工具和武器§r安装额外的§2强化和特化升级模块§r， 使得工具和装备更强大好用。\n将道具放入上方的槽位， 再将模块放入下方槽位， 接着点击 + 按钮就可以将模块装载到道具上了。",
    ),
    MachineryWorkstationRecipePage("assembler_description_2", id_enum.ASSEMBLER),
])

machinery_workstation = PageGroup([
    TextPage(
        "machinery_workstation_description_1",
        "机件加工台",
        "§5绝大多数机器的制造§r都需要在机件加工台进行完成。 \n\n将材料摆放在九宫格中， 再准备合适的§3工具钳和工具扳手（统称为工具）§r放入右上角的工具槽中， 按下扳手图案的§2制造按钮§r增加制造进度。\n\n工具槽上方的§c强度槽§r表示加工强度。",
    ),
    TextPage(
        "machinery_workstation_description_2",
        "",
        "每按一次制造按钮都会§c增加加工强度§r， 加工强度会§2随时间自然恢复§r。 \n\n工具磨损概率和加工强度成正比， 请尽可能让加工强度不超过绿色范围。 一旦达到红色范围， 钳和扳手的磨损概率都会§4大大增加§r。 在工具耐久度和时间消耗间二选一吧。",
    ),
    TextPage(
        "machinery_workstation_description_3",
        "",
        "更高阶的机械的制造需要更高等级的工具， 高等级的工具也能提供§2更快§r的制造速度。",
    ),
    MachineryWorkstationRecipePage(
        "machinery_workstation_description_4", id_enum.MACHINERY_WORKSTATION
    ),
])
