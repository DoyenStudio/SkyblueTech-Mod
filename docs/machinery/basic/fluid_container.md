# FluidContainer 单流体容器基类

可存储单种流体的机器基类。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluid_io_mode | tuple[int, int, int, int, int, int] | 流体容器六个面的输入输出模式, -1:兼容 0:输入 1:输出 其他:无 |
| max_fluid_volume | float | 最多可存储流体容量, 默认为 1000 |
| allow_player_use_bucket_interact | bool | 是否允许玩家直接使用桶交互 |
| allow_player_use_bucket_push | bool | 是否允许玩家直接使用桶装填流体 |
| allow_player_use_bucket_pull | bool | 是否允许玩家直接使用桶取出流体 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | (property) str \| None | 容器内当前流体的 ID |
| fluid_volume | (property) float | 容器内当前流体的容量 |

## 基类方法
```python
def AddFluid(self, fluid_id: str, fluid_volume: float) -> tuple[bool, float]
```
添加流体。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否添加成功, 添加的流体容量 |

---

```python
def OutputFluid(self, fluid_id: str, fluid_volume: float) -> tuple[bool, float]
```
产出流体。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否产出成功, 产出的流体容量 |

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
self.handler.SubscribeOnSingleFluidSlotUpdate(self.on_fluid_slot_update)
```
流体内容更新时调用。

---

```python
self.handler.SubscribeOnSingleAddedFluid(self.on_added_fluid)
```
容器内流体体积已经增加时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 添加的流体类型 |
| added_fluid_volume | float | 添加的流体体积 |

---

```python
self.handler.SubscribeOnSingleReducedFluid(self.on_reduced_fluid)
```
容器内流体体积已经减少时调用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 减少的流体类型 |
| reduced_fluid_volume | float | 减少的流体体积 |
