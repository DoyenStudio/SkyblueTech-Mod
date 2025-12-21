# coding=utf-8
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.ui import UScreenNode, RegistScreen, SNode, ViewBinder, UBaseCtrl
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client.control import OnKeyPressInGame
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from skybluetech_scripts.tooldelta.plugins.recipe_obj import CraftingRecipeRes, FurnaceRecipe
from ...define.machine_config.define import MachineRecipe
from .utils import RenderMachineRecipe, RenderCraftingTableRecipe, RenderFurnaceRecipe

MAIN_PATH = SNode("/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel")

ESC = GetMinecraftEnum().KeyBoardType.KEY_ESCAPE


@RegistScreen("RecipeCheckerUI.main")
class RecipeCheckerUI(UScreenNode):

    def __init__(self, namespace, name, param=None):
        UScreenNode.__init__(self, namespace, name, param)
        self.loaded_recipes = [] # type: list[tuple[str, list[MachineRecipe] | list[CraftingRecipeRes] | list[FurnaceRecipe]]]
        self.looking_catrgory_index = 0
        self.inited = False
        self.ctrls_in_fgrid = [] # type: list[UBaseCtrl]

    def Create(self):
        UScreenNode.Create(self)
        self.left_sections_grid = self.GetElement(MAIN_PATH / "left_sections_grid").asGrid()
        self.title = self.GetElement(MAIN_PATH / "title").asLabel()
        self.recipes_view = self.GetElement(MAIN_PATH / "recipes_view").asScrollView()
        self.close_btn = self.GetElement(MAIN_PATH / "close_btn").asButton()
        self.close_btn.SetCallback(self.onClose) 
        if self.loaded_recipes:
            self.updateRecipeCategories()
            self.updateCurrentRecipePage()
        self.inited = True

    def onClose(self, params):
        self.RemoveUI()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown == 1 and event.key == ESC:
            self.RemoveUI()

    def SetRecipes(self, recipes):
        # type: (dict[str, list[MachineRecipe]]) -> None
        self.loaded_recipes = [(recipe_name, recipes[recipe_name]) for recipe_name in recipes]

    def updateRecipeCategories(self):
        self.left_sections_grid.SetGridDimension((1, len(self.loaded_recipes)))
        self.left_sections_grid.ExecuteAfterUpdate(self.updateRecipeCategoriesNext)

    def updateRecipeCategoriesNext(self):
        for i, (rcp_name, _) in enumerate(self.loaded_recipes):
            category_panel = self.left_sections_grid.GetGridItem(0, i)
            category_panel["item_renderer"].asItemRenderer().SetUiItem(Item(rcp_name))

    def updateCurrentRecipePage(self):
        rcp_fake_grid = self.recipes_view.GetContent()
        rcp_name, rcps = self.loaded_recipes[self.looking_catrgory_index]
        self.title.SetText(GetItemHoverName(rcp_name))
        for fgrid_ctrl in self.ctrls_in_fgrid:
            fgrid_ctrl.Remove()
        self.ctrls_in_fgrid[:] = []
        last_xize = 0
        last_ysize = 0
        for i, rcp in enumerate(rcps):
            rcp_ctrl_suffix = rcp_name
            if rcp_ctrl_suffix.startswith("minecraft:"):
                rcp_ctrl_suffix = rcp_name[len("minecraft:"):]
            elif rcp_ctrl_suffix.startswith("skybluetech:"):
                rcp_ctrl_suffix = rcp_name[len("skybluetech:"):]
            elem = rcp_fake_grid.AddElement(
                "RecipeCheckerUI." + rcp_ctrl_suffix + "_recipes",
                "fgrid_item%d" % i,
            )
            last_xize, last_ysize = elem.GetSize()
            elem.SetPos((0, last_ysize * i))
            self.ctrls_in_fgrid.append(elem)
            if isinstance(rcp, MachineRecipe):
                RenderMachineRecipe(elem, rcp)
            elif isinstance(rcp, CraftingRecipeRes):
                RenderCraftingTableRecipe(elem, rcp)
            elif isinstance(rcp, FurnaceRecipe):
                RenderFurnaceRecipe(elem, rcp)
        rcp_fake_grid.SetSize((last_xize, last_ysize * len(rcps)))

    @ViewBinder.binding(ViewBinder.BF_ButtonClick, "#recipe_checker.select_category") # pyright: ignore[reportOptionalCall]
    def onSelectCategory(self, params):
        if not self.activated:
            return
        print(params)
        return
        for i, (rcp_name, _) in enumerate(self.loaded_recipes):
            category_panel = self.left_sections_grid.GetGridItem(1, i+1)
            if i == self.looking_catrgory_index:
                category_panel.SetLayer(3)
            else:
                category_panel.SetLayer(0)
