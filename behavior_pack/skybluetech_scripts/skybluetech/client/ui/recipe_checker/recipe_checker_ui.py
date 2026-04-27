# coding=utf-8
from skybluetech_scripts.tooldelta.ui import (
    ToolDeltaScreen,
    RegistToolDeltaScreen,
    UIPath,
    Binder,
    UBaseCtrl,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import (
    OnKeyPressInGame,
    ScreenSizeChangedClientEvent,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName, GetScreenSize
from skybluetech_scripts.skybluetech.common.mini_jei import CategoryType, RecipeBase
from skybluetech_scripts.skybluetech.client.mini_jei import RecipeRenderer
from .favourite_items import GetFavourites, favourite_items_idauxs
from .render_utils import CreateDescBoard

MAIN_PATH = UIPath(
    "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
)
LEFT_CONTENT_PATH = MAIN_PATH / "left_content"
MIDDLE_CONTENT_PATH = MAIN_PATH / "middle_content"


@RegistToolDeltaScreen("RecipeCheckerUI.main")
class RecipeCheckerUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.looking_category_index = 0
        self.inited = False
        self.recipe_ctrls = {}  # type: dict[UBaseCtrl, RecipeRenderer]
        self.recipes_chain = [params["recipes"]] if params.get("recipes") else []  # type: list[list[tuple[str, str, list[RecipeBase]]]]
        self.update_ticks = 0
        self.current_page = 0
        self.recipes_per_page = 0
        self.total_pages_num = 0

    def OnCreate(self):
        self.left_sections_grid = self.GetElement(
            MIDDLE_CONTENT_PATH / "left_sections_grid"
        ).asGrid()
        self.title = self.GetElement(MIDDLE_CONTENT_PATH / "title").asLabel()
        self.recipes_display = self.GetElement(MIDDLE_CONTENT_PATH / "recipes_display")
        self.prev_page_btn = (
            self
            .GetElement(MIDDLE_CONTENT_PATH / "prev_page_btn")
            .asButton()
            .SetCallback(self.onPrevPage)
        )
        self.next_page_btn = (
            self
            .GetElement(MIDDLE_CONTENT_PATH / "next_page_btn")
            .asButton()
            .SetCallback(self.onNextPage)
        )
        self.close_btn = (
            self
            .GetElement(MIDDLE_CONTENT_PATH / "close_btn")
            .asButton()
            .SetCallback(self.onClose)
        )
        self.back_btn = (
            self
            .GetElement(MIDDLE_CONTENT_PATH / "back_btn")
            .asButton()
            .SetCallback(self.onBack)
        )
        self.back_btn.SetVisible(False)
        self.update_left_content_size()
        self.update_all()
        self.inited = True

    def OnTicking(self):
        self.update_ticks += 1
        if self.update_ticks % 6 == 0:
            for ctrl, rcp in self.recipe_ctrls.items():
                rcp.RenderUpdate(ctrl, self.update_ticks)

    def PushRecipes(self, recipes, update=True):
        # type: (dict[tuple[str, str], list[RecipeBase]], bool) -> None
        r = [
            (recipe_icon_id, recipe_name, recipe)
            for (recipe_icon_id, recipe_name), recipe in recipes.items()
        ]
        if len(self.recipes_chain) > 64:
            self.recipes_chain.pop(4)
        self.recipes_chain.append(r)
        if update:
            self.recipes_per_page = 0
            self.update_all()

    def update_left_content_size(self):
        screen_size_x, screen_size_y = GetScreenSize()
        middle_content_size_x = (
            self.GetElement(MIDDLE_CONTENT_PATH).GetSize()[0] / 2
            + self.GetElement(MIDDLE_CONTENT_PATH / "left_sections_grid").GetSize()[0]
        )
        self.GetElement(LEFT_CONTENT_PATH).SetSize(
            (
                screen_size_x / 2 - middle_content_size_x,
                screen_size_y,
            ),
            resize_children=True,
        )

    def update_all(self):
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

        if self.looking_category_index >= len(self.recipes_chain[-1]):
            self.looking_category_index = 0
        self.left_sections_grid.SetDimensionAndCall(
            (1, len(self.recipes_chain[-1])), after
        )
        self.current_page = 0
        self.total_pages_num = 0

    def update_current_recipe_page(self):
        _, rcp_title, rcps = self.recipes_chain[-1][self.looking_category_index]
        for ctrl, recipe_renderer in self.recipe_ctrls.items():
            recipe_renderer.DeRender(ctrl)
            ctrl.Remove()
        self.recipe_ctrls.clear()
        display_max_sizey = self.recipes_display.GetSize()[1]
        i = -1
        for i, rcp in enumerate(rcps[self.current_page * self.recipes_per_page :]):
            rcp_renderer_cls = rcp.GetRenderer()
            if rcp_renderer_cls is None:
                continue
            rcp_renderer = rcp_renderer_cls(rcp)
            elem = self.recipes_display.AddElement(
                rcp_renderer.render_ui_def_name,
                "recipe%d" % i,
            )
            rcp_renderer.RenderInit(elem)
            rcp_renderer.RenderUpdate(elem, self.update_ticks)
            _, size_y = elem.GetSize()
            elem.SetPos((0, size_y * i))
            self.recipe_ctrls[elem] = rcp_renderer
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

    @ToolDeltaScreen.Listen(ScreenSizeChangedClientEvent)
    def onScreenSizeChanged(self, _):
        ExecLater(0, self.update_left_content_size)

    @Binder.binding(Binder.BF_ButtonClick, "#recipe_checker.select_category")
    def onSelectCategory(self, params):
        griditem_path = UIPath("/".join(params["ButtonPath"].split("/")[1:-1]))
        griditem = self.GetElement(griditem_path)
        if not self._activated or params["TouchEvent"] != 0:
            return
        click_index = params["#collection_index"]
        if self.looking_category_index != click_index:
            self.looking_category_index = click_index
            self.update_all()
        else:
            x, y = griditem.GetRootPos()
            if y > 400:
                offset = -10
            else:
                offset = 10
            selected_item_id = griditem["item_renderer"].asItemRenderer().GetUiItem()[0]
            CreateDescBoard(
                griditem,
                (x + 20, y + offset),
                CategoryType.ITEM,
                selected_item_id,
                selected_item_id,
                GetItemHoverName(selected_item_id),
            )

    @Binder.binding_collection(
        Binder.BF_BindInt,
        "recipe_check_ui_favourite_items",
        "#RecipeCheckerUI.favourite_item_nums",
    )
    def onGetFavRecipeResultItem(self, args):
        # type: (int) -> int
        return len(GetFavourites())

    @Binder.binding_collection(
        Binder.BF_BindInt,
        "recipe_check_ui_favourite_items",
        "#RecipeCheckerUI.facourite_item_idaux",
    )
    def onGetFavRecipeSrcItem(self, idx):
        if idx >= len(favourite_items_idauxs):
            return 131072
        return favourite_items_idauxs[idx]

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#RecipeCheckerUI.favourite_item_select",
    )
    def onSelectFavouriteItem(self, params):
        # type: (dict) -> None
        idx = params["#collection_index"]
        if idx >= len(favourite_items_idauxs):
            return
        button_path = params["ButtonPath"][len("main/") :]
        button = self.GetElement(button_path)
        x, y = button.GetRootPos()
        category, item_id, display_item_id = GetFavourites()[idx]
        CreateDescBoard(
            button._parent,
            (x + 20, y),
            category,
            item_id,
            display_item_id,
            GetItemHoverName(display_item_id),
        )
