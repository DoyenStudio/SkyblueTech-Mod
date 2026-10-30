# coding=utf-8
"""
蔚蓝科技的配方 → MEI 的配方。**纯函数，不继承 MEI 的任何类型**，故可以写在模块级。

（需要继承 MEI 类型的东西都在 runtime.py —— 基类是运行期从组件取到的对象，
类定义只能放在函数里。）

两边模型的差别就三条：

  1. 蔚蓝的 inputs/outputs 是 `{类别: {槽位: 元素}}` 双层 dict，
     MEI 是两个**有序 list**。⇒ 按槽位号升序摊平，槽位号另存进 Data 备查。
  2. 蔚蓝的类别里除了 item 还有 fluid / energy / exp，MEI 只认物品。
     ⇒ 目前只转 item，其余类别原样落进 Data，等概念物品接入后再处理。
  3. 蔚蓝的 `Input.is_tag` 对应 MEI 的 `Ingredient.from_tag(tag_id=)`。
     **这条必须走 from_tag，不能自己展开成多候选** —— 见 to_ingredient 的注释。
"""
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag

from . import bridge

CATEGORY_ITEM = "item"
CATEGORY_FLUID = "fluid"
""" 蔚蓝 CategoryType 的字面值。这里不 import 它们的 CategoryType 是刻意的：
    本模块只认下面 SLOT_KINDS 里的那几种，多认一种就要多接一种，
    不如让缺失显式暴露 """

SLOT_KINDS = (CATEGORY_ITEM, CATEGORY_FLUID)
"""
**会渲染成槽位**的类别，与 MEI 的 `Stack.KIND` 同一套字符串。

其余类别（`energy` / `exp` / `exp_lv`）**不是槽位** ——
它们没有真 id、不进物品表、点了也查不出用途，minijei 自己也是当
label 画的（`output_power_displayer` / `xp_cost_label`）。
→ 原样落进 `Recipe.Data`，由各机型的配方页自己画文字。
论据见 `skybluetech.md` §7.8.1-②。
"""


class Element(object):
    """
    形同蔚蓝 `Input` / `Output` 的元素：数据不是配方集合的机器（发酵池、火力 / 地热发电机）自己拼配方时用，
    好让 `to_ingredient` 一条路走到底（特殊值、概率、流体的 KIND 都照旧）。
    """

    __slots__ = ("id", "count", "prob", "aux", "is_tag")

    def __init__(self, item_id, count=1, prob=1):
        # type: (str, float, float) -> None
        self.id = item_id
        self.count = count
        self.prob = prob
        self.aux = 0
        self.is_tag = False


def slot_key(kind, slot):  # type: (str, any) -> str
    """
    槽位键，形如 `"item:0"` / `"fluid:0"`。

    **为什么必须带类别前缀**：蔚蓝的槽位号是按类别分命名空间的。
    金属压印机 / 搅拌机 / 热能反应发电机的输入都长这样：
    `{ITEM: {0: ...}, FLUID: {0: ...}}` —— **两个 0**。
    minijei 靠控件名分开（`slot0` vs `fluid0`）；而 MEI 侧两类入参合并成
    一个 `Recipe.Inputs` 后，不带前缀就会变成 `[0, 0]`，
    `IngredientForCell` 按槽位号反查会取错格。

    用字符串而不是 `(kind, slot)` 元组：`Recipe.Data` 是会序列化出去的，
    而**引擎的 CreateEventData / NotifyTo* 不支持 tuple**（CLAUDE.md 引擎结论 §6）。
    """
    return "%s:%d" % (kind, _slot_index(slot))


def slot_number(key):  # type: (any) -> int
    """ 从槽位键取回编号。旧形式（纯数字）也收 """
    if isinstance(key, basestring) and ":" in key:
        return _slot_index(key.split(":", 1)[1])
    return _slot_index(key)


