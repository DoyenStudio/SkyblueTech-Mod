# coding=utf-8
#
"""
SkyblueTech Mod | 蔚蓝科技
交流群:   532685971
作者:     SuperScript
联动请找: SuperScript
问题反馈: https://github.com/SuperScript-PRC/SkyblueTech-Mod/issues
"""

from .tooldelta.mod_main import ToolDeltaMod, RegisterMod
from . import entry


@RegisterMod()
class SkyblueTech(ToolDeltaMod):
    name = "SkyblueTech"
    version = (1, 0, 0)


