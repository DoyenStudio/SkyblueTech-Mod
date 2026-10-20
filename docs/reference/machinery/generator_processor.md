# GeneratorProcessor

[基类索引](README.md) · [生命周期](../lifecycle.md)

按燃料配方持续产电，维护已启动配方及进度。

直接继承：`ProcessorBase, BaseGenerator`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.GeneratorProcessor`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

recipes 为 GeneratorRecipe 集合；energy_io_mode=(1,1,1,1,1,1)；allow_upgraders=frozenset()；dump_progress_to_block_entity_data=True。

recheck_recipe()；继承 SetOutputPower；generator_output_power 和 recipe_index 为已保存的配方运行信息。

## 事件与组合

自动订阅 tick、槽位及流体变化；BaseGenerator 的 tick 负责发电，本组件推进配方。

参考红石发电机；不要再写一份每 tick 发电。运行中的配方索引依赖集合顺序，勿在运行中重排/删改集合。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[generator_processor.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/generator_processor.py)。
