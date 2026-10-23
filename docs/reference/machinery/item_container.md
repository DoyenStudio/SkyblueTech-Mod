# ItemContainer

[基类索引](README.md) · [生命周期](../lifecycle.md)

访问自定义物品容器及输入输出槽，参与玩家放入校验。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.ItemContainer`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

item_input_slots=()；item_output_slots=()；槽号必须与 JSON 容器大小、UI collection_index 一致。

GetSlotItem(slot_pos)、SetSlotItem(slot_pos,item)、GetInputSlotItems()、GetOutputSlotItems()、DropAllItems()、IsValidInput(slot,item)。

## 事件与组合

自动订阅 SubscribeOnCustomCotainerPutItem（名称沿用现有 API 拼写）。

SetSlotItemCount 的原 API 对自定义容器有已知问题，应使用项目已有设置物品方式。继承容器不等于创建 JSON 容器。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[item_container.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/item_container.py)。
