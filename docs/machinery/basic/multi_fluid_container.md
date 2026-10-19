# MultiFluidContainer 多流体容器基类

可存储多种流体的机器基类。

与物品槽类似，流体容器的流体槽也依靠数字 ID 区分槽位。
流体槽 ID 需要从 0 开始连续递增。

基类会在构造时直接向 `self.handler` 订阅所需事件, 无需重声明空方法。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluid_io_mode | tuple[int, int, int, int, int, int] | 每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无 |
| fluid_input_slots | set[int] | 可接受输入的流体槽位 |
| fluid_output_slots | set[int] | 可输出的流体槽位 |
| fluid_slot_max_volumes | tuple[int, ...] | 每个流体槽最多可存储流体容量 |
| allow_player_use_bucket_interact | bool | 是否允许玩家直接使用桶交互 |
| allow_player_use_bucket_push | bool | 是否允许玩家直接使用桶装填流体 |
| allow_player_use_bucket_pull | bool | 是否允许玩家直接使用桶取出流体 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluids | list\[FluidSlotServer] | 机器的流体槽位 |

**FluidSlotServer 定义**
| 属性名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| fluid_id | (property) str | 流体ID，`None`表示为空  | None |
| fluid_volume | (property) float | 流体体积 | 0.0 |
| max_volume | float | 流体槽最大容量 | 0.0 |


## 基类方法
```python
def IsValidFluidInput(self, slot: int, fluid_id: str) -> bool
```
判定某槽位是否可以输入指定流体。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot | int | 流体槽位 |
| fluid_id | str | 流体类型 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 如题 |

---

```python
def OutputFluid(self, fluid_id: str, fluid_volume: float, slot_pos: int, is_final: bool) -> tuple[bool, float]
```
在指定槽位中产出流体。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |
| slot_pos | int | 流体槽位 |
| is_final | bool | 是否为最后一个处理槽位 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否产出成功, 溢出的流体容量 |

---

```python
def AddFluid(self, fluid_id: str, fluid_volume: float) -> tuple[bool, float]
```
将流体输入到合适的输入槽位。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否添加成功, 剩余的流体容量 |

---

```python
def CanAddFluid(self, fluid_id: str) -> bool
```
容器能否添加指定种类的流体。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 如题 |

## 事件订阅
```python
self.handler.SubscribeOnAddedFluid(self.on_added_fluid)
```
容器内流体体积已经增加时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot | int | 流体槽位 |
| fluid_id | str | 添加的流体类型 |
| added_fluid_volume | float | 添加的流体体积 |
| is_final | bool | 是否为最后一个处理槽位 |

---

```python
self.handler.SubscribeOnReducedFluid(self.on_reduced_fluid)
```
容器内流体体积已经减少时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot | int | 流体槽位 |
| fluid_id | str | 减少的流体类型 |
| reduced_fluid_volume | float | 减少的流体体积 |
| is_final | bool | 是否为最后一个处理槽位 |

---

```python
self.handler.SubscribeOnFluidSlotUpdate(self.on_fluid_slot_update)
```
流体槽位发生更新时执行的回调。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot_pos | int | 流体槽位 |
| is_final | bool | 是否为最后一个处理槽位 |
