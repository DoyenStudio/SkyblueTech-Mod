# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    Pincer,
    SkyblueTools,
    Wrench,
)
from .actions.register import RegisterTool

for _tool_id in SkyblueTools.all():
    RegisterTool(_tool_id)

# 充能工具钳/扳手同样按充能工具注册, 以便充电后自动从耗尽形态恢复
for _tool_id in (Pincer.SKYBLUE, Wrench.SKYBLUE):
    RegisterTool(_tool_id)
