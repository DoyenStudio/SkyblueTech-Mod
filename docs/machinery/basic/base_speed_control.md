# BaseSpeedControl 速度控制机器基类

基本的速度控制机器基类。

派生自 `BaseMachine` 基类。

基类会在构造时直接向 `self.handler` 订阅所需事件, 无需重声明空方法。


## 需要定义的类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| origin_process_ticks | int | 机器默认的单次处理所耗 ticks |
| dump_progress_to_block_entity_data | bool | 是否在运行时将进度导出到方块实体, 供客户端UI读取 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| ticks_left | (property) float | 机器工作一次剩余ticks，大多数时候为int |

## 基类方法
```python
def SetSpeedRelative(self, speed: float) -> None
```
设置相对速度。默认为 1

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| speed | float | 相对速度 |

---

```python
def ProcessOnce(self)
```
尝试处理一次配方, 如可处理返回 True, 制作中返回 False

值得注意的是, 我们可能要在 1tick 之内进行多次配方产出

| 返回值 | 说明 |
| --- | --- |
| bool | 是否已完成一次处理, 可进行配方产出 |

---

```python
def SetProcessTicks(self, ticks: int) -> None
```
设置工作一次所需 ticks。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| ticks | int | mc game ticks |

---

```python
def GetProcessProgress(self) -> float
```
获取工作进度 (最多为 1)。

| 返回类型 | 说明 |
| --- | --- |
| float | 工作进度, 0~1 |

---

```python
def ResetProgress(self) -> None
```
重置工作进度。
