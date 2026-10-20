# UpgradeControl

[基类索引](README.md) · [生命周期](../lifecycle.md)

处理升级槽、速度和耗能倍率，并为产物输出接入自动输出功能。

直接继承：`SPControl, ItemContainer`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.UpgradeControl`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

upgrade_slot_start=2；upgrade_slots=4；allow_upgraders=frozenset()，元素是物品 ID，不是旧文档的 allow_upgrader_tags。

InUpgradeSlot(slot)、GetAllUpgraders()、UpdateUpgraders(upgraders)、HasUpgrader(item_id)、OutputItem(item)、FlushOutputSlots(slots)。

## 事件与组合

自动订阅物品放入及槽位更新。

覆写 UpdateUpgraders 时保留父实现；升级槽与物品产物槽不得重叠。Processor 已提供其默认允许升级列表。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[upgrade_control.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/upgrade_control.py)。
