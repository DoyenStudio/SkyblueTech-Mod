# BaseClicker

[基类索引](README.md) · [生命周期](../lifecycle.md)

非自定义容器的可点击机器，统一限流并拦截点击放置。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.BaseClicker`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

onclick_delay=0.25，单位秒；其余沿用 BaseMachine。

通过 handler.SubscribeOnClick(callback) 接收 event, extra_datas=None。

## 事件与组合

引擎机器监听器调用 _can_click 后分发，潜行交互另有处理。

计数器、无容器控制器可用；有原生自定义容器的配方机通常使用 GUIControl。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[base_clicker.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/base_clicker.py)。
