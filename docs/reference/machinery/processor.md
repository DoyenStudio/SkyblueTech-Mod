# Processor

[基类索引](README.md) · [生命周期](../lifecycle.md)

消耗电力和输入，按时长产出物品/流体的标准机器。

直接继承：`ProcessorBase`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.Processor`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

recipes 为 MachineRecipe 集合；process_item/process_fluid 按实际输入输出开启；dump_progress_to_block_entity_data=True；配置物品/升级槽和储能。

recheck_recipe() 重新匹配；GetProgressPercent() 获取当前配方进度；配方切换使用已有处理流程，不自行复制 start_next 逻辑。

## 事件与组合

自动订阅 tick、物品槽、流体增加与减少；处理输出满和无配方等停机恢复。

磨粉机使用 Processor；熔岩炉用 (Processor, MultiFluidContainer)。流体组件放在 Processor 后，构造时流体槽要先于配方检查就绪。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[processor.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/processor.py)。
