# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.api.common import GetItemTags


class CategoryType:
    ITEM = "item"
    FLUID = "fluid"
    ENERGY = "energy"


class RecipeBase:
    recipe_icon_id = "minecraft:barrier"
    render_ui_def_name = ""
    minijei_title = None  # type: str | None

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

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        raise NotImplementedError

    def RenderUpdate(self, panel_ctrl, render_ticks):
        # type: (UBaseCtrl, int) -> None
        """
        0.2 秒触发一次。render_ticks 每次比上一次触发多 5。
        """
        pass

    @property
    def collection_key(self):
        raise NotImplementedError

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


class Description(RecipeBase):
    recipe_icon_id = "skybluetech:description_icon"
    render_ui_def_name = "RecipeCheckerLib.description_page"

    def __init__(self, categories_with_ids, title, content):
        # type: (dict[str, list[str]], str, str) -> None
        self.categories_with_ids = categories_with_ids
        self.title = title
        self.content = content

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        panel_ctrl["bg_img/title"].asLabel().SetText(self.title, sync_size=True)
        panel_ctrl["bg_img/content"].asLabel().SetText(self.content, sync_size=True)

    def GetInputs(self):
        return {}

    def GetOutputs(self):
        return self.categories_with_ids

    def __hash__(self):
        return hash(self.title)
