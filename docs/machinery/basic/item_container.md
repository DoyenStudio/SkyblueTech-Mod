# ItemContainer 物品容器基类

可存储物品的机器基类。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| input_slots | tuple[int, ...] | 可用输入槽位 |
| output_slots | tuple[int, ...] | 可用输出槽位 |

## 基类方法
```python
def GetSlotItem(self, slot_pos: int, get_user_data: bool = True) -> Item | None
```
获取槽位内的物品。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot_pos | int | 槽位 ID |
| get_user_data | bool | 是否获取物品的 userData。默认为 True |

| 返回类型 | 说明 |
| --- | --- |
| Item \| None | 槽位内物品实例, 如果为空则返回 None |

---

```python
def SetSlotItem(self, slot_pos: int, item: Item | None) -> bool
```
设置槽位内的物品。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot_pos | int | 槽位 ID |
| item | Item \| None | 设置的物品, 如果为 None 则设置槽位为空 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 是否成功设置物品 |

---

```python
def DropAllItems(self) -> None
```
掉落所有槽位内的物品。

---

```python
def SetSlotItemCount(self, slot_pos: int, count: int) -> None
```
> **WARNING**: 此 api 对于自定义容器有 bug。

设置槽位内物品数量。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot_pos | int | 槽位 ID |
| count | int | 数量 |

---

```python
def GetSlotSize(self) -> int
```
获取输入槽和输出槽的总数量。

| 返回类型 | 说明 |
| --- | --- |
| int | 总槽位数 |

---

```python
def GetInputSlotItems(self, get_user_data: bool = True) -> dict[int, Item]
```
获取输入槽的所有物品。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| get_user_data | bool | 是否获取物品的 userData。默认为 True |

| 返回类型 | 说明 |
| --- | --- |
| dict[int, Item] | 槽位对应的物品实例, 如果槽位里有物品 |

---

```python
def GetOutputSlotItems(self) -> dict[int, Item]
```
获取输出槽的所有物品。

| 返回类型 | 说明 |
| --- | --- |
| dict[int, Item] | 槽位对应的物品实例, 如果槽位里有物品 |

---

```python
def SetSlotItems(self, slotitems: dict[int, Item | None]) -> None
```
设置多个槽位内的物品。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slotitems | dict[int, Item \| None] | 槽位 ID 对应物品实例 |

---

```python
def PushItem(self, item: Item) -> Item | None
```
尝试将物品输入此容器。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| item | Item | 将输入的物品 |

| 返回类型 | 说明 |
| --- | --- |
| Item \| None | 如有剩余物品则返回物品实例 |

---

```python
def CanOutputItems(self, items: list[Item]) -> bool
```
机器是否可以输出这些物品。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| items | list[Item] | 物品列表 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 如题 |

---

```python
def OutputItem(self, item: Item) -> Item | None
```
输出产出的物品。需要机器设置了 output_slots。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| item | Item | 产出物 |

| 返回类型 | 说明 |
| --- | --- |
| Item \| None | 剩余物品, 当没有剩余物时返回 None |

## 事件订阅
```python
def IsValidInput(self, slot: int, item: Item) -> bool
```
判定槽位物品是否为合法输入。超类防止物品输入到输出口。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot | int | 槽位 ID |
| item | Item | 物品实例 |

| 返回类型 | 说明 |
| --- | --- |
| bool | 是否合法输入 |

---

```python
self.handler.SubscribeOnSlotUpdate(self.on_slot_update)
```
机器物品槽位更新的回调。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| slot_pos | int | 槽位 ID |