def flatten_slots(slot_map):  # type: (dict) -> list
    """
    `{槽位: 元素}` → 按槽位号**升序**的元素表

    顺序必须确定：MEI 的 Recipe.Id 是内容哈希，而有序配方的 canonical 保序。
    直接 `.values()` 会拿到 py2 dict 的哈希序 —— 同一条配方两次运行可能算出两个 Id，
    玩家的置顶与书签就全错位了。（MEI 自己也栽过：RecipeManager.processors
    当年因为撞 dict 哈希才改成 OrderedDict。）

    排序键取 `int(slot)` 而不是原值：字符串序下 "10" < "2"，十格以上的机器会排错。
    """
    if not slot_map:
        return []
    return [slot_map[key] for key in sorted(slot_map.keys(), key=_slot_index)]


def slot_numbers(slot_map):  # type: (dict) -> list
    """ 与 flatten_slots 同序的槽位号表，供 UI 脚本按自己的 layout 取用 """
    if not slot_map:
        return []
    return [_slot_index(key) for key in sorted(slot_map.keys(), key=_slot_index)]


def _slot_index(key):  # type: (any) -> int
    try:
        return int(key)
    except (TypeError, ValueError):
        return 0


def _amount_of(element):  # type: (any) -> int
    """ 蔚蓝的 count 是 float（流体体积要小数），物品侧取整且至少为 1 """
    try:
        value = int(round(float(getattr(element, "count", 1) or 1)))
    except (TypeError, ValueError):
        return 1
    return value if value > 0 else 1


def stacks_of(item_ids, count=1):  # type: (any, int) -> list
    """ id 表 → ItemStack 表。**拿不到的物品会被跳过**，不抛 """
    # 走 MEI 的工厂而不是自己造 Item: Item 的惰性 Info 加载回调由工厂注入,
    # 自己 new 出来的拿不到名字与堆叠上限
    return bridge.Registry.ItemFactory.GetStacksFromIds(list(item_ids or ()), count)


def stacks_of_element(element):  # type: (any) -> list
    """ 一个 `Input` / `Output` 的物品堆，带上特殊值；拿不到返回空表 """
    # next 框架起元素带 aux（缺省 0，-1 表示任意特殊值）。0 与 -1 都按 0 造 ——
    # MEI 的物品键本来就把 -1 规约成 0；其余特殊值要经工厂按 aux 造，否则会画成别的变体
    aux = int(getattr(element, "aux", 0) or 0)
    if aux in (0, -1):
        return stacks_of([element.id])
    factory = bridge.Registry.ItemFactory
    try:
        item = factory.GetItem(ItemId=element.id, AuxValue=aux)
    except Exception:  # noqa  物品表里没有这个 id: 与 GetStacksFromIds 一样跳过
        return []
    return [item.stack(1)] if item else []


def to_ingredient(element, kind=CATEGORY_ITEM):  # type: (any, str) -> any
    """
    蔚蓝的 `Input` / `Output` → MEI 的 `Ingredient`。转不出来返回 None

    `kind` 是条目种类（`SLOT_KINDS` 之一）：流体候选要包成 `FluidStack`，
    它靠 `Stack.KIND` 告诉 `render_slot` 该用哪个面板。
    除此之外与物品一模一样 —— 流体本来就是个隐藏 Item。

    **标签必须走 `from_tag(tag_id=...)`，不能自己展开成字面多候选。**
    理由是 `GetItemsByTag` 的数据是**异步**从服务端拉来的（allitems_getter 走
    C2S/S2C 一个来回）：字面展开的话，「标签还没到」与「标签到了」两个时刻
    会算出两个不同的 `Recipe.Id`，索引会把同一条配方当成两条。
    `from_tag` 给的 Ingredient 在算身份时只发标签引用、不展开成员，因此免疫。
    （MEI 的 mei:fuels 踩过同一个坑，见其 tasks_s2b.md §2。）
    """
    Ingredient = bridge.Types.Ingredient
    amount = _amount_of(element)
    chance = float(getattr(element, "prob", 1) or 1)

    if getattr(element, "is_tag", False):
        tag = element.id
        # 成员为空是正常的中间态(标签表还没从服务端到), 不是错误 ——
        # Id 不受影响, 只是这一刻还查不到"哪些物品能用"
        candidates = stacks_of(sorted(GetItemsByTag(tag)))
        return Ingredient.from_tag(candidates, amount, tag_id=tag)

    stacks = _typed(stacks_of_element(element), kind)
    if not stacks:
        return None
    if chance != 1:
        return Ingredient(stacks, amount, chance=chance)
    return Ingredient.of(stacks[0], amount)


