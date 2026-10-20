# OperationListener

[基类索引](README.md) · [生命周期](../lifecycle.md)

将自定义客户端操作事件路由到对应机器实例。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.OperationListener`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

事件类继承 MachineryOperationC2S；用唯一事件名和 extra_attrs 声明额外字段。

@MachineClass.ForOperation(EventClass) 装饰 callback(event,machine)，从玩家所在维度和事件坐标查找机器。

## 事件与组合

装饰器注册服务端通信监听，检查机器类型、禁用状态和多方块是否完成。

业务回调仍须校验参数和操作许可；事件坐标来自客户端，不应当作任意远程操作授权。组合 GUIControl 可检查 ui_sync.PlayerInSync。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[operation_listener.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/operation_listener.py)。
