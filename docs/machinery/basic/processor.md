# Processor 耗能配方处理器基类

如果你只是单纯地想让机器接受输入，消耗能量，经过一段时间输出产物~~(变成一个熔炉pro)~~， 那么可以直接继承Processor类。

派生自 `ProcessBase` 基类。
`ProcessBase` 派生自 `GUIControl`, `UpgradeControl`, `WorkRenderer` 基类。

目前 Processor 支持与 `MultiFluidContainer` 基类组合。（由于 Processor 本身继承自 `ItemContainer` 基类，所以默认支持）

## 类属性

为了一步到位，直接列出所有可用的类属性，包括父类的类属性。

- 基本类属性：

| 属性名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| block_name | str | 机器方块 ID |
| store_rf_max | int | 机器最大存储能量 | 10000 |
| process_item | bool | 是否需要处理物品，有物品输入或输出都要设为 True。下同 | False |
| process_fluid | bool | 是否需要处理流体 | False |
| recipes | RecipesCollection\[MachineRecipe] | 机器可用配方集 |
| upgrade_slot_start | int | 升级槽集合的首个槽位索引 | 2 |
| upgrade_slots | int | 升级槽集合的槽位数量 | 4 |

- 物品容器基类属性：

| 属性名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| input_slots | tuple\[int] | 物品输入槽位 | () |
| output_slots | tuple\[int] | 物品输出槽位 | () |

- 多流体容器基类属性：

| 属性名 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| fluid_input_slots | set\[int] | 可用的流体输入槽位 | set() |
| fluid_output_slots | set\[int] | 可用的流体输出槽位 | set() |
| fluid_slot_max_volumes | tuple\[float] | 每个流体槽位最大容量 | () |

## 初始化与事件订阅

组合多流体容器时使用 `class FluidCondenser(Processor, MultiFluidContainer)`。
`super()` 按 MRO 串联初始化, 流体容器须在配方检查前创建 `self.fluids`。

```python
@RegisterMachine
class FluidCondenser(Processor, MultiFluidContainer):
    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidCondenser, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnPlaced(self.on_placed)

    def on_placed(self, event):
        self.recheck_recipe()
```

`Processor` 会自行订阅 tick、物品槽位及多流体增减事件, 不再需要空的 `OnXXX` 方法或装饰器。
新增组件构造器均须调用一次 `super(当前类, self).__init__(...)`, 不要手动逐个调用父类构造器。
订阅回调使用组件各自的名称, 防止继承覆写意外替换其他组件的回调。
