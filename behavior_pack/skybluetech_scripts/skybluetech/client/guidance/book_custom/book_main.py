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
                    "minecraft:crafting_table",
                    0,
                    "内置 JEI",
                    contents.mini_jei.mini_jei_desc,
                ),
                MainTOCPageSection(
                    id_enum.ALLOY_FURNACE,
                    0,
                    "机器设备",
                    contents.machinery.machinery_toc,
                ),
                MainTOCPageSection(
                    id_enum.REDSTONEFLUX_CORE,
                    0,
                    "能源",
                    contents.energy.energy_toc,
                ),
            ],
        ),
    ],
)
