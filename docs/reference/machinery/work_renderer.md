# WorkRenderer

[基类索引](README.md) · [生命周期](../lifecycle.md)

将停机状态映射到方块工作外观。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.WorkRenderer`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

方块 JSON 必须定义 skybluetech:active 布尔状态。

通过 BaseMachine 的停机标志 API 驱动；handler.SubscribeOnWorkStatusUpdated 可监听外观更新。

## 事件与组合

自动订阅停机状态变化，只在工作状态改变且 flush=True 时更新方块状态。

Processor 已包含本组件。自定义机器若需要工作纹理，可与其他组件组合；外观状态不代替业务开关。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[work_renderer.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/work_renderer.py)。
