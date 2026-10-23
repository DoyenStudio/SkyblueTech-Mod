# MultiFluidContainer

[基类索引](README.md) · [生命周期](../lifecycle.md)

按槽位编号维护一个或多个流体槽，负责输入过滤与变化通知。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.MultiFluidContainer`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

fluid_slot_max_volumes；fluid_input_slots、fluid_output_slots；fluid_io_mode 的 -1 兼容、0 输入、1 输出、其他关闭；player_fluid_input_slots=None 默认复用输入槽。

AddFluid(id,volume)、OutputFluid(id,volume,slot_pos,is_final) 均返回 (是否接收, 未接收量)；CanAddFluid(id)；IsValidFluidInput(slot,id)。

## 事件与组合

变更方法分发 Added/Reduced/FluidSlotUpdate 事件，带 GUI 时同步；仅直接改 fluids 槽值不会自动通知。

新设备 migrate_legacy_fluid_data=False。单槽也用本类，按 fluids[0] 访问。配方机使用 (Processor, MultiFluidContainer)。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[multi_fluid_container.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/multi_fluid_container.py)。

## 详细行为与既有存档说明

# MultiFluidContainer 多流体容器基类

所有流体容器统一使用本基类。只需存储一种流体的机器声明一个槽位即可。

与物品槽类似，流体容器的流体槽也依靠数字 ID 区分槽位。
流体槽 ID 无需连续，使用 `fluid_slot_max_volumes` 字典显式配置槽位编号及容量。

增减流体后，基类通过 `self.handler` 分发对应事件和槽位更新事件，并为带 GUI 的机器同步数据。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluid_io_mode | tuple[int, int, int, int, int, int] | 每个面的流体输入输出模式, -1:兼容 0:输入 1:输出 其他:无 |
| fluid_input_slots | tuple[int, ...] | 可接受输入的流体槽位 |
| fluid_output_slots | tuple[int, ...] | 可输出的流体槽位 |
| player_fluid_input_slots | set[int] \| None | 桶和试管可倒入的槽位；None 时使用 fluid_input_slots |
| fluid_slot_max_volumes | dict[int, float] | 流体槽位编号到最大容量的映射 |
| allow_player_use_bucket_interact | bool | 是否允许玩家直接使用桶交互 |
| allow_player_use_bucket_push | bool | 是否允许玩家直接使用桶装填流体 |
| allow_player_use_bucket_pull | bool | 是否允许玩家直接使用桶取出流体 |
| migrate_legacy_fluid_data | bool | 原单流体设备启用的一次性存档迁移；新设备默认 False |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| fluids | dict[int, FluidSlotServer] | 槽位编号到流体槽对象的映射 |

**FluidSlotServer 定义**
| 属性名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| fluid_id | (property) str | 流体ID，`None`表示为空  | None |
| volume | (property) float | 流体体积 | 0.0 |
| max_volume | float | 流体槽最大容量 | 0.0 |


## 基类方法
```text
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

```text
def OutputFluid(self, fluid_id: str, fluid_volume: float, slot_pos: int, is_final: bool) -> tuple[bool, float]
```
在指定槽位中产出流体，不受 `fluid_input_slots` 和输入过滤限制，但仍检查类型和剩余容量。向多方块输出接口灌液应使用本方法。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |
| slot_pos | int | 流体槽位 |
| is_final | bool | 是否为最后一个处理槽位 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否接收了流体, 剩余未接收的流体容量 |

---

```text
def AddFluid(self, fluid_id: str, fluid_volume: float) -> tuple[bool, float]
```
按槽位编号依次将流体输入到合适的输入槽位，同时检查容量、流体类型和 `IsValidFluidInput`。一份流体可分配到多个输入槽；本次实际更新的最后一个槽位收到 `is_final=True`。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| fluid_id | str | 流体类型 |
| fluid_volume | float | 流体容量 |

