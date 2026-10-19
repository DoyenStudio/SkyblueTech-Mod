# BaseMachine 基础机器基类

所有机器的基类，所有被注册的机器都需要继承它。

## 需要定义的类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| block_name | str | 机器方块的 ID |
| is_non_energy_machine | bool | 机器是否不涉及能源使用。设为 True 后将不会和线缆以及周围的能源机器产生能量交互，所有能量相关方法也不会生效 |
| energy_io_mode | tuple[int, int, int, int, int, int] | 六个面的能源输入输出模式。0: 输入；1: 输出；其它: 无模式 |
| store_rf_max | int | 机器最大可存储的能量值。 |

## 实例属性

| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| store_rf | (property) int | 机器当前存储的能量值 |
| dim | int | 机器所在的维度 |
| x | int | 机器 X 坐标 |
| y | int | 机器在 Y 方向上的坐标 |
| z | int | 机器在 Z 方向上的坐标 |
| bdata | BlockEntityData | 机器的方块实体信息实例 |


## 基类方法
```python
@classmethod
def AddExtraMachineId(cls, id: str)
```
为机器添加额外的方块 ID。
用于多个机器方块类型共用同一个机器类。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| id | str | 额外的机器 ID |

示例
```python
FluidOutputIO.AddExtraMachineId("custom:a_fluid_output")
FluidOutputIO.AddExtraMachineId("custom:b_fluid_output")
FluidOutputIO.AddExtraMachineId("custom:c_fluid_output")
```

---

```python
def AddPower(self, rf: int) -> tuple[bool, int]
```
为自身添加能量。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| rf | int | 能量 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, int] | 数值是否变动, 溢出的能量 |

---

```python
def ReducePower(self, rf: int) -> bool
```
减少自身能量。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| rf | int | 能量 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 数值是否变动 |

---

```python
def TakeoutPower(self, rf: int) -> int
```
从自身取出能量。

如果取出的能量在使用后发生了溢出，需要在同帧内调用 `GivebackPower` 返还溢出的能量。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| rf | int | 能量 |

| 返回类型 | 说明 |
| --- | --- |
| int | 实际取出的能量 |

---

```python
def GivebackPower(self, rf: int) -> None
```
返还从 `TakeoutPower` 取出的能量。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| rf | int | 返还的能量, 不应大于取走能量值 |

---

```python
def HasDeactiveFlag(self, flag: int) -> bool
```
是否拥有某一停机标志。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| flag | int | 标志位 |

| 返回值 | 说明 |
| --- | --- |
| bool | 是否拥有该标志位 |

示例
```python
from skybluetech_scripts.skybluetech.common.define import flags as rf_flags


class Machine(BaseMachine):
    ...

    def is_power_lack(self):
        return self.HasDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
```

---

```python
def SetDeactiveFlag(self, flag: int, flush: bool = True) -> None
```
设置机器的停机状态。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| flag | int | 标志位 |

---

```python
def UnsetDeactiveFlag(self, flag: int, flush: bool = True) -> None
```
取消机器的停机状态。

| 参数 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| flag | int | 标志位 | |
| flush | bool | 是否刷新停机标志 | True |

---

```python
def IsActive(self) -> bool
```
机器是否处于工作状态。

| 返回值 | 说明 |
| --- | --- |
| bool | 如题 |

---

```python
def IsActiveIgnoreCondition(self, cond: int) -> bool
```
机器在排除某种停机标志的情况下是否还能工作。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| cond | int | 一个或多个停机标志 |

| 返回值 | 说明 |
| --- | --- |
| bool | 如题 |

---

```python
def ResetDeactiveFlags(self) -> None
```
重置所有停机标志, 即将机器设置为工作模式。
不要随意使用，除非你确定机器已经没有任何停机可能， 完全可以转变为工作状态。

## 放置前检查

`OnPrePlaced` 保留为类方法, 在机器实例创建前调用, 可以取消放置。

```python
@classmethod
def OnPrePlaced(cls, event):
    pass
```

## 实例事件订阅

所有机器组件最终继承 `BaseMachine`, 由它创建唯一的 `MachineEventDispatcher` 实例,
保存在 `self.handler` 中。
构造器调用 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)` 后,
完成自身字段初始化, 再通过 `self.handler.SubscribeOnXXX(self.callback)` 订阅事件。
不再使用 `@SuperExecutorMeta.execute_super` 或重声明空方法。

| 订阅方法 | 回调参数 |
| --- | --- |
| `SubscribeOnPlaced` | `event` |
| `SubscribeOnTicking` | 无 |
| `SubscribeOnUnload` | 无 |
| `SubscribeOnDestroy` | 无 |
| `SubscribeOnNeighborChanged` | `event` |
| `SubscribeOnBlockRedstoneStrengthChanged` | `event` |
| `SubscribeOnBlockRandomTick` | `event` |
| `SubscribeOnSetDeactiveFlag` | `flag, flush` |
| `SubscribeOnUnsetDeactiveFlag` | `flag, flush` |
| `SubscribeOnDeactiveFlagsChanged` | `flush` |
| `SubscribeOnInvalidateCaches` | 无 |

`SetDeactiveFlag(flag, flush=True)` 和 `UnsetDeactiveFlag(flag, flush=True)` 先更新标志,
再派发对应操作事件和状态通知。`flush=False` 仍处理停机逻辑, 但跳过工作外观刷新;
需要刷新时调用 `FlushDeactiveFlags()`。重置标志也会派发状态通知。

缓存失效回调只打脏标记或清空缓存, 实际重建留到下一 tick 惰性完成。
不要在回调中同步读取正在拆建的管网或触发其他系统的副作用。

对于替换父组件行为的分支, 显式取消对应订阅后注册自己的回调。
`MachineEventDispatcher.Unsubscribe(topic_name, callback)` 提供通用取消接口;
tick、槽位及点击事件还提供 `UnsubscribeOnTicking`、`UnsubscribeOnSlotUpdate` 和 `UnsubscribeOnClick`。

`IsValidInput` / `IsValidFluidInput` 保持同步返回布尔值。按组件职责收集父类约束和本机判定后做 `all(results)`;
组件对不属于自己职责的槽位保持中立, 防止普通输入槽与升级槽相互否决。

## 框架模块分工

- `basic/` 只放机器基类和可继承的组件基类。
- `core/event_dispatcher.py` 定义实例事件分发器及事件常量。
- `core/registry.py` 提供 `RegisterMachine`、`GetMachineCls` 和 `TryGetMachineCls`, 管理方块 ID 到机器类的映射。
- `core/pool.py` 管理机器实例的创建、查询、移除及缓存失效。`GetLoadedMachine` 只查询已有实例;
  `GetMachineWithoutCls` 可在缓存缺失时创建实例; `LoadMachine` 用于从方块实体数据创建并登记实例, 会替换原位置缓存。
- `listeners/event_listener.py` 接收游戏事件, 包括区块加载与卸载, 再调用实例池及机器的事件分发器。

注册装饰器从 `core` 或 `core.registry` 导入。`core` 不主动导入监听模块;
`machinery/__init__.py` 在所有具体机器、接口和储罐导入完成后统一导入 `listeners`, 注册游戏事件监听。
