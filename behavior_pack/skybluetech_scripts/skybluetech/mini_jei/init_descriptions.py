# coding=utf-8
from ..define.id_enum import *
from .core import CategoryType, RegisterDescription

# RegisterDescription(
#     {CategoryType.FLUID: [RAW_OIL]},
#     "原油获取",
#     "你可以在地下、 海上或矿洞里找到天然油井或者油田。 \n油田里的油是有限的， 可以供你装桶以便临时之需。\n油井可以提取的原油储量几乎可以认为是无限的， 你可以在油井旁就地建立一个炼油产线以提取各种油料产物。"
# )

RegisterDescription(
    {CategoryType.ITEM: ["skybluetech:description_icon"]},
    "关于介绍的介绍？！",
    "这是一个介绍， 它并没有“获取途径”， 但是你却可以通过查看介绍的介绍来获取介绍的介绍。 是不是很有趣？"
)
