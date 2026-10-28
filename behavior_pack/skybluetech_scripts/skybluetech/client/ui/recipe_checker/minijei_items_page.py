# coding=utf-8
from skybluetech_scripts.skybluetech.common.export import (
    MOD_NAMESPACE,
    GetCategoryOptions,
)
from skybluetech_scripts.skybluetech.common.mini_jei import CategoryType
from skybluetech_scripts.skybluetech.client.ui.recipe_checker.favourite_items import (
    GetFavourites,
)
from skybluetech_scripts.tooldelta.api.client import (
    GetItemFormattedHoverText,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import (
    MouseWheelClientEvent,
    OnKeyPressInGame,
    ScreenSizeChangedClientEvent,
)
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetAllItems
from skybluetech_scripts.tooldelta.extensions.dropdown import Dropdown
from skybluetech_scripts.tooldelta.ui import (
    Binder,
    RegistToolDeltaScreen,
    ToolDeltaScreen,
    UIPath,
)

from .recipe_checker_ui import RecipeCheckerUI
from .utils import RecipeCategoriesData

if 0 > 1:
    import typing

MAIN_PATH = UIPath(
    "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"
)
CONTENT_PATH = MAIN_PATH / "panel"  # 全屏外层 screen_root -> panel
BG_PATH = CONTENT_PATH / "bg1"
FAVOURITES_BG_PATH = CONTENT_PATH / "bg2"
GRID_PANEL_PATH = BG_PATH / "grid_panel"
ITEMS_GRID_PATH = GRID_PANEL_PATH / "jei_items_grid"
CATEGORY_COMBO_PATH = BG_PATH / "category_combo"
PAGE_LABEL_PATH = BG_PATH / "page_label"
PREV_PAGE_BTN_PATH = BG_PATH / "prev_page_btn"
NEXT_PAGE_BTN_PATH = BG_PATH / "next_page_btn"
CLOSE_BTN_PATH = BG_PATH / "close_btn"

ITEMS_COLLECTION = "minijei_item_list_grid"
FAVOURITES_COLLECTION = "minijei_favourites_grid"
MOD_CATEGORY_PREFIX = MOD_NAMESPACE + ":"
EMPTY_ITEM_ID_AUX = 131072
GRID_ITEM_SIZE_Y = 20.0
MAX_ITEMS_PER_PAGE = 200
ITEM_NAME_CACHE = {}  # type: dict[str, str]
ALL_ITEM_IDS_CACHE = []  # type: list[str]
ITEM_CATEGORIES_CACHE = {}  # type: dict[str, str]
ITEM_ID_AUX_CACHE = {}  # type: dict[str, int]


def _get_item_category(item_basic_info):
    # type: (object) -> str
    return getattr(
        item_basic_info,
        "category",
        getattr(item_basic_info, "itemCategory", "none") or "none",
    )


def _get_search_text(text):
    # type: (str) -> str
    return (text or "").replace("§r", "").replace("§f", "").strip().lower()


def _scan_all_items():
    # type: () -> None
    for item_id in sorted(GetAllItems()):
        try:
            basic_info = Item(item_id).GetBasicInfo()
        except Exception:
            continue
        category = _get_item_category(basic_info)
        if category == "none" or category == "commands":
            continue
        ALL_ITEM_IDS_CACHE.append(item_id)
        ITEM_CATEGORIES_CACHE[item_id] = category
        ITEM_ID_AUX_CACHE[item_id] = basic_info.id_aux
        if item_id not in ITEM_NAME_CACHE:
            try:
                ITEM_NAME_CACHE[item_id] = GetItemHoverName(item_id) or item_id
            except Exception:
                ITEM_NAME_CACHE[item_id] = item_id


@RegistToolDeltaScreen("MiniJEIItemListUI.main")
class MiniJEIItemListUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params=None):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.all_item_ids = []  # type: list[str]
        self.item_categories = {}  # type: dict[str, str]
        self.item_id_aux_cache = {}  # type: dict[str, int]
        self.filtered_item_ids = []  # type: list[str]
        self.current_page_item_ids = []  # type: list[str]
        self.page_start_index = 0
        self.current_page = 0
        self.total_pages_num = 1
        self.items_per_page = 1
        self.category_options = []  # type: list[tuple[str, str]]
        self.category_combo = None  # type: Dropdown | None
        self.category_prefix = ""
        self.search_text = ""
        self.current_page_favourites = []  # type: list[tuple[str, str, str]]
        self.favourites_current_page = 0
        self.favourites_total_pages_num = 1
        self.favourites_per_page = 1
        self.favourites_search_text = ""

    def OnCreate(self):
        self.grid_panel = self.GetElement(GRID_PANEL_PATH)
        self.jei_items_grid = self.GetElement(ITEMS_GRID_PATH).asGrid()
        self.category_combo = Dropdown(
            self.GetElement(CATEGORY_COMBO_PATH),
            placeholder="全部",
            max_visible_options=6,
            row_height=20,
        )
        self.page_label = self.GetElement(PAGE_LABEL_PATH).asLabel()
        self.GetElement(PREV_PAGE_BTN_PATH).asButton().SetCallback(self.onPrevPage)
        self.GetElement(NEXT_PAGE_BTN_PATH).asButton().SetCallback(self.onNextPage)
        self.GetElement(CLOSE_BTN_PATH).asButton().SetCallback(self.onClose)
        self.favourites_grid_panel = self.GetElement(FAVOURITES_BG_PATH / "grid_panel")
        self.favourites_grid = self.GetElement(
            FAVOURITES_BG_PATH / "grid_panel/jei_items_grid"
        ).asGrid()
        self.favourites_page_label = self.GetElement(
            FAVOURITES_BG_PATH / "page_label"
        ).asLabel()
        self.GetElement(FAVOURITES_BG_PATH / "prev_page_btn").asButton().SetCallback(
            self.onPrevFavouritesPage
        )
        self.GetElement(FAVOURITES_BG_PATH / "next_page_btn").asButton().SetCallback(
            self.onNextFavouritesPage
        )
        self.load_items()
        self.setup_category_combo()
        self.update_grid_capacity(self.render_current_page)
        ExecLater(0, lambda: self.update_grid_capacity(self.render_current_page))

    def OnActive(self):
        self.render_favourites_page()

    def OnDeactive(self):
        if self.category_combo is not None:
            self.category_combo.Close()

    def OnDestroy(self):
        if self.category_combo is not None:
            self.category_combo.Dispose(screen_destroyed=True)

    def load_items(self):
        # type: () -> None
        if not ALL_ITEM_IDS_CACHE:
            _scan_all_items()
        self.all_item_ids = ALL_ITEM_IDS_CACHE
        self.item_categories = ITEM_CATEGORIES_CACHE
        self.item_id_aux_cache = ITEM_ID_AUX_CACHE

    def update_grid_capacity(self, after=None):
        # type: (typing.Callable[[], None] | None) -> None
        columns, _ = self.jei_items_grid.GetGridDimension()
        grid_panel_size_y = self.grid_panel.GetSize()[1]
        columns = max(1, int(columns))
        if grid_panel_size_y <= 0:
            rows = max(1, int(self.jei_items_grid.GetGridDimension()[1]))
        else:
            rows = max(1, int(grid_panel_size_y / GRID_ITEM_SIZE_Y))
        self.items_per_page = min(columns * rows, MAX_ITEMS_PER_PAGE)
        favourites_columns, favourites_rows = self.favourites_grid.GetGridDimension()
        favourites_panel_size_y = self.favourites_grid_panel.GetSize()[1]
        if favourites_panel_size_y > 0:
            favourites_rows = int(favourites_panel_size_y / GRID_ITEM_SIZE_Y)
        self.favourites_per_page = min(
            max(1, int(favourites_columns)) * max(1, int(favourites_rows)),
            MAX_ITEMS_PER_PAGE,
        )
        self.render_favourites_page()
        ExecLater(0, self.render_favourites_page)
        if after:
            after()
            ExecLater(0, after)

    def setup_category_combo(self):
        # type: () -> None
        self.category_options = GetCategoryOptions()
        combo = self.category_combo
        if combo is None:
            return
        combo.Clear()
        for label, prefix in self.category_options:
            combo.AddOption(label, prefix)
        default_index = 0
        for index, (_, prefix) in enumerate(self.category_options):
            if prefix == MOD_CATEGORY_PREFIX:
                default_index = index
                break
        self.category_prefix = ""
        if self.category_options:
            self.category_prefix = self.category_options[default_index][1]
            combo.SetSelectedOption(default_index)
        combo.RegisterSelectItemCallback(self.onSelectCategory)

    def get_filtered_item_ids(self):
        # type: () -> list[str]
        item_ids = self.all_item_ids
        if self.category_prefix:
            item_ids = [
                item_id
                for item_id in item_ids
                if item_id.startswith(self.category_prefix)
            ]
        query = self.search_text.strip()
        if not query:
            return item_ids
        keywords = query.lower().split()
        return [
            item_id
            for item_id in item_ids
            if all(
                keyword
                in (
                    item_id.lower()
                    + " "
                    + _get_search_text(ITEM_NAME_CACHE.get(item_id, item_id))
                )
                for keyword in keywords
            )
        ]

    def render_current_page(self):
        # type: () -> None
        self.filtered_item_ids = self.get_filtered_item_ids()
        item_count = len(self.filtered_item_ids)
        self.total_pages_num = max(
            1,
            (item_count + self.items_per_page - 1) // self.items_per_page,
        )
        if self.current_page >= self.total_pages_num:
            self.current_page = 0
        if self.current_page < 0:
            self.current_page = self.total_pages_num - 1
        self.page_start_index = self.current_page * self.items_per_page
        end = self.page_start_index + self.items_per_page
        self.current_page_item_ids = self.filtered_item_ids[self.page_start_index : end]
        self.jei_items_grid.SetPropertyBag({
            "#maximum_grid_items": len(self.current_page_item_ids)
        })
        self.jei_items_grid.SetVisible(bool(self.current_page_item_ids), True)
        self.page_label.SetText(
            "第 %d / %d 页" % (self.current_page + 1, self.total_pages_num)
        )

    def get_page_item_id(self, index):
        # type: (int) -> str | None
        if index >= len(self.current_page_item_ids):
            return None
        return self.current_page_item_ids[index]

    def render_favourites_page(self):
        # type: () -> None
        # Ignore incomplete saved records without modifying the favourite config.
        favourites = [
            favourite
            for favourite in GetFavourites()
            if isinstance(favourite, (tuple, list)) and len(favourite) == 3
        ]
        keywords = self.favourites_search_text.lower().split()
        if keywords:
            favourites = [
                favourite
                for favourite in favourites
                if all(
                    keyword
                    in (
                        favourite[1].lower()
                        + " "
                        + favourite[2].lower()
                        + " "
                        + _get_search_text(
                            ITEM_NAME_CACHE.get(favourite[2], favourite[2])
                        )
                    )
                    for keyword in keywords
                )
            ]
        self.favourites_total_pages_num = max(
            1,
            (len(favourites) + self.favourites_per_page - 1)
            // self.favourites_per_page,
        )
        self.favourites_current_page = min(
            self.favourites_current_page, self.favourites_total_pages_num - 1
        )
        start = self.favourites_current_page * self.favourites_per_page
        self.current_page_favourites = favourites[start : start + self.favourites_per_page]
        self.favourites_grid.SetPropertyBag({
            "#maximum_grid_items": len(self.current_page_favourites)
        })
        self.favourites_grid.SetVisible(bool(self.current_page_favourites), True)
        self.favourites_page_label.SetText(
            "第 %d / %d 页"
            % (self.favourites_current_page + 1, self.favourites_total_pages_num)
        )

    def get_item_id_aux(self, item_id):
        # type: (str) -> int
        cached = self.item_id_aux_cache.get(item_id)
        if cached is not None:
            return cached
        item_id_aux = Item(item_id).GetBasicInfo().id_aux
        self.item_id_aux_cache[item_id] = item_id_aux
        return item_id_aux

    def PushRecipes(self, recipes, update=True):
        # type: (RecipeCategoriesData, bool) -> RecipeCheckerUI | None
        return RecipeCheckerUI.Display(recipes)

    def onClose(self, params):
        # type: (dict) -> None
        self.RemoveUI()

    def onPrevPage(self, params):
        # type: (dict) -> None
        if self.total_pages_num <= 1:
            return
        self.current_page = (self.current_page - 1) % self.total_pages_num
        self.render_current_page()

    def onNextPage(self, params):
        # type: (dict) -> None
        if self.total_pages_num <= 1:
            return
        self.current_page = (self.current_page + 1) % self.total_pages_num
        self.render_current_page()

    def onPrevFavouritesPage(self, params):
        # type: (dict) -> None
        self.favourites_current_page = (
            self.favourites_current_page - 1
        ) % self.favourites_total_pages_num
        self.render_favourites_page()

    def onNextFavouritesPage(self, params):
        # type: (dict) -> None
        self.favourites_current_page = (
            self.favourites_current_page + 1
        ) % self.favourites_total_pages_num
        self.render_favourites_page()

    @Binder.binding_collection(
        Binder.BF_BindInt,
        FAVOURITES_COLLECTION,
        "#MiniJEIItemListUI.favourite_item_nums",
    )
    def get_favourite_item_nums(self, _index):
        # type: (int) -> int
        return len(self.current_page_favourites)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        FAVOURITES_COLLECTION,
        "#MiniJEIItemListUI.favourite_item_id_aux",
    )
    def get_favourite_item_id_aux_binding(self, index):
        # type: (int) -> int
        if not 0 <= index < len(self.current_page_favourites):
            return EMPTY_ITEM_ID_AUX
        return self.get_item_id_aux(self.current_page_favourites[index][2])

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#MiniJEIItemListUI.favourite_item_select",
    )
    def onSelectFavouriteItem(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if not 0 <= index < len(self.current_page_favourites):
            return
        category, item_id, display_item_id = self.current_page_favourites[index]
        button_path = params["ButtonPath"]
        if button_path.startswith("main/"):
            button_path = button_path[len("main/") :]
        button = self.GetElement(button_path)
        x, y = button.GetRootPos()
        from skybluetech_scripts.skybluetech.client.ui.recipe_checker.render_utils import (
            CreateDescBoard,
        )

        CreateDescBoard(
            button._parent,
            (x + 20, min(y, self.favourites_grid_panel.GetSize()[1] - 40)),
            category,
            item_id,
            display_item_id,
            GetItemFormattedHoverText(display_item_id) or display_item_id,
        )

    @Binder.binding_collection(
        Binder.BF_BindInt,
        ITEMS_COLLECTION,
        "#MiniJEIItemListUI.item_nums",
    )
    def get_item_nums(self, _index):
        # type: (int) -> int
        return len(self.current_page_item_ids)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        ITEMS_COLLECTION,
        "#MiniJEIItemListUI.item_id_aux",
    )
    def get_item_id_aux_binding(self, index):
        # type: (int) -> int
        item_id = self.get_page_item_id(index)
        if item_id is None:
            return EMPTY_ITEM_ID_AUX
        return self.get_item_id_aux(item_id)

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#MiniJEIItemListUI.item_select",
    )
    def onSelectItem(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        item_id = self.get_page_item_id(index)
        if item_id is None:
            return
        button_path = params["ButtonPath"]
        if button_path.startswith("main/"):
            button_path = button_path[len("main/") :]
        button = self.GetElement(button_path)
        x, y = button.GetRootPos()
        from .render_utils import CreateDescBoard

        CreateDescBoard(
            button._parent,
            (
                x + 20,
                min(
                    y,
                    self.grid_panel.GetSize()[1] - 40,
                ),
            ),
            CategoryType.ITEM,
            item_id,
            item_id,
            GetItemFormattedHoverText(item_id) or item_id,
        )

    def onSelectCategory(self, index, show_name, user_data):
        # type: (int, str, typing.Any) -> None
        self.category_prefix = user_data or ""
        self.current_page = 0
        self.render_current_page()

    @Binder.binding(
        Binder.BF_EditChanged,
        "#MiniJEIItemListUI.search_item",
    )
    def onSearchItemFinished(self, params):
        # type: (dict) -> None
        self.search_text = params["Text"].strip()
        self.current_page = 0
        self.render_current_page()

    @Binder.binding(
        Binder.BF_EditChanged,
        "#MiniJEIItemListUI.search_favourites",
    )
    def onSearchFavouritesFinished(self, params):
        # type: (dict) -> None
        self.favourites_search_text = params["Text"].strip()
        self.favourites_current_page = 0
        self.render_favourites_page()

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == event.KeyBoardType.KEY_ESCAPE and event.isDown:
            if self.category_combo is not None and self.category_combo.IsOpen():
                self.category_combo.Close()
                return
            self.RemoveUI()

    @ToolDeltaScreen.Listen(MouseWheelClientEvent)
    def onMouseWheel(self, event):
        # type: (MouseWheelClientEvent) -> None
        if self.category_combo is not None and self.category_combo.IsOpen():
            return
        if event.direction == 1:
            self.onPrevPage({})
        else:
            self.onNextPage({})

    @ToolDeltaScreen.Listen(ScreenSizeChangedClientEvent)
    def onScreenSizeChanged(self, _):
        if self.category_combo is not None:
            self.category_combo.Close()
        ExecLater(0, lambda: self.update_grid_capacity(self.render_current_page))
