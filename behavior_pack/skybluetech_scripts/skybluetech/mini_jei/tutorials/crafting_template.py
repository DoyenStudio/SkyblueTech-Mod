from ...define.id_enum.items import CRAFTING_TEMPLATE
from ...define.id_enum.machinery import ELECTRIC_CRAFTER
from ..core import CategoryType, RegisterDescription

content = (
    "自动合成台需要使用合成样板以设置合成配方。 "
    "打开设置界面后， 点击槽位， 在弹出的界面选择合成所需物品。 "
    "当配方被正确摆放之后， 输出槽将会显示合成结果。"
    "\n"
    "设置完合成配方之后， 将合成样板放入自动合成台合成进度箭头下面的模版槽内， "
    "就可以手动放入或使用物品管道给自动合成台提供原料， "
    "使其进入工作状态。"
    "\n"
    "自动合成台可以智能过滤掉非原料物品、 自动均摊原料。"
)

RegisterDescription(
    {CategoryType.ITEM: [CRAFTING_TEMPLATE, ELECTRIC_CRAFTER]},
    "自动合成台与合成样板",
    content.strip()
)