| 返回类型 | 说明 |
| --- | --- |
| tuple[bool, float] | 是否添加成功, 剩余的流体容量 |

---

```text
def CanAddFluid(self, fluid_id: str) -> bool
```
按 `AddFluid` 相同的输入槽、容量、类型和过滤规则检查能否添加流体。

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

## 单槽设备

原单流体设备使用 `fluids[0]`，不再提供机器级别的液体 ID、体积和容量属性。例如一个双向储罐：

```python
class ExampleTank(MultiFluidContainer):
    fluid_slot_max_volumes = {0: 32000}
    fluid_input_slots = (0,)
    fluid_output_slots = (0,)
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
```

使用 `self.fluids[0].fluid_id`、`volume`、`max_volume` 读写槽位。直接修改槽位不会自动分发机器事件；调用方必须在状态更新完成后调用 `_on_added_fluid(0, fluid_id, amount, True)` 或 `_on_reduced_fluid(0, fluid_id, amount, True)`。

泵只有输出槽，采矿机和流体输入接口只有输入槽。流体输出接口只有输出槽，主机使用 `OutputFluid(..., 0, True)` 灌入；其 `player_fluid_input_slots = {0}` 保留桶和试管手动倒液能力。管道仍按六面 `fluid_io_mode` 连接。

流体接口容量统一使用 `common/machinery_def/fluid_interface.py` 的 `FLUID_INTERFACE_MAX_VOLUME`，储罐容量统一使用 `TANK_MAX_VOLUMES`。客户端使用 `FluidSlotClient(ex_data, 0, max_volume)` 读取；无限储罐需要传入对应容量，才能将有限存档标记显示为无限体积。

## 存档和无限储罐

每个槽位仍使用原生标量字段 `fluid_idN`、`fluid_volN`。体积写为原生 `float`，不使用 JSON。体积小于等于 `1e-6` 时清空流体类型，有限槽的体积不超过其容量。

原单流体设备启用 `migrate_legacy_fluid_data = True`，在构造槽位前迁移 `fluid_id`、`fluid_vol` 到 `fluid_id0`、`fluid_vol0`。已有任一新字段的非 None 值优先，包括体积为零的空槽。完成后清空旧字段并记录 `fluid_slot_migrated = True`，防止耗空后重载恢复旧液体。新建多槽机器不启用此迁移。

创造储罐使用容量为 `float("inf")` 的槽位。空罐首次注液后按液体类型提供无限供应；已配置的罐拒绝继续注入和混液。服务端内存体积为无限，存档只记录类型和 `fluid_vol0 = 1.0`。重载时依据液体类型恢复无限供应，客户端也依据容量恢复无限显示，不向 NBT 写入 `inf`。

## 游戏内回归检查

- 普通储罐：每种容量、桶和试管双向操作、物品槽装桶、满罐拒绝输入、抽空后更换液体。
- 创造储罐：首次使用桶、试管或管道设定类型，持续输出不耗尽，拒绝再次注入或混液，液面和 UI 显示无限。
- 泵：源流体按批次进入缓存，主槽装满时缓存不丢失，排空后继续抽取，缓存与槽内类型一致。
- 采矿机：补液唤醒、耗液至不足时停机、桶/试管和管道补液后的状态显示。
- 输出接口：管道仅抽出，桶和试管仍可手动倒入，主机产出使用指定槽位；输入接口保持反向行为。
- 发酵机、基岩熔岩钻机和真空冷冻机：连续输入输出，接口满后停止或等待，腾出空间后继续，无复制或混液。
- 现有多槽机器：一次输入跨槽、提前装完、末尾候选槽不合适时，仍收到最终更新以检查配方。
- 旧字段迁移、新字段优先、抽空后重载、区块卸载和切维度、退出重进后的容量和流体类型。
- 检查实际序列化 NBT；创造储罐只保存有限标记，缓存立即读回成功不能替代存盘重载验收。
