# coding=utf-8
from skybluetech_scripts.tooldelta.api.common import GetItemTags

if 0:
    import typing  # noqa: F401
    from skybluetech_scripts.skybluetech.client.mini_jei.core import RecipeRenderer


class CategoryType:
    ITEM = "item"
    FLUID = "fluid"
    ENERGY = "energy"


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
    def __init__(self, id, count=1):
        # type: (str, float) -> None
        self.id = id
        self.count = count

    def __repr__(self):
        return "io(%s, %d)" % (self.id, self.count)


class Input(Element):
    def __init__(self, id, count=1, is_tag=False):
        # type: (str, float, bool) -> None
        Element.__init__(self, id, count)
        self.is_tag = is_tag

    def match_item_id(self, item_id):
        # type: (str) -> bool
        if self.is_tag:
            return self.id in GetItemTags(item_id, 0)
        else:
            return item_id == self.id

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
            return cls(dct["item"], dct.get("count", 1))

    def to_dict(self):
        if self.is_tag:
            return {"tag": self.id, "count": self.count}
        else:
            return {"item": self.id, "count": self.count}


class Output(Element):
    def __init__(self, id, count=1, prob=1):
        # type: (str, float, float) -> None
        Element.__init__(self, id, count)
        self.prob = prob

    @classmethod
    def from_dict(
        cls,
        dct,  # type: dict
    ):
        return cls(dct["id"], dct.get("count", 1), dct.get("prob", 1))

    def to_dict(self):
        res = {"id": self.id, "count": self.count}
        if self.prob != 1:
            res["prob"] = self.prob
        return res


class Recipe(RecipeBase):
    shaped = False
    "shaped 目前仅决定 collection_key 的生成方式。"

    def __init__(self, inputs, outputs):
        # type: (dict[str, dict[int, Input]], dict[str, dict[int, Output]]) -> None
        self.inputs = inputs
        "配方输入: [配方类型: [槽位: 输入元素]]"
        self.outputs = outputs
        "配方输出: [配方类型: [槽位: 输出元素]]"
        self._collection_key = None
        self._recipe_identifier = None

    def equals(self, other):
        # type: (Recipe | None) -> bool
        if other is None:
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs

    def GetInputs(self):
        return {
            cat: [
                ("tag:" + input.id if input.is_tag else input.id)
                for input in slot2input.values()
            ]
            for cat, slot2input in self.inputs.items()
        }

    def GetOutputs(self):
        return {
            category: [output.id for output in slot2output.values()]
            for category, slot2output in self.outputs.items()
        }

    def Marshal(self):
        from .marshal_utils import MarshalInputs, MarshalOutputs

        return {
            "inputs": MarshalInputs(self.inputs),
            "outputs": MarshalOutputs(self.outputs),
        }

    @classmethod
    def Unmarshal(cls, dct):
        from .marshal_utils import UnmarshalInputs, UnmarshalOutputs

        return cls(
            UnmarshalInputs(dct["inputs"].items()),
            UnmarshalOutputs(dct["outputs"].items()),
        )

    def __hash__(self):
        return hash(self.collection_key)

    @property
    def collection_key(self):
        if self._collection_key is None:
            if self.shaped:
                self._collection_key = tuple(
                    sorted(
                        (
                            (
                                category,
                                tuple(sorted(inputs.items(), key=lambda x: x[0])),
                            )
                            for category, inputs in self.inputs.items()
                        ),
                        key=lambda x: x[0],
                    )
                )
            else:
                self._collection_key = tuple(
                    sorted(
                        (
                            (
                                category,
                                tuple(sorted(inputs.values(), key=lambda x: x.id)),
                            )
                            for category, inputs in self.inputs.items()
                        ),
                        key=lambda x: x[0],
                    )
                )
        return self._collection_key
