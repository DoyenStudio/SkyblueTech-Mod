# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl


class CategoryType:
    ITEM = "item"
    FLUID = "fluid"


class RecipeBase:
    recipe_icon_id = "minecraft:barrier"
    render_ui_def_name = ""

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
        0.2 秒触发一次。实际传入的 render_ticks 一秒增加 30。
        """
        pass

    def __hash__(self):
        raise NotImplementedError


class Description(RecipeBase):
    recipe_icon_id = "skybluetech:description_icon"
    render_ui_def_name = "RecipeCheckerUI.description_page"

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