def _typed(stacks, kind):  # type: (list, str) -> list
    """ 非物品种类的候选换成带 KIND 的兄弟类。物品原样返回 """
    if kind == CATEGORY_ITEM or not stacks:
        return stacks
    if kind == CATEGORY_FLUID:
        from .fluids import StackCls
        FluidStack = StackCls()
        # 身份与序列化全部沿用 ItemStack, 换的只是 KIND —— 不漂移 Recipe.Id
        return [FluidStack(st.Item, st.Count) for st in stacks]
    return stacks


def is_resolved(ingredient):  # type: (any) -> bool
    """
    这个 Ingredient 的候选是不是已经落实了。

    只对**标签**有意义：标签表异步到达，先建出来的 Ingredient 候选是空的。
    候选为空 ⇒ `StaticRecipeSource` 按 `get_stacks()` 建的「按材料查用途」索引
    会漏掉这一格。来源据此判断要不要重建表，见 runtime.py 的自愈。
    """
    if ingredient is None:
        return False
    if not ingredient.get_tag_id():
        return True
    return bool(ingredient.get_stacks())


def split_inputs(sb_recipe):  # type: (any) -> tuple
    """
    蔚蓝配方的输入 → (槽位条目表, 非槽位类别的原始数据)

    槽位条目表的元素是 `(槽位键, 元素, 种类)`，涵盖 `SLOT_KINDS` 里的全部类别。
    其余类别（energy / exp）**原样带走而不是丢掉** —— 它们要落进
    `Recipe.Data`，由配方页自己画成 label（不是槽位，见 SLOT_KINDS 的说明）。
    """
    return _split(getattr(sb_recipe, "inputs", None) or {})


def split_outputs(sb_recipe):  # type: (any) -> tuple
    return _split(getattr(sb_recipe, "outputs", None) or {})


def _split(by_category):  # type: (dict) -> tuple
    entries = []
    others = {}
    for category, slot_map in (by_category or {}).items():
        if category in SLOT_KINDS:
            for slot, element in slot_map.items():
                entries.append((slot_key(category, slot), element, category))
            continue
        # 非槽位类别: 存成 {类别: [[槽位, id, 数量], ...]}，全部是标量，
        # 才能安全地躺在 Recipe.Data 里(引擎事件与存盘都不收 Python 对象)。
        # **用 list 不用 tuple** —— 引擎的 CreateEventData / NotifyTo* 不支持 tuple，
        # 而 Recipe.Data 是会随配方一起序列化出去的
        others[category] = [
            [_slot_index(slot), element.id, float(getattr(element, "count", 0) or 0)]
            for slot, element in sorted(slot_map.items(), key=lambda kv: _slot_index(kv[0]))
        ]

    # 排序必须确定: MEI 的 Recipe.Id 是内容哈希，有序配方的 canonical 保序。
    # 按 (种类, 槽位号) 而不是槽位键字符串: 后者在 "10" < "2" 上会排错。
    # ⥠ 实数据核过: 这一排对**已上线的 9 台全部是空操作**，
    #   玩家的置顶与书签安全（模板成型机恰好占着第 10 格，它就是上面那个坑）。
    #   真正靠它定下来的是**混类别输入**那三台（金属压印机 / 搅拌机 /
    #   热反应发电机，都是 `item:0` + `fluid:0`）: 不排的话外层跑的是
    #   `by_category.items()`，键是字符串，而 py2 的 str hash 在 32/64 位构建下不同
    #   （CLAUDE.md 引擎结论 §8 为此禁掉了内建 hash()）
    #   ⇒ 同一条配方在 PC 与手机上会算出两个 Id。
    entries.sort(key=lambda e: (e[2], slot_number(e[0])))
    return entries, others
