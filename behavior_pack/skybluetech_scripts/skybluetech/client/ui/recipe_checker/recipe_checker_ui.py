# coding=utf-8
from skybluetech_scripts.tooldelta.ui import (
    ToolDeltaScreen,
    RegistToolDeltaScreen,
    UIPath,
    Binder,
    UBaseCtrl,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client.control import OnKeyPressInGame
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ....common.mini_jei import (
    CategoryType,
    RecipeBase,
    GetRecipesByOutput,
    CreateDisplayBoard,
    NeedRemoveDisplayBoard,
    RemoveDisplayBoard,
    GetDoubleClickDetecter,
)

MAIN_PATH = UIPath(
    "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
)


@RegistToolDeltaScreen("RecipeCheckerUI.main")
class RecipeCheckerUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.looking_category_index = 0
        self.inited = False
        self.ctrls_in_fgrid = {}  # type: dict[UBaseCtrl, RecipeBase]
        self.recipes_chain = [params["recipes"]] if params.get("recipes") else []  # type: list[list[tuple[str, str, list[RecipeBase]]]]
        self.update_ticks = 0

    def OnCreate(self):
        self.left_sections_grid = self.GetElement(
            MAIN_PATH / "left_sections_grid"
        ).asGrid()
        self.title = self.GetElement(MAIN_PATH / "title").asLabel()
        self.recipes_view = self.GetElement(MAIN_PATH / "recipes_view").asScrollView()
        self.close_btn = (
            self
            .GetElement(MAIN_PATH / "close_btn")
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

    def OnTicking(self):
        self.update_ticks += 1
        if self.update_ticks % 6 == 0:
            for ctrl, rcp in self.ctrls_in_fgrid.items():
                rcp.RenderUpdate(ctrl, self.update_ticks)

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.isDown and event.key == event.KeyBoardType.KEY_ESCAPE:
            self.RemoveUI()

    def PushRecipes(self, recipes):
        # type: (dict[tuple[str, str], list[RecipeBase]]) -> None
        r = [
            (recipe_icon_id, recipe_name, recipes[(recipe_icon_id, recipe_name)])
            for (recipe_icon_id, recipe_name) in recipes
        ]
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
        for i, (rcp_icon_id, _, _) in enumerate(self.recipes_chain[-1]):
            category_panel = self.left_sections_grid.GetGridItem(0, i)
            category_panel["item_renderer"].asItemRenderer().SetUiItem(
                Item(rcp_icon_id)
            )
            if i == self.looking_category_index:
                category_panel.SetLayer(3)
            else:
                category_panel.SetLayer(0)
        self.category_double_click_helpers = [
            GetDoubleClickDetecter() for _ in self.recipes_chain[-1]
        ]

    def updateCurrentRecipePage(self):
        rcp_fake_grid = self.recipes_view.GetContent()
        _, rcp_title, rcps = self.recipes_chain[-1][self.looking_category_index]
        self.title.SetText(rcp_title)
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
            rcp.RenderInit(elem)
            last_xize, last_ysize = elem.GetSize()
            elem.SetPos((0, last_ysize * i))
            self.ctrls_in_fgrid[elem] = rcp
        rcp_fake_grid.SetSize((last_xize, last_ysize * len(rcps)))

    @Binder.binding(Binder.BF_ButtonClick, "#recipe_checker.select_category")
    def onSelectCategory(self, params):
        griditem_path = UIPath("/".join(params["ButtonPath"].split("/")[1:-1]))
        griditem = self.GetElement(griditem_path)
        if not self._activated or params["TouchEvent"] != 0:
            return
        click_index = params["#collection_index"]
        if self.category_double_click_helpers[click_index]():
            # BUG: 无法原地双击按钮
            self.renderRecipesOfInput(
                self.left_sections_grid
                .GetGridItem(0, click_index)["item_renderer"]
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
                offset = -40
            else:
                offset = 40
            CreateDisplayBoard(
                griditem,
                GetItemHoverName(
                    griditem["item_renderer"].asItemRenderer().GetUiItem()[0]
                ),
            ).SetPos((x, y + offset)).SetLayer(20)
            return
        self.looking_category_index = click_index
        self.updateAll()

    def renderRecipesOfInput(self, id, category):
        # type: (str, str) -> None
        recipe_dic = {}  # type: dict[tuple[str, str], list[RecipeBase]]
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
            recipe_dic.setdefault(
                (
                    rcp.recipe_icon_id,
                    rcp.minijei_title or GetItemHoverName(rcp.recipe_icon_id),
                ),
                [],
            ).append(rcp)
        self.PushRecipes(recipe_dic)
        self.updateAll()
