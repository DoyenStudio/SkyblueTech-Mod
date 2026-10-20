# BaseGenerator

[基类索引](README.md) · [生命周期](../lifecycle.md)

持续发电的组件，每 tick 在活动状态按当前输出功率发电。

直接继承：`BasePowerProvider`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.BaseGenerator`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

output_power 初始 0；必须声明 energy_io_mode 输出面；store_rf_max 控制储能。

SetOutputPower(power) 设置 RF/t；继承 GeneratePower、PowerFull。注意不是 SetPower。

## 事件与组合

自动订阅 tick；停机且仍有储能时尝试输出邻接机器。

太阳能等连续发电采用本类；燃料配方用 GeneratorProcessor。不要自行重复调用 GeneratePower 导致双倍发电。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[base_generator.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/base_generator.py)。
