# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

assembler = PageGroup(
    "assembler_description",
    [
        TextPage(
            "装配站",
            '装配站可以为蔚蓝科技系列的<text color="§9" t="工具和武器">安装额外的<text color="§2" t="强化和特化升级模块">， 使得工具和装备更强大好用。\n将道具放入上方的槽位， 再将模块放入下方槽位， 接着点击 + 按钮就可以将模块装载到道具上了。',
        ),
        MachineryWorkstationRecipePage(id_enum.ASSEMBLER),
    ],
)

machinery_workstation = PageGroup(
    "machinery_workstation_description",
    [
        TextPage(
            "机件加工台",
            '<text color="§5" t="绝大多数机器的制造">都需要在机件加工台进行完成。 \n\n将材料摆放在九宫格中， 再准备合适的<style color="§3"><link text="工具钳" id="pincer_craft">和<link text="工具扳手" id="wrench_craft">（统称为工具）<style color="R">放入右上角的工具槽中， 按下扳手图案的<text color="§2" t="制造按钮">增加制造进度。\n\n工具槽上方的<text color="§c" t="强度槽">表示加工强度。',
            hyperlink_cbs={
                "pincer_craft": lambda _: CheckRecipe(id_enum.Pincer.IRON),
                "wrench_craft": lambda _: CheckRecipe(id_enum.Wrench.IRON),
            },
        ),
        TextPage(
            "",
            '每按一次制造按钮都会<text color="§c" t="增加加工强度">， 加工强度会<text color="§2" t="随时间自然恢复">。 \n\n工具磨损概率和加工强度成正比， 请尽可能让加工强度不超过绿色范围。 一旦达到红色范围， 钳和扳手的磨损概率都会<text color="§4" t="大大增加">。 在工具耐久度和时间消耗间二选一吧。',
        ),
        TextPage(
            "",
            '更高阶的机械的制造需要更高等级的工具， 高等级的工具也能提供<text color="§2" t="更快">的制造速度。',
        ),
    ],
)
