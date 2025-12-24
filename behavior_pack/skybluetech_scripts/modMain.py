# coding=utf-8
#
"""
SkyblueTech Mod | 蔚蓝科技
交流群:   532685971
作者:     SuperScript
联动请找: SuperScript
开源地址(别解包了! 来仓库看完整的含类型注释的源代码!): https://github.com/SuperScript-PRC/SkyblueTech-Mod
问题反馈: https://github.com/SuperScript-PRC/SkyblueTech-Mod/issues

开放式 API: skybluetech_scripts.skybluetech.export
"""

from .tooldelta.mod_main import ToolDeltaMod, RegisterMod
from . import entry


@RegisterMod()
class SkyblueTech(ToolDeltaMod):
    name = "SkyblueTech"
    version = (1, 0, 0)


