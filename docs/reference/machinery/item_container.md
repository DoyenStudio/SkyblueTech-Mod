# ItemContainer

[基类索引](README.md) · [生命周期](../lifecycle.md)

访问自定义物品容器及输入输出槽，参与玩家放入校验。

直接继承：`BaseMachine`。服务端正式入口：`skybluetech_scripts.skybluetech.server.export.machinery.ItemContainer`（先 ImportModule 取模块，再访问类）。

## 配置与常用接口

item_input_slots=()；item_output_slots=()；槽号必须与 JSON 容器大小、UI collection_index 一致。

GetSlotItem(slot_pos)、SetSlotItem(slot_pos,item)、GetInputSlotItems()、GetOutputSlotItems()、DropAllItems()、IsValidInput(slot,item)。

## 管道分面槽位

`item_input_slots_by_face`、`item_output_slots_by_face` 的类型均为 `dict[str, tuple[int, ...]] | None`，默认 `None`，保持原有输入与抽取行为。键使用 `RelativeFacingStrEnum`，左右以面对机器正面的视角为准。

```python
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

# 在机器类上声明；槽号必须属于已有的对应输入/输出槽。
item_input_slots_by_face = {
    RelativeFacingStrEnum.TOP: (0,),
}
item_output_slots_by_face = {
    RelativeFacingStrEnum.LEFT: (1,),
    RelativeFacingStrEnum.RIGHT: (2,),
}
```

- `None` 不增加限制；`{}` 禁止所有面；映射中缺失的面和 `()` 均禁止对应操作。四种物品/流体输入/抽取配置互相独立。
- 白名单与原有对应槽位取交集，不能开放原料槽供抽取或产物槽供输入。保留原有候选槽顺序，映射值不定义优先级。
- `GetItemInputSlotsForFace(relative_face)`、`GetItemOutputSlotsForFace(relative_face)` 返回筛选后的元组。方向解析失败传入 `None` 时，有配置则禁止，无配置则返回原有槽位。
- 管道先将指向机器的接入方向取反，再用 `GetRelativeFacing` 转为相对面；优先读取 `minecraft:facing_direction`，否则读取 `minecraft:cardinal_direction`。缺失或无效方向不猜测正面，旋转后的下一次传输重新读取方向。
- 网络 tick 与直接投递 `PushItemToGenericContainerEasy` 均生效；后者的 `face` 从来源指向目标。原有事件否决和 `IsValidInput` 校验仍有效，网络连接模式不变。
- 类属性不写入存档、不在运行中修改，子类覆写整个映射，不合并父类配置。玩家 UI、机器内部存取不受这些属性限制。

### 游戏内验收

分别检查无配置、空映射、缺失面、空元组和越界权限槽位；用不同物品填充多槽，确认每个接入面只改变允许的槽位。覆盖四个水平朝向、上下正面、旋转后的下一次传输、同一机器多面接同一管网、直接投递和网络 tick。检查满槽、空槽、事件取消时物品总数守恒，并回归普通容器与无配置机器。本清单需在游戏内执行，不在本地运行或编译项目 Python。

## 事件与组合

自动订阅 SubscribeOnCustomCotainerPutItem（名称沿用现有 API 拼写）。

SetSlotItemCount 的原 API 对自定义容器有已知问题，应使用项目已有设置物品方式。继承容器不等于创建 JSON 容器。

所有自定义构造器遵守协作式 `super(当前类, self).__init__(dim, x, y, z, block_entity_data)`；已有父类订阅不要重复登记。具体操作示例见[机器教程](../../tutorials/03-recipe-machines.md)。

源码：[item_container.py](../../../behavior_pack/skybluetech_scripts/skybluetech/server/machinery/basic/item_container.py)。
