# 机器生命周期与事件

[基类索引](machinery/README.md) · [第一台机器](../tutorials/02-first-machine.md)

注册类与加载实例是两件事。`RegisterMachine` 记录方块 ID 到类的映射；主模组机器监听器在放置、区块加载等事件中创建实例，tick 时查询已加载实例并分发 `handler` 回调。只写类而漏掉导入链，类不会注册。

```python
def __init__(self, dim, x, y, z, block_entity_data):
    super(MyMachine, self).__init__(dim, x, y, z, block_entity_data)
    self.handler.SubscribeOnTicking(self.my_tick)
    self.handler.SubscribeOnUnload(self.my_unload)

def my_tick(self):
    pass

def my_unload(self):
    pass
```

自定义组件的构造器使用一次 `super(当前类, self).__init__(...)`，不要逐个调用父构造器。回调取组件专属名称，避免覆写同名方法意外替换其他组件订阅。已由父类注册的 tick 不要重复订阅。

| 订阅 | 回调参数 | 时机/用途 |
| --- | --- | --- |
| `SubscribeOnPlaced` | `event` | 新放置通知，不等于每次构造 |
| `SubscribeOnTicking` | 无 | 方块实体 tick，JSON 需要 `tick: true` |
| `SubscribeOnUnload` / `SubscribeOnDestroy` | 无 | 区块/实例卸载与破坏，不应混同 |
| `SubscribeOnClick` | `event, extra_datas=None` | 机器点击；非容器通常组合 BaseClicker |
| `SubscribeOnSlotUpdate` | `slot_pos` | 物品槽变化 |
| `SubscribeOnAddedFluid` / `SubscribeOnReducedFluid` | `slot, fluid_id, volume, is_final` | 流体变化已发生 |
| `SubscribeOnFluidSlotUpdate` | `slot_pos, is_final` | 本次流体槽更新 |
| `SubscribeOnSync` | 无 | `GUIControl.CallSync()` 分发同步 |
| `SubscribeOnDeactiveFlagsChanged` | `flush=True` | 停机标志变化 |
| `SubscribeOnInvalidateCaches` | 无 | 邻接/网络缓存失效 |
| `SubscribeOnStructureChanged` | `structure_finished` | 多方块检测结果变化 |
| `SubscribeOnWorkStatusUpdated` | 无 | 外观工作状态改变 |
| `SubscribeOnHeatWork` | 无 | 热处理周期 |

`Processor` 已组合外观、升级、速度、能量、物品容器和 GUI。物品转流体使用 `class Melter(Processor, MultiFluidContainer)`，保证协作式初始化在配方检查前完成流体槽创建。发电配方使用 `GeneratorProcessor`，持续发电才使用 `BaseGenerator`。

源码：[事件分发器](../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/core/event_dispatcher.py)、[引擎监听器](../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/listeners/event_listener.py)。
