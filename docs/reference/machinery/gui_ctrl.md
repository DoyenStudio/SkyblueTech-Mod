# GUIControl

[基类索引](README.md) · [生命周期](../lifecycle.md)

机器点击打开 UI、维护 S2CSync 与卸载清理。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.GUIControl`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

bound_ui=None 表示原生自定义容器；独立界面指定注册 key。

CallSync() 分发 SubscribeOnSync；ui_sync 为服务器同步实例。

## 事件与组合

自动订阅点击与卸载；卸载时关闭绑定界面并停用同步。

原生容器由 JSON screen_name 打开，客户端注册相应 proxy；不要把 bound_ui 同时当成原生 screen_name。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[gui_ctrl.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/gui_ctrl.py)。
