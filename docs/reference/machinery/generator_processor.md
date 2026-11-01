# GeneratorProcessor

[基类索引](README.md) · [生命周期](../lifecycle.md)

按燃料配方持续产电，维护已启动配方及进度。

直接继承：`ProcessorBase, BaseGenerator`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.GeneratorProcessor`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

recipes 为 GeneratorRecipe 集合；energy_io_mode=(1,1,1,1,1,1)；allow_upgraders=frozenset()；dump_progress_to_block_entity_data=True。

recheck_recipe()；继承 SetOutputPower；generator_output_power 和 recipe_index 为已保存的配方运行信息。

## 事件与组合

自动订阅 tick、槽位及流体变化；取消 BaseGenerator 的独立发电订阅，在同一个 tick 回调里推进进度并结算对应发电量。批次完成的当帧立即交付产物，不额外增加一帧发电；停机时仍可向邻居输出已储存的能量。

开工扣除材料后保留 recipe_index；任何停机原因都不重置这批已扣料配方的剩余进度。重载恢复剩余 ticks，0 表示已完成待交付；输出阻塞解除后仅补交产物。恢复和解堵只清除配方自身的停机标志，不清除满电等其他停机原因。

本批已发出的整数 RF 单独保存为包含两个 31 位 `int` 的原生字典，每次更新重新赋值，避免 NBT 丢失 `long`。恢复后以该计数结算后续差额，不从经过 float32 量化的剩余 ticks 反推此前发电量。已有开发存档缺少这个计数时，仅首次按剩余进度估算；过去实际发出的电量无法追溯修正。

参考红石发电机；不要再写一份每 tick 发电。运行中的配方索引依赖集合顺序，勿在运行中重排/删改集合。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[generator_processor.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/generator_processor.py)。
