# MultiBlockStructure 多方块结构基类

多方块机器结构的基类。

派生自 `BaseMachine` 基类。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| structure_palette | StructureBlockPalette \| None | 用于进行多方块完整性检测的多方块结构调色板 |
| functional_block_ids | set[str] | 多方块结构中功能性方块的 ID 列表。GetMachine() 获取的机器方块 ID 都需要包含在其中; 这些方块只有放在调色板允许的位置上才算数, 藏进结构内部会让结构判破损 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| last_destroy_flag | (property) int | 上一次检测到的结构销毁标记 |
| lacked_blocks | (property) dict[str, int] | 结构要求的方块还差多少, 键为方块 ID, 值为还差的数量 |
| lacked_block_poses | (property) list[dict] | 结构破损时记录的位置列表, 每条包含 x/y/z/expected/actual; 也包括"多放东西"的位置: 空腔被填时 expected 是空气, 接口放错位置时 expected 是该位置允许放的方块 |

## 基类覆写方法
```python
def OnStructureChanged(self, structure_finished: bool) -> None
```
结构变更（完成或破损）时的回调。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| structure_finished | bool | 结构是否已完成 |

## 基类方法
```python
def GetFunctionalBlockPoses(self) -> dict[str, list[tuple[int, int, int]]]
```
返回功能性方块的世界坐标, 按方块 ID 分组; 只有在结构完整时才会更新, 且只包含放在调色板允许位置上的方块。

| 返回类型 | 说明 |
| --- | --- |
| dict[str, list[tuple[int, int, int]]] | 方块 ID 对应坐标列表 |

---

```python
def GetMachine(self, cls: type[BaseMachine], block_id: str | None = None, index: int = 0) -> BaseMachine
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

```python
def TryGetMachine(self, cls: type[BaseMachine], block_id: str | None = None, index: int = 0) -> BaseMachine | None
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
  `GetFunctionalBlockPoses()` 里, `GetMachine()` 取不到, 而且结构会被判定为破损。
