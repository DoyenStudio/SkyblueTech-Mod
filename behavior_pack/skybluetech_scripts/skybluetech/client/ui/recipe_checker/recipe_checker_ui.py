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
        self.recipe_ctrls = {}  # type: dict[UBaseCtrl, RecipeBase]
        self.recipes_chain = [params["recipes"]] if params.get("recipes") else []  # type: list[list[tuple[str, str, list[RecipeBase]]]]
        self.update_ticks = 0
        self.current_page = 0
        self.recipes_per_page = 0
        self.total_pages_num = 0
        self.category_double_click_helpers = None

    def OnCreate(self):
        self.left_sections_grid = self.GetElement(
            MAIN_PATH / "left_sections_grid"
        ).asGrid()
        self.title = self.GetElement(MAIN_PATH / "title").asLabel()
        self.recipes_display = self.GetElement(MAIN_PATH / "recipes_display")
        self.prev_page_btn = (
            self
            .GetElement(MAIN_PATH / "title/prev_page_btn")
            .asButton()
            .SetCallback(self.onPrevPage)
        )
        self.next_page_btn = (
            self
            .GetElement(MAIN_PATH / "title/next_page_btn")
            .asButton()
            .SetCallback(self.onNextPage)
        )
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
        self.update_all()
        self.inited = True

    def OnTicking(self):
        self.update_ticks += 1
        if self.update_ticks % 6 == 0:
            for ctrl, rcp in self.recipe_ctrls.items():
                rcp.RenderUpdate(ctrl, self.update_ticks)

    def render_recipes_of_input(self, id, category):
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
        self.update_all()

    def update_all(self):
        RemoveDisplayBoard(self)
        self.update_recipe_categories()
        self.update_current_recipe_page()
        if len(self.recipes_chain) > 1:
            self.back_btn.SetVisible(True)
        else:
            self.back_btn.SetVisible(False)

    def update_recipe_categories(self):
        def after():
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

        if self.looking_category_index >= len(self.recipes_chain[-1]):
            self.looking_category_index = 0
        self.left_sections_grid.SetDimensionAndCall(
            (1, len(self.recipes_chain[-1])), after
        )
        self.current_page = 0
        self.total_pages_num = 0

    def update_current_recipe_page(self):
        _, rcp_title, rcps = self.recipes_chain[-1][self.looking_category_index]
        for ctrls in self.recipe_ctrls:
            ctrls.Remove()
        self.recipe_ctrls.clear()
        display_max_sizey = self.recipes_display.GetSize()[1]
        i = -1
        for i, rcp in enumerate(rcps[self.current_page * self.recipes_per_page :]):
            elem = self.recipes_display.AddElement(
                rcp.render_ui_def_name,
                "recipe%d" % i,
            )
            rcp.RenderInit(elem)
            _, size_y = elem.GetSize()
            elem.SetPos((0, size_y * i))
            self.recipe_ctrls[elem] = rcp
            if size_y * (i + 2) > display_max_sizey:
                break
        if self.total_pages_num == 0:
            self.total_pages_num = int(round(float(len(rcps)) / (i + 1)))
        if self.recipes_per_page == 0:
            self.recipes_per_page = i + 1
        self.title.SetText(
            "%s§f %d/%d" % (rcp_title, self.current_page + 1, self.total_pages_num)
        )

    def onClose(self, params):
        self.RemoveUI()

    def onBack(self, params):
        self.recipes_chain.pop(-1)
        self.update_all()

    def onPrevPage(self, params):
        if self.total_pages_num == 0:
            return
        self.current_page = (self.current_page - 1) % self.total_pages_num
        self.update_current_recipe_page()

    def onNextPage(self, params):
        if self.total_pages_num == 0:
            return
        self.current_page = (self.current_page + 1) % self.total_pages_num
        self.update_current_recipe_page()

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

    @Binder.binding(Binder.BF_ButtonClick, "#recipe_checker.select_category")
    def onSelectCategory(self, params):
        griditem_path = UIPath("/".join(params["ButtonPath"].split("/")[1:-1]))
        griditem = self.GetElement(griditem_path)
        if not self._activated or params["TouchEvent"] != 0:
            return
        click_index = params["#collection_index"]
        if (
            self.category_double_click_helpers
            and self.category_double_click_helpers[click_index]()
        ):
            # BUG: 无法原地双击按钮
            self.render_recipes_of_input(
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
        self.update_all()
