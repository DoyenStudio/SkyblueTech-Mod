# MultiBlockStructure

[基类索引](README.md) · [生命周期](../lifecycle.md)

检测主机周围结构、缺块提示、功能接口枚举与生命周期管理。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.MultiBlockStructure`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

structure_palette 必须提供；functional_block_ids 指定可查找的接口方块。

StructureFinished()、GetStructureLackedBlocks()、GetFunctionalBlockPoses()、GetAllMachines(cls,block_id=None)、GetLoadedMachine/ TryGetLoadedMachine。

## 事件与组合

构造注册 DetectArea，卸载注销；结构变化通过 SubscribeOnStructureChanged 传出。

结构图案唯一 # 为主机，. 是必须为空的位置；接口必须位于调色板允许位置，不能藏在空腔内凑数量。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[multi_block_structure.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/multi_block_structure.py)。

## 详细行为与既有存档说明

# MultiBlockStructure 多方块结构基类

多方块机器结构的基类。

派生自 `BaseMachine` 基类。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| structure_palette | StructureBlockPalette \| None | 用于进行多方块完整性检测的多方块结构调色板 |
| functional_block_ids | set[str] | 多方块结构中功能性方块的 ID 列表。GetLoadedMachine() 获取的机器方块 ID 都需要包含在其中; 这些方块只有放在调色板允许的位置上才算数, 藏进结构内部会让结构判破损 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| last_destroy_flag | (property) int | 上一次检测到的结构销毁标记 |
| lacked_blocks | (property) dict[str, int] | 结构要求的方块还差多少, 键为方块 ID, 值为还差的数量 |
| lacked_block_poses | (property) list[dict] | 结构破损时记录的位置列表, 每条包含 x/y/z/expected/actual; 也包括"多放东西"的位置: 空腔被填时 expected 是空气, 接口放错位置时 expected 是该位置允许放的方块 |

## 事件订阅
```python
self.handler.SubscribeOnStructureChanged(self.on_structure_changed)
```
结构变更（完成或破损）时的回调。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| structure_finished | bool | 结构是否已完成 |

## 基类方法
```text
def GetFunctionalBlockPoses(self) -> dict[str, list[tuple[int, int, int]]]
```
返回功能性方块的世界坐标, 按方块 ID 分组; 只有在结构完整时才会更新, 且只包含放在调色板允许位置上的方块。

| 返回类型 | 说明 |
| --- | --- |
| dict[str, list[tuple[int, int, int]]] | 方块 ID 对应坐标列表 |

---

```text
def GetLoadedMachine(self, cls: type[BaseMachine], block_id: str | None = None, index: int = 0) -> BaseMachine
```
获取多方块结构中某一类型的机器（多用于多方块结构接口的获取）。
其 ID 需要被包含在类属性 `functional_block_ids` 中。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| cls | type[BaseMachine] | 机器类 |
| block_id | str \| None | 机器方块 ID。默认为 cls.block_name |
| index | int | 索引值, 如果有多个匹配的机器则使用索引值 |

| 返回类型 | 说明 |
| --- | --- |
| BaseMachine | 所求机器实例 |

| 异常 | 说明 |
| --- | --- |
| ValueError | 找不到对应机器 |

---

```text
def TryGetLoadedMachine(self, cls: type[BaseMachine], block_id: str | None = None, index: int = 0) -> BaseMachine | None
```
GetMachine 的可空返回版本, 获取不到对应机器则返回 None。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| cls | type[BaseMachine] | 机器类 |
| block_id | str \| None | 机器方块 ID。默认为 cls.block_name |
| index | int | 索引值 |

| 返回类型 | 说明 |
| --- | --- |
| BaseMachine \| None | 所求机器实例, 找不到则返回 None |

---

## 结构调色板 StructureBlockPalette

结构调色板描述一个多方块结构, 位于 `common/utils/structure_palette.py`, 一般用
`GenerateSimpleStructureTemplate()` 由文本图案生成, 例如:

```python
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {
        "F": FRAME,
        # 一个字母可以对应多种方块: "这一圈上放哪种都行"
        "f": [FRAME, IO_ENERGY],
    },
    {
        -1: [
            "FfF",
            "fff",
            "FfF",
        ],
        0: [
            "f#f",
            "fCf",
            "fff",
        ],
    },
    require_blocks_count={IO_ENERGY: 1},
)
```

要点:

- 键是单字母, 值是方块 ID 或"方块 ID 列表"(可选族); 图案里同字母的位置允许放列表中任意一种方块。
- `#` 表示核心方块本身, 有且只能有一个; 核心方块不参与检测, 它固定在内部坐标 `(0, 0, 0)`。
- `GenerateSimpleStructureTemplate()` 的 `air_block_sign`(默认 `.`)表示"这里必须是空气":
  用来把结构内部的空腔钉死 —— 谁往里塞方块(尤其是接口方块), 结构就判破损, 并在 UI 里
  指出具体坐标。没有标 `.` 的空格位置才表示"不关心", 不参与检测。
- 层号是 `y` 的相对值, 行是 `z`、列是 `x`; 图案按核心朝北编写, 其余朝向由 90° 旋转派生。
- 检测只要求"期望位置被填上", 多出来的方块不影响匹配; 想把位置钉死到具体方块, 用
  `require_blocks_count`, 它只统计**落在允许该方块的位置上**的数量。
- 功能性方块(接口)只能放在调色板允许的位置上: 藏进结构内部空腔的接口不会出现在
  `GetFunctionalBlockPoses()` 里, `GetLoadedMachine()` 取不到, 而且结构会被判定为破损。

## 多方块结构手杖

公共注册表位于 `skybluetech_scripts.skybluetech.common.machinery_def.multi_block_structures`：

```python
CONTROLLER_STRUCTURE_PALETTES = {
    CONTROLLER_ID: STRUCTURE_PALETTE,
}
```

表中存放朝北的原始调色板，当前登记电池仓、基岩熔岩钻、卤水池、发酵池、海水蓄水池和真空冷却仓。
新增结构时，在此表增加控制器 ID 与对应调色板即可接入手杖。

手杖在工作台合成，消耗 3 个轻质蔚蓝锭（A）和 2 根钢棒（B），`.` 表示空格：

```text
.AA
.BA
B..
```

玩家手持 `skybluetech:multiblock_structure_scepter` 点击控制器后：

1. 按控制器朝向旋转调色板，分帧扫描整个结构，收集通过 `MayPlace` 检查的未匹配位置。
2. 扫描完成后，按背包中的同名、aux=0 方块生成建造计划。优先满足接口最低数量，再使用剩余材料搭建其他位置；材料不足时仍搭建可完成的部分。
3. 每帧最多尝试放置 8 个方块。每次先复核位置和 `MayPlace`，再扣除当前背包中的一份材料并放置；放置失败返还该份材料。
4. 全部尝试结束后重新检查整个结构，汇总显示实际不匹配总数，在聊天栏每帧发送一条消息，最多列出前 20 处不匹配坐标、期望方块和当前方块，方块名称使用本地化名称。没有材料或没有可放置位置也会执行这一步。最低接口数量不足时另列缺额，不显示可放置位置列表。

手杖不会拆除障碍物、清空空腔或替换已经合法的外壳。水等没有同名背包方块的材料需要手动准备，手杖不进行水桶转换。
同一玩家或同一控制器同时只处理一个任务；玩家离线、切换维度或控制器改变时停止后续建造，未使用材料保留在背包中。
