# BaseSpeedControl

[基类索引](README.md) · [生命周期](../lifecycle.md)

独立的进度与速度控制，不自动耗电或产物。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.BaseSpeedControl`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

origin_process_ticks=20；dump_progress_to_block_entity_data=False；reduce_ticks 初始化为 1。

SetSpeedRelative(speed)、SetProcessTicks(ticks)、ProcessOnce()、GetProcessProgress()、ResetProgress()。

## 事件与组合

订阅设置停机标志；按 PROGRESS_PRESERVING_FLAGS 决定保留还是重置进度。

ProcessOnce 返回 True 才完成一次；调用方决定调度。ticks_left 写入 bdata，UI 进度导出由开关控制。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[base_speed_control.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/base_speed_control.py)。
