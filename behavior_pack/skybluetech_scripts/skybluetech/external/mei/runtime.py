# coding=utf-8
"""
需要**继承 MEI 类型**的东西全在这里。

为什么单独一个模块：MEI 的基类是运行期从组件上取到的对象，
`class Foo(Types.StaticRecipeSource)` 写在模块级必然 NameError。
所以这类定义只能包在函数里，由 `Build()` 在 OnRegister 阶段造一次。

（不继承 MEI 类型的纯逻辑在 convert.py，那些可以正常写在模块级。）

**没有 Recipe 子类是刻意的**：机器配方不需要形状（GetShape 返回 None 即自由布局），
功率与耗时属于展示元数据，`Recipe.Data` 就够装。加一层子类只会多一处要维护的
`_extra_to_canonical` —— 那个写错会毁掉 Recipe.Id 的稳定性。
"""
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetAllItems

from . import bridge, convert

_BUILT = None
""" Build() 的结果缓存。同一个游戏进程里类只造一次 —— 每次进世界都重造的话，
    上个世界建出来的配方与新造的类会 isinstance 不上 """


def Build():  # type: () -> any
    """ 造出运行期类；重复调用返回同一份 """
    global _BUILT
    if _BUILT is not None:
        return _BUILT
    _BUILT = _Namespace(MachineRecipeSource=_BuildSource(), ListRecipeSource=_BuildListSource())
    return _BUILT


def MakeRecipe(category_id, inputs, outputs, data=None, catalysts=None):
    # type: (str, list, list, dict, list) -> any
    """
    拼一条 MEI 配方 —— 数据不是蔚蓝配方集合的机器（发酵池、火力 / 地热发电机）用。

    `inputs` / `outputs` 是 `[(种类, 槽位号, 物品 id, 数量, 概率), ...]`，槽位号同蔚蓝的写法（流体、物品各自从 0 数）。
    规则同 `_Convert`：物品表里没有的输入保留成空格（槽位表不错位），没有的产物整格丢掉（两张表同一趟过滤）。
    """
    Ingredient = bridge.Types.Ingredient
    in_slots, in_list = [], []
    for kind, slot, item_id, count, chance in inputs:
        in_slots.append(convert.slot_key(kind, slot))
        in_list.append(convert.to_ingredient(convert.Element(item_id, count, chance), kind) or Ingredient([]))
    out_slots, out_list = [], []
    for kind, slot, item_id, count, chance in outputs:
        ingredient = convert.to_ingredient(convert.Element(item_id, count, chance), kind)
        if ingredient is not None:
            out_slots.append(convert.slot_key(kind, slot))
            out_list.append(ingredient)
    data = dict(data or {})
    data["input_slots"] = in_slots
    data["output_slots"] = out_slots
    return bridge.Types.Recipe(category_id, in_list, out_list, catalysts=catalysts or None, data=data)


