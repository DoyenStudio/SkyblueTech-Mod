# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from .define import TextPage, MainTOCPage, MainTOCPageSection, PageGroup

from . import contents


main_pages = PageGroup(
    "main",
    [
        TextPage(
            "蔚蓝科技",
            '蔚蓝空域精英计划¹；\n红石能专业必修教材²；\n红石能电路基础³\n\n本书将带您走进复杂、 高度自由的蔚蓝科技®红石能<item id="%s">世界， 教导您从如何使用<style color="§c">红石能<style color="R">到设计出复杂的工业生产线。\n\n加入玩家QQ群 <text color="§d" t="532685971"> 以讨论攻略、 获取最新更新消息！'
            % id_enum.REDSTONEFLUX_CORE,
            # '<opt name="line_spacing", val=8.0><style color="§2">你好！<style color="§4">你知道我们曾经是<link id="link1" text="一条超链接">。这是一个电动马达图标！<img path="textures/items/electric_motor">而这是一个草方块！<item id="minecraft:grass">这之后我们复原一下颜色：<style color="R">复原好了， 很有趣吧？<br><item id="minecraft:stick" scale=30><br><img path="textures/ui/warning_icon" x_scale=20 y_scale=10><img path="textures/ui/warning_icon" x_scale=10 y_scale=20>',
            # hyperlink_cbs={"link1": cb1}
        ),
        MainTOCPage(
            [
                MainTOCPageSection(
                    "minecraft:paper", 0, "引言", contents.intros.general_intro_pages
                ),
                MainTOCPageSection(
                    id_enum.Icons.SHEET,
                    0,
                    "基本概念",
                    contents.basic_concepts.basic_concepts_toc,
                ),
                MainTOCPageSection(
                    id_enum.MACHINERY_FRAME,
                    0,
                    "机器设备",
                    contents.machinery.machinery_toc,
                ),
            ],
        ),
    ],
)
