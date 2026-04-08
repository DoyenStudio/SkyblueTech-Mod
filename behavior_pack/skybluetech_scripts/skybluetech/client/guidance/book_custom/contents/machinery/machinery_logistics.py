# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from ...define import (
    TextPage,
    MachineryWorkstationRecipePage,
    PageGroup,
)

fluid_splitter = PageGroup("fluid_splitter_description", [])

item_splitter = PageGroup(
    "item_splitter_description",
    [
        TextPage(
            "物品分拣器",
            '物品分拣器是根据给定设置对物品进行<text color="§2" t="分类">的机器。\n它可以将标记上了颜色序号的物品类型发送到<text color="§2" t="拥有相同颜色编号">的物品管道输入口中。',
        ),
        TextPage(
            "",
            '例如， 我们需要从物品中分出钻石： \n\n打开物品分拣器界面， 点击 + 按钮新增一个分类选项， 将其颜色标记设置为<text color="§b" t="天蓝色">， 再将选项右侧的物品选项设置为需要分类的物品（例如钻石）。 使用<text color="§3" t="物品管道">连接分拣器和容器（例如箱子）， 将管道与分拣器连接处（管道入口）设置为<text color="§c" t="抽取模式">；',
        ),
        TextPage(
            "",
            '手持<text color="§5" t="传输设置扳手">点击容器与物品管道的连接处（管道出口）打开<text color="§5" t="传输设置界面">， 将其颜色标记也设置为<text color="§b" t="天蓝色">。\n这时候向物品分拣器输入钻石， 它就会向箱子发送钻石。 但如果输入的物品不是钻石， 分拣器不会处理物品而是会将其存入自身的缓存槽内。',
        ),
        TextPage(
            "",
            '需要<text color="§2" t="将更多物品分类">时， 可以重复上述步骤， 使用<text color="§9" t="不同的颜色标记">区分不同物品， 将不同物品通过不同颜色标记的管道出口发送到不同的容器内。',
        ),
        TextPage(
            "",
            '如果你只需要从物品中<text color="§2" t="分离出部分物品">， 可以使用<text color="§3" t="特化升级： 泛用物品过滤">， 将其插入到分拣器的升级槽内， 可以将所有<text color="§c" t="未在分类设置中">的物品全部发送到<text color="§c" t="红色标记（默认颜色标记）">的物品管道输入口中。',
        ),
        MachineryWorkstationRecipePage(id_enum.ITEM_SPLITTER),
    ],
)