class _Namespace(object):
    """ 简易命名空间；py2 没有 SimpleNamespace """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _BuildSource():  # type: () -> type
    StaticRecipeSource = bridge.Types.StaticRecipeSource

    class MachineRecipeSource(StaticRecipeSource):
        """
        把一个蔚蓝 `RecipesCollection` 喂给 MEI。

        **惰性建表 + 自愈**，不是构造时一次性转换：转换要经 `ItemFactory` 造 Item，
        而 OnRegister 时物品表未必齐。建表早了，候选物品可能造不出来，
        「按材料查用途」的索引也会缺失对应条目。

        标签成员已由原生接口直接查询，不再等待全物品列表请求或标签扫描。
        仍以 `GetAllItems()` 非空作为现有的物品表就绪信号。
        没到之前每次查询重建一次（查询是玩家点出来的，不是每帧路径，代价可接受），
        到了之后重建最后一次就封盘。
        """

        CAN_ENUMERATE = True
        """ 表在自己手上，GetAll 给的就是全部 """

        def __init__(self, category_id, collection, decorate=None):
            # type: (str, any, any) -> None
            StaticRecipeSource.__init__(self, category_id)
            self._collection = collection
            self._sealed = False
            self._decorate = decorate
            """
            可选钩子 `decorate(sb_recipe, parts)` —— **就地改** parts，无返回值。

            parts 是个 dict：`inputs` / `input_slots` / `outputs` / `output_slots` /
            `catalysts` / `data`。给「不止是 N 进 1 出」的机型用，三种真实需求：

              · 机件加工台：加**工具**催化剂（不消耗但决定能不能做）与等级；
              · 模版成型机：`sb_recipe.inputs` 里**没有**刻印模版，它只出现在
                对方的 `GetInputs()` 里，要补一格 —— 补成催化剂（做配方时不扣它）；
              · 水培床：种子与收获相同时 `harvest_outputs` 是**空表**，
                产物其实是种子自己 —— 不补的话整条配方会因"零产物"被丢掉。

            这些**只有那台机器知道**，塞进通用转换里就是在轮子里枚举业务
            （quick_craft.md §0 硬规矩①）。
            """

        # 三个查询入口都要先确保表是新的
    # ==================================================================================================================
        def QueryByOutput(self, item):
            self._Ensure()
            return StaticRecipeSource.QueryByOutput(self, item)

        def QueryByInput(self, item):
            self._Ensure()
            return StaticRecipeSource.QueryByInput(self, item)

        def GetAll(self):
            self._Ensure()
            return StaticRecipeSource.GetAll(self)

        def IsAllComplete(self):
            # 物品表就绪前报不完整，避免把缺少候选物品的配方表当成最终结果。
            return self._sealed

        # 内部
    # ==================================================================================================================
        def _Ensure(self):
            if self._sealed:
                return
            items_ready = bool(GetAllItems())
            self._Rebuild()
            # 物品表已到，完成最后一次重建；标签成员查询不依赖这次全物品请求。
            self._sealed = items_ready

        def _Rebuild(self):
            self.Clear()
            for sb_recipe in self._collection:
                recipe = self._Convert(sb_recipe)
                if recipe is not None:
                    self.Add(recipe)

        def _Convert(self, sb_recipe):  # type: (any) -> any
            """ 一条蔚蓝配方 → 一条 MEI 配方；转不出来返回 None 并记一条日志 """
            in_entries, extra_in = convert.split_inputs(sb_recipe)
            out_entries, extra_out = convert.split_outputs(sb_recipe)

            # 输入里转不出来的**保留成空 Ingredient 而不是删掉** ——
            # 删掉会让槽位与 Data["input_slots"] 错位, 配方页就渲染到错的格子上了。
            # 空 Ingredient 在 MEI 侧的语义正是"这一格空着"(零候选)
            Ingredient = bridge.Types.Ingredient
            in_slots = [key for key, _, _ in in_entries]
            in_ingredients = [convert.to_ingredient(e, k) or Ingredient([])
                              for _, e, k in in_entries]

            # 产物相反: 转不出来的**整条丢掉**(空产物格没有意义), 但槽位表要**一起**丢,
            # 否则 output_slots 与 outputs 就不等长了 —— 两边必须同一趟过滤
            out_slots, out_ingredients = [], []
            for key, element, kind in out_entries:
                ingredient = convert.to_ingredient(element, kind)
                if ingredient is not None:
                    out_slots.append(key)
                    out_ingredients.append(ingredient)

            data = {
                "input_slots": in_slots,
                "output_slots": out_slots,
            }
            # 功率与耗时进 Data 而不是进身份: 蔚蓝那边的 __hash__ 也只看输入输出,
            # 两边对"什么是同一条配方"的判断因此一致
            for name in ("power_cost", "tick_duration", "output_power"):
                value = getattr(sb_recipe, name, None)
                if value is not None:
                    data[name] = value
            if extra_in:
                data["extra_inputs"] = extra_in
            if extra_out:
                data["extra_outputs"] = extra_out

            parts = {
                "inputs": in_ingredients,
                "input_slots": data["input_slots"],
                "outputs": out_ingredients,
                "output_slots": data["output_slots"],
                "catalysts": [],
                "data": data,
            }
            if self._decorate is not None:
                try:
                    self._decorate(sb_recipe, parts)
                except Exception as e:  # noqa  一条配方的附加信息炸了不该丢掉整条
                    bridge.Error("配方附加信息解析失败: {}".format(bridge.ErrorText(e)))
            # 槽位表可能被 decorate 改过, 回写
            data["input_slots"] = parts["input_slots"]
            data["output_slots"] = parts["output_slots"]

            # **零产物检查放在 decorate 之后**: 水培床的产物正是 decorate 补上的。
            #
            # `extra_out` 非空则放行 —— **燃气发电机的唯一产物就是 RF**
            # (outputs 里只有 `energy:0`, 没有任何物品或流体)。
            # 那不是解析失败, 是这台机器本来就不产实体东西;
            # 一律拦掉的话它那条配方会被整条丢弃, 整台机器 0 条配方。
            # 这类配方在 MEI 里仍然查得到 —— "按材料查用途"走的是输入侧,
            # 玩家点甲烷照样能看到"能在燃气发电机里烧成电"。
            if not parts["outputs"] and not extra_out:
                bridge.Error("配方 {} 的产物一个都解析不出, 已跳过".format(
                    type(sb_recipe).__name__))
                return None

            return bridge.Types.Recipe(
                self.CategoryId, parts["inputs"], parts["outputs"],
                catalysts=parts["catalysts"] or None, data=data)

    return MachineRecipeSource


def _BuildListSource():  # type: () -> type
    StaticRecipeSource = bridge.Types.StaticRecipeSource

    class ListRecipeSource(StaticRecipeSource):
        """
        配方由机器模块自己拼的来源（`make()` 返回 MEI 的 `Recipe` 列表）：发酵池、火力 / 地热发电机的数据不是配方集合。

        与 `MachineRecipeSource` 一样**惰性建表 + 自愈**：拼配方要经 `ItemFactory`，OnRegister 时物品表未必齐；
        物品表到了之后建最后一次就封盘。
        """

        CAN_ENUMERATE = True

        def __init__(self, category_id, make):
            # type: (str, any) -> None
            StaticRecipeSource.__init__(self, category_id)
            self._make = make
            self._sealed = False

        def QueryByOutput(self, item):
            self._Ensure()
            return StaticRecipeSource.QueryByOutput(self, item)

        def QueryByInput(self, item):
            self._Ensure()
            return StaticRecipeSource.QueryByInput(self, item)

        def GetAll(self):
            self._Ensure()
            return StaticRecipeSource.GetAll(self)

        def IsAllComplete(self):
            return self._sealed

        def _Ensure(self):
            if self._sealed:
                return
            items_ready = bool(GetAllItems())
            self.Clear()
            try:
                recipes = self._make() or []
            except Exception as e:  # noqa  拼不出来不该带走这次查询
                bridge.Error("{} 的配方拼不出来: {}".format(self.CategoryId, bridge.ErrorText(e)))
                recipes = []
            for recipe in recipes:
                self.Add(recipe)
            self._sealed = items_ready

    return ListRecipeSource
