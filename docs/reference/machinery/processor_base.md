# ProcessorBase

[基类索引](README.md) · [生命周期](../lifecycle.md)

共享的配方匹配、输出检查和 GUI 进度基础，用于实现不同处理协议。

直接继承：`WorkRenderer, UpgradeControl, GUIControl`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.ProcessorBase`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

process_item=False；process_fluid=False；recipes 必须换成附属的唯一 RecipesCollection。

get_recipe() 返回 (索引, 配方或 None)；can_output(recipe) 检查输出；IsValidFluidInput(slot,fluid_id) 联合配方过滤。

## 事件与组合

继承组合组件订阅；构造时匹配已有输入并设置或清除无配方停机标志。

本类不是完整的周期处理器。通常使用 Processor 或 GeneratorProcessor。旧名称 ProcessBase 不存在。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[processor_base.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/processor_base.py)。
