# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag

if 0 > 1:
    import typing  # noqa: F401
    from skybluetech_scripts.skybluetech.client.mini_jei.core import RecipeRenderer


class CategoryType:
    ITEM = "item"
    FLUID = "fluid"
    ENERGY = "energy"
    EXP = "exp"
    EXP_LV = "exp_lv"


class _RecipeMeta(type):
    recipe_classes = {}  # type: dict

    def __init__(self, name, bases, attrs):
        _RecipeMeta.recipe_classes[name] = self

    @classmethod
    def _get_recipe_cls(cls, cls_name):
        # type: (str) -> type[RecipeBase] | None
        return cls.recipe_classes.get(cls_name)


class RecipeBase(object):
    __metaclass__ = _RecipeMeta

    recipe_icon_id = "???"
    renderer = None  # type: type[RecipeRenderer] | None

    def GetInputs(self):
        # type: () -> dict[str, list[str]]
        """
        #### 应返回此配方的输入 {输入类型: 输入物 ID 列表}, 如:

        {
            CategoryType.ITEM: ["minecraft:dirt"],
            CategoryType.FLUID: ["minecraft:water", "skybluetech:raw_oil"]
        }

        如果输入类型为 CategoryType.ITEM, 则可以用 `tag:` 前缀表示此配方接受该类标签。
        """
        raise NotImplementedError

    def GetOutputs(self):
        # type: () -> dict[str, list[str]]
        """
        #### 应返回此配方能产出的 {产出类型: 产出物 ID 列表}, 如:

        {
            CategoryType.ITEM: ["minecraft:dirt"],
            CategoryType.FLUID: ["minecraft:water", "skybluetech:raw_oil"]
        }
        """
        raise NotImplementedError

    def Marshal(self):
        # type: () -> dict
        """
        将配方序列化。

        Returns:
            dict: 配方数据
        """
        raise NotImplementedError

    @classmethod
    def Unmarshal(cls, dct):
        # type: (dict) -> typing.Self
        """
        从配方数据返序列化为配方。

        Args:
            dct (dict): 配方数据。
        """
        raise NotImplementedError

    @classmethod
    def SetRenderer(cls, renderer):
        # type: (type[RecipeRenderer]) -> None
        cls.renderer = renderer

    @classmethod
    def GetRenderer(cls):
        # type: () -> type[RecipeRenderer] | None
        return cls.renderer

    @classmethod
    def GetRendererForced(cls):
        # type: () -> type[RecipeRenderer]
        if cls.renderer is None:
            raise ValueError("No renderer for %s" % cls.__name__)
        return cls.renderer

    @staticmethod
    def GetRecipeCls(cls_name):
        # type: (str) -> type[RecipeBase] | None
        return _RecipeMeta._get_recipe_cls(cls_name)

    @property
    def collection_key(self):
        # type: () -> tuple
        "建议通过继承 Recipe 类实现。 返回此配方的唯一 key"
        raise NotImplementedError

    @property
    def cls_name(self):
        return self.__class__.__name__

    def __hash__(self):
        raise NotImplementedError


class Element(object):
    def __init__(self, id, count=1, aux=0):
        # type: (str, float, int) -> None
        self.id = id
        self.count = count
        self.aux = aux

    def __repr__(self):
        return "io(%s, %d)" % (self.id, self.count)


class Input(Element):
    def __init__(self, id, count=1, aux=0, is_tag=False):
        # type: (str, float, int, bool) -> None
        Element.__init__(self, id, count, aux)
        self.is_tag = is_tag
        self.aux = aux

    def match_item_id(self, item_id, aux=0):
        # type: (str, int) -> bool
        if self.is_tag:
            return item_id in GetItemsByTag(self.id)
        else:
            return item_id == self.id and (self.aux == -1 or self.aux == aux)

    @classmethod
    def from_dict(
        cls,
        dct,  # type: dict | str
    ):
        if isinstance(dct, str):
            return cls(dct)
        if "tag" in dct:
            return cls(dct["tag"], dct.get("count", 1), is_tag=True)
        else:
            return cls(dct["item"], dct.get("count", 1), aux=dct.get("aux", 0))

    def to_dict(self):
        if self.is_tag:
            return {"tag": self.id, "count": self.count}
        else:
            return {"item": self.id, "count": self.count, "aux": self.aux}


