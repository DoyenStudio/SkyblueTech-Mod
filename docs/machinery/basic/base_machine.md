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
def SetDeactiveFlag(self, flag: int) -> None
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

## 基类覆写方法
```python
@classmethod
def OnPrePlaced(cls, event: ServerEntityTryPlaceBlockEvent)
```
可被覆写，在机器被放置之前调用，可在这时候对事件进行 `cancel()`。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| event | ServerEntityTryPlaceBlockEvent | 放置事件 |

---

```python
def OnPlaced(self, event: ServerPlaceBlockEntityEvent)
```
可被覆写，机器被放置后调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| event | ServerPlaceBlockEntityEvent | 放置事件 |

---

```python
def OnTicking(self)
```
可被覆写，方块实体 tick 调用。

---

```python
def OnUnload(self)
```
可被覆写，方块实体被卸载时调用。

---

```python
def OnDestroy(self)
```
可被覆写，方块被破坏时调用。

---

```python
def OnNeighborChanged(self, event: BlockNeighborChangedServerEvent)
```
可被覆写，邻近方块变化时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| event | BlockNeighborChangedServerEvent | 邻近方块变化事件 |

---

```python
def OnDeactiveFlagsChanged(self)
```
可被覆写，机器激活状态更改时调用。

---

```python
def OnInvalidateCaches(self)
```
可被覆写，机器缓存的按位置 / 邻居 / 管网推导出的数据失效时调用。

子类若缓存了这类数据，应重写此方法，并在其中**只打脏标记或清空缓存**，实际重建留到下一 tick 惰性完成。
不要在钩子里同步读取管网数据或触发其他系统的副作用 —— 它可能在管网拆到一半时被调用。

触发时机：邻近方块变化、邻居方块放置 / 移除、区块装卸，以及管网网络重建或接入点设置变化。
