# coding=utf-8

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

    def __hash__(self):
        raise NotImplementedError