class Output(Element):
    def __init__(self, id, count=1, aux=0, prob=1):
        # type: (str, float, int, float) -> None
        Element.__init__(self, id, count, aux=aux)
        self.prob = prob

    @classmethod
    def from_dict(
        cls,
        dct,  # type: dict
    ):
        if "tag" in dct:
            return cls(dct["tag"], dct.get("count", 1), prob=dct.get("prob", 1))
        else:
            return cls(
                dct["id"],
                dct.get("count", 1),
                aux=dct.get("aux", 0),
                prob=dct.get("prob", 1),
            )

    def to_dict(self):
        res = {"id": self.id, "count": self.count, "aux": self.aux}
        if self.prob != 1:
            res["prob"] = self.prob
        return res


class Recipe(RecipeBase):

    def __init__(
        self,
        inputs=None,  # type: dict[str, dict[int, Input]] | None
        outputs=None,  # type: dict[str, dict[int, Output]] | None
        inputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Input]]] | None
        outputs_unordered=None,  # type: dict[str, dict[tuple[int, ...], list[Output]]] | None
    ):
        self.inputs = inputs
        "固定槽位配方输入: [配方类型: [槽位: 输入元素]]"
        self.outputs = outputs
        "固定槽位配方输出: [配方类型: [槽位: 输出元素]]"
        self.inputs_unordered = inputs_unordered
        "无序槽位配方输入: [配方类型: [槽位元组]: 输入元素列表]"
        self.outputs_unordered = outputs_unordered
        "无序槽位配方输出: [配方类型: [槽位元组]: 输出元素列表]"
        self._collection_key = None
        self._recipe_identifier = None

    def equals(self, other):
        # type: (Recipe | None) -> bool
        if other is None:
            return False
        return (
            self.inputs == other.inputs
            and self.outputs == other.outputs
            and self.inputs_unordered == other.inputs_unordered
            and self.outputs_unordered == other.outputs_unordered
        )

    def GetInputs(self):
        inputs = {
            cat: [
                ("tag:" + input.id if input.is_tag else input.id)
                for input in slot2input.values()
            ]
            for cat, slot2input in (self.inputs or {}).items()
        }
        for cat, slot2input in (self.inputs_unordered or {}).items():
            inputs.setdefault(cat, []).extend(
                "tag:" + input.id if input.is_tag else input.id
                for input_list in slot2input.values()
                for input in input_list
            )
        return inputs

    def GetOutputs(self):
        # TODO: 支持 item aux
        outputs = {
            category: [output.id for output in slot2output.values()]
            for category, slot2output in list((self.outputs or {}).items())
        }
        for category, slot2output in (self.outputs_unordered or {}).items():
            outputs.setdefault(category, []).extend(
                output.id
                for output_list in slot2output.values()
                for output in output_list
            )
        return outputs

    def Marshal(self):
        from .marshal_utils import (
            MarshalOrderedInputs,
            MarshalOrderedOutputs,
            MarshalUnorderedInputs,
            MarshalUnorderedOutputs,
        )

        return {
            "inputs": MarshalOrderedInputs(self.inputs) if self.inputs else None,
            "outputs": MarshalOrderedOutputs(self.outputs) if self.outputs else None,
            "inputs_unordered": MarshalUnorderedInputs(self.inputs_unordered)
            if self.inputs_unordered
            else None,
            "outputs_unordered": MarshalUnorderedOutputs(self.outputs_unordered)
            if self.outputs_unordered
            else None,
        }

    @classmethod
    def Unmarshal(cls, dct):
        from .marshal_utils import (
            UnmarshalOrderedInputs,
            UnmarshalOrderedOutputs,
            UnmarshalUnorderedInputs,
            UnmarshalUnorderedOutputs,
        )

        inputs = dct["inputs"]
        inputs_unordered = dct["inputs_unordered"]
        outputs = dct["outputs"]
        outputs_unordered = dct["outputs_unordered"]

        if inputs is not None:
            inputs = UnmarshalOrderedInputs(inputs)
        if inputs_unordered is not None:
            inputs_unordered = UnmarshalUnorderedInputs(inputs_unordered)
        if outputs is not None:
            outputs = UnmarshalOrderedOutputs(outputs)
        if outputs_unordered is not None:
            outputs_unordered = UnmarshalUnorderedOutputs(outputs_unordered)

        return cls(
            inputs=inputs,
            outputs=outputs,
            inputs_unordered=inputs_unordered,
            outputs_unordered=outputs_unordered,
        )
