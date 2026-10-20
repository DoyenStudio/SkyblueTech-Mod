# SPControl

[基类索引](README.md) · [生命周期](../lifecycle.md)

把耗电检查与进度推进合并。

直接继承：`PowerControl, BaseSpeedControl`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.SPControl`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

继承 running_power、origin_process_ticks、dump_progress_to_block_entity_data。

ProcessOnce() 先 PowerEnough，再 ReducePower，再推进进度；返回是否完成一次。

## 事件与组合

继承速度组件的停机订阅，不自行订阅 tick。

自定义非标准配方流程可用；标准输入输出机器优先 Processor。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[sp_control.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/sp_control.py)。
