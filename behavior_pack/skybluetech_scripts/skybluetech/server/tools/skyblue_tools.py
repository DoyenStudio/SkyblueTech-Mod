# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import SkyblueTools
from .actions.register import RegisterTool

for _tool_id in SkyblueTools.all():
    RegisterTool(_tool_id)
