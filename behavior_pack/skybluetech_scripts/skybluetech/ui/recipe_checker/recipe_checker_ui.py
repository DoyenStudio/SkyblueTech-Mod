# coding=utf-8
from mod.client.extraClientApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.ui import (
    UScreenNode,
    RegistScreen,
    SNode,
    ViewBinder,
    UBaseCtrl,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client.control import OnKeyPressInGame
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ...define.machine_config.define import MachineRecipe
from ..machines.utils import UpdateGenericProgressL2R
from ...mini_jei import (
    CategoryType,
    RecipeBase,
    GetRecipesByInput,
    GetRecipesByOutput,
    GenericCraftingTableRecipe,
    GenericFurnaceRecipe,
)
from .utils import (
    CreateDisplayBoard,
    RemoveDisplayBoard,
    NeedRemoveDisplayBoard,
    GetDoubleClickDetecter,
    RenderGenericMachineRecipe,
    RenderCraftingTableRecipe,
    RenderFurnaceRecipe,
)

MAIN_PATH = SNode(
    "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
)

ESC = GetMinecraftEnum().KeyBoardType.KEY_ESCAPE


@RegistScreen("RecipeCheckerUI.main")
class RecipeCheckerUI(UScreenNode):
    def __init__(self, namespace, name, param=None):
        UScreenNode.__init__(self, namespace, name, param)
        self.looking_category_index = 0
        self.inited = False
        self.ctrls_in_fgrid = {}  # type: dict[UBaseCtrl, RecipeBase]
        self.recipes_chain = []  # type: list[list[tuple[str, list[RecipeBase]]]]
        self.update_ticks = 0

    def Create(self):
        UScreenNode.Create(self)
        self.left_sections_grid = self.GetElement(
            MAIN_PATH / "left_sections_grid"
        ).asGrid()
        self.title = self.GetElement(MAIN_PATH / "title").asLabel()
        self.recipes_view = self.GetElement(MAIN_PATH / "recipes_view").asScrollView()
        self.close_btn = (
            self.GetElement(MAIN_PATH / "close_btn")
            .asButton()
            .SetCallback(self.onClose)
        )
        self.back_btn = (
            self.GetElement(MAIN_PATH / "back_btn").asButton().SetCallback(self.onBack)
        )
        self.back_btn.SetVisible(False)
        self.updateAll()
        self.inited = True

    def onClose(self, params):
        self.RemoveUI()

    def onBack(self, params):
        self.recipes_chain.pop(-1)
        self.updateAll()

    def Update(self):
        self.update_ticks += 1
        if self.update_ticks % 6 == 0:
            for ctrl, rcp in self.ctrls_in_fgrid.items():
                self.updateFakegridCtrl(ctrl, rcp)

    def OnCurrentPageKeyEvent(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown == 1 and event.key == ESC:
            self.RemoveUI()

    def PushRecipes(self, recipes):
        # type: (dict[str, list[RecipeBase]]) -> None
        r = [(recipe_name, recipes[recipe_name]) for recipe_name in recipes]
        if len(self.recipes_chain) > 64:
            self.recipes_chain.pop(4)
        self.recipes_chain.append(r)

    def updateAll(self):
        RemoveDisplayBoard(self)
        self.updateRecipeCategories()
        self.updateCurrentRecipePage()
        if len(self.recipes_chain) > 1:
            self.back_btn.SetVisible(True)
        else:
            self.back_btn.SetVisible(False)

    def updateRecipeCategories(self):
        if self.looking_category_index >= len(self.recipes_chain[-1]):
            self.looking_category_index = 0
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
            if i == self.looking_category_index:
                category_panel.SetLayer(3)
            else:
                category_panel.SetLayer(0)
        self.category_double_click_helpers = [
            GetDoubleClickDetecter() for _ in self.recipes_chain[-1]
        ]

    def updateCurrentRecipePage(self):
        rcp_fake_grid = self.recipes_view.GetContent()
        rcp_name, rcps = self.recipes_chain[-1][self.looking_category_index]
        self.title.SetText(GetItemHoverName(rcp_name))
        for fgrid_ctrl in self.ctrls_in_fgrid:
            fgrid_ctrl.Remove()
        self.ctrls_in_fgrid.clear()
        last_xize = 0
        last_ysize = 0
        for i, rcp in enumerate(rcps):
            elem = rcp_fake_grid.AddElement(
                rcp.render_ui_def_name,
                "fgrid_item%d" % i,
            )
            last_xize, last_ysize = elem.GetSize()
            elem.SetPos((0, last_ysize * i))
            self.ctrls_in_fgrid[elem] = rcp
            if isinstance(rcp, MachineRecipe):
                RenderGenericMachineRecipe(elem, rcp)
            elif isinstance(rcp, GenericCraftingTableRecipe):
                RenderCraftingTableRecipe(elem, rcp)
            elif isinstance(rcp, GenericFurnaceRecipe):
                RenderFurnaceRecipe(elem, rcp)
        rcp_fake_grid.SetSize((last_xize, last_ysize * len(rcps)))

    @ViewBinder.binding(ViewBinder.BF_ButtonClick, "#recipe_checker.select_category")  # pyright: ignore[reportOptionalCall]
    def onSelectCategory(self, params):
        griditem_path = SNode("/".join(params["ButtonPath"].split("/")[1:-1]))
        griditem = self.GetElement(griditem_path)
        if not self.activated or params["TouchEvent"] != 0:
            return
        click_index = params["#collection_index"]
        if self.category_double_click_helpers[click_index]():
            self.renderRecipesOfInput(
                self.left_sections_grid.GetGridItem(0, click_index)["item_renderer"]
                .asItemRenderer()
                .GetUiItem()[0],
                CategoryType.ITEM,
            )
            return
        if self.looking_category_index == click_index:
            if NeedRemoveDisplayBoard(griditem):
                RemoveDisplayBoard(self)
                return
            x, y = griditem.GetRootPos()
            if y > 100:
                offset = -20
            else:
                offset = 20
            CreateDisplayBoard(
                griditem, 
                    GetItemHoverName(
                    griditem["item_renderer"]
                    .asItemRenderer()
                    .GetUiItem()[0]
                )
            ).SetPos((x, y + offset))
            return
        self.looking_category_index = click_index
        self.updateAll()

    def renderRecipesOfInput(self, id, category):
        # type: (str, str) -> None
        recipe_dic = {}  # type: dict[str, list[RecipeBase]]
        rcps = GetRecipesByOutput(category, id)
        if not rcps:
            print(
                "Failed to find recipes for %s %s"
                % (
                    category,
                    id,
                )
            )
            return
        for rcp in rcps:
            recipe_dic.setdefault(rcp.recipe_icon_id, []).append(rcp)
        self.PushRecipes(recipe_dic)
        self.updateAll()

    def updateFakegridCtrl(self, ctrl, rcp):
        # type: (UBaseCtrl, RecipeBase) -> None
        if isinstance(rcp, MachineRecipe):
            progress_bar = ctrl["progress"]
            run_time = self.update_ticks * 0.66 % rcp.tick_duration
            UpdateGenericProgressL2R(progress_bar, run_time / rcp.tick_duration)
            
