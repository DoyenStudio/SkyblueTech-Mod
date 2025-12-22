# coding=utf-8
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.ui import UScreenNode, RegistScreen, SNode, ViewBinder, UBaseCtrl
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client.control import OnKeyPressInGame
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ...define.machine_config.define import MachineRecipe
from ...mini_jei import RecipeBase, GetRecipesByInput, GetRecipesByOutput, GenericCraftingTableRecipe, GenericFurnaceRecipe
from .utils import RenderGenericMachineRecipe, RenderCraftingTableRecipe, RenderFurnaceRecipe, ClearDisplayBoard

MAIN_PATH = SNode("/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel")

ESC = GetMinecraftEnum().KeyBoardType.KEY_ESCAPE


@RegistScreen("RecipeCheckerUI.main")
class RecipeCheckerUI(UScreenNode):

    def __init__(self, namespace, name, param=None):
        UScreenNode.__init__(self, namespace, name, param)
        self.looking_catrgory_index = 0
        self.inited = False
        self.ctrls_in_fgrid = [] # type: list[UBaseCtrl]
        self.recipes_chain = [] # type: list[list[tuple[str, list[RecipeBase]]]]

    def Create(self):
        UScreenNode.Create(self)
        self.left_sections_grid = self.GetElement(MAIN_PATH / "left_sections_grid").asGrid()
        self.title = self.GetElement(MAIN_PATH / "title").asLabel()
        self.recipes_view = self.GetElement(MAIN_PATH / "recipes_view").asScrollView()
        self.close_btn = self.GetElement(MAIN_PATH / "close_btn").asButton().SetCallback(self.onClose)
        self.back_btn = self.GetElement(MAIN_PATH / "back_btn").asButton().SetCallback(self.onBack)
        self.back_btn.SetVisible(False)
        self.updateAll()
        self.inited = True

    def onClose(self, params):
        self.RemoveUI()

    def onBack(self, params):
        self.recipes_chain.pop(-1)
        self.updateAll()

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown == 1 and event.key == ESC:
            self.RemoveUI()

    def PushRecipes(self, recipes):
        # type: (dict[str, list[RecipeBase]]) -> None
        r = [(recipe_name, recipes[recipe_name]) for recipe_name in recipes]
        self.recipes_chain.append(r)

    def updateAll(self):
        ClearDisplayBoard(self)
        self.updateRecipeCategories()
        self.updateCurrentRecipePage()
        if len(self.recipes_chain) > 1:
            self.back_btn.SetVisible(True)
        else:
            self.back_btn.SetVisible(False)

    def updateRecipeCategories(self):
        if self.looking_catrgory_index >= len(self.recipes_chain[-1]):
            self.looking_catrgory_index = 0
        last_len = self.left_sections_grid.GetGridDimension()[1]
        expected_len = len(self.recipes_chain[-1])
        if last_len != expected_len:
            self.left_sections_grid.SetGridDimension((1, len(self.recipes_chain[-1])))
            self.left_sections_grid.ExecuteAfterUpdate(self.updateRecipeCategoriesNext)
        else:
            self.updateRecipeCategoriesNext()

    def updateRecipeCategoriesNext(self):
        for i, (rcp_name, _) in enumerate(self.recipes_chain[-1]):
            category_panel = self.left_sections_grid.GetGridItem(0, i)
            category_panel["item_renderer"].asItemRenderer().SetUiItem(Item(rcp_name))
            if i == self.looking_catrgory_index:
                category_panel.SetLayer(3)
            else:
                category_panel.SetLayer(0)

    def updateCurrentRecipePage(self):
        rcp_fake_grid = self.recipes_view.GetContent()
        rcp_name, rcps = self.recipes_chain[-1][self.looking_catrgory_index]
        self.title.SetText(GetItemHoverName(rcp_name))
        for fgrid_ctrl in self.ctrls_in_fgrid:
            fgrid_ctrl.Remove()
        self.ctrls_in_fgrid[:] = []
        last_xize = 0
        last_ysize = 0
        for i, rcp in enumerate(rcps):
            elem = rcp_fake_grid.AddElement(
                rcp.render_ui_def_name,
                "fgrid_item%d" % i,
            )
            last_xize, last_ysize = elem.GetSize()
            elem.SetPos((0, last_ysize * i))
            self.ctrls_in_fgrid.append(elem)
            if isinstance(rcp, MachineRecipe):
                RenderGenericMachineRecipe(elem, rcp)
            elif isinstance(rcp, GenericCraftingTableRecipe):
                RenderCraftingTableRecipe(elem, rcp)
            elif isinstance(rcp, GenericFurnaceRecipe):
                RenderFurnaceRecipe(elem, rcp)
        rcp_fake_grid.SetSize((last_xize, last_ysize * len(rcps)))

    @ViewBinder.binding(ViewBinder.BF_ButtonClick, "#recipe_checker.select_category") # pyright: ignore[reportOptionalCall]
    def onSelectCategory(self, params):
        if not self.activated or params["TouchEvent"] != 0:
            return
        self.looking_catrgory_index = params["#collection_index"]
        self.updateAll()

    def renderRecipesOfInput(self, id, category):
        # type: (str, str) -> None
        recipe_dic = {} # type: dict[str, list[RecipeBase]]
        rcps = GetRecipesByOutput(category, id)
        if not rcps:
            print ("Failed to find recipes for %s %s" % (category, id,))
            return
        for rcp in rcps:
            recipe_dic.setdefault(rcp.recipe_icon_id, []).append(rcp)
        self.PushRecipes(recipe_dic)
        self.updateAll()


