# BasePowerProvider

[基类索引](README.md) · [生命周期](../lifecycle.md)

一次性产生电力，管理直接供给邻接机器和自身缓冲。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.BasePowerProvider`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

store_rf_max；energy_io_mode 中 1 表示输出面，构造时缓存输出方向。

GeneratePower(rf) 返回 (是否供能, 溢出量)；PowerFull() 判断缓冲已满。

## 事件与组合

自动订阅缓存失效以清理邻机引用；不自行周期发电。

需要处理溢出时用本类。自行订阅 tick，在明确条件下调用 GeneratePower；不要忽略溢出而声称能量守恒。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[base_power_provider.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/base_power_provider.py)。
