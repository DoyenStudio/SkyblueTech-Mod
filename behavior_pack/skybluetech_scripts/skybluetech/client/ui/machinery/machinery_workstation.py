# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.api.client.player import (
    GetLocalPlayerHotbarAndInvItems,
)
from skybluetech_scripts.tooldelta.extensions.rate_limiter import PlayerRateLimiter
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.events.machinery.machinery_workstation import (
    MachineryWorkstationDoCraft,
    MachineryWorkstationTransferRecipe,
)
from skybluetech_scripts.skybluetech.common.machinery_def.machinery_workstation import (
    MRecipe,
    recipes,
    K_CRAFTING_PROGRESS,
    K_OUTPUT_ITEM_ID,
)
from ..recipe_checker import AsRecipeCheckerBtn
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdateGenericProgressL2R


WARNING_BAR_DISPLAY_THRESOLD = 0.8

RECIPES_COLLECTION = "machinery_workstation_recipes_grid"
EMPTY_ITEM_ID_AUX = 131072
RECIPE_REFRESH_INTERVAL = 10
NORMAL_BG_COLOR = (1.0, 1.0, 1.0)
INCOMPLETE_BG_COLOR = (1.0, 85 / 255.0, 85 / 255.0)  # 0xFF5555
_hover_name_cache = {}  # type: dict[str, str]


def _get_output_hover_name(output_item_id):
    # type: (str) -> str
    cached = _hover_name_cache.get(output_item_id)
    if cached is None:
        cached = (GetItemHoverName(output_item_id) or output_item_id).lower()
        _hover_name_cache[output_item_id] = cached
    return cached


# 本 UI 的 main 面板被嵌入 left_half 中(右侧为配方表), 故在共享 MAIN_PATH 基础上补一层
MAIN_PATH = MAIN_PATH.parent / "left_half/main"
RECIPES_VIEW_PATH = MAIN_PATH.parent.parent / "right_half/recipes_view"

CRAFT_BTN_PATH = MAIN_PATH / "craft_btn"
CRAFT_SPEED_BAR_PATH = MAIN_PATH / "craft_speed_bar"
WARNING_BAR_PATH = MAIN_PATH / "warning_bar"
PRGS_PATH = MAIN_PATH / "progress"
RESEARCHING_BTN_PATH = MAIN_PATH / "researching_btn"
OUTPUT_ITEM_PREVIEWER_PATH = (
    MAIN_PATH / "output_slot/slot/item_cell_overlay_ref/item_renderer"
)

craft_hi_freq_limiter = PlayerRateLimiter(0.1)


@RegistToolDeltaScreen("MachineryWorkstationUI.main", is_proxy=True)
class MachineryWorkstationUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.craft_strength = 0.0
        self.warning_bar_shown = False
        self.warning_bar_display_time = 0
        self.search_text = ""
        self.recipe_refresh_ticks = 0
        self.visible_recipes = []  # type: list[dict]
        self.recipes_grid = None  # type: UBaseCtrl | None
        self.craft_btn = (
            self.GetElement(CRAFT_BTN_PATH).asButton().SetCallback(self.onClickCraftBtn)
        )
        self.researching_btn = (
            self
            .GetElement(RESEARCHING_BTN_PATH)
            .asButton()
            .SetCallback(self.onClickResearchingBtn)
        )
        self.craft_speed_bar = self.GetElement(CRAFT_SPEED_BAR_PATH).asImage()
        self.warning_bar = self.GetElement(WARNING_BAR_PATH)
        self.output_item_previewer = self.GetElement(
            OUTPUT_ITEM_PREVIEWER_PATH
        ).asItemRenderer()
        self.progress_bar = self.GetElement(PRGS_PATH)
        self.warning_bar.SetVisible(False)
        self.output_item_previewer.SetVisible(False)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )
        self.recipes_grid = (
            self.GetElement(RECIPES_VIEW_PATH).asScrollView().GetContent().asGrid()
        )
        self.refresh_visible_recipes()

    def onClickCraftBtn(self, _):
        _, x, y, z = self.pos
        if not craft_hi_freq_limiter.record():
            return
        data = GetBlockEntityData(x, y, z)
        if data is None:
            return
        output_item_id = GetValue(data["exData"], K_OUTPUT_ITEM_ID, None)
        if output_item_id is None:
            return
        self.craft_strength = min(1.0, self.craft_strength + 0.3)
        MachineryWorkstationDoCraft(x, y, z, self.craft_strength).send()

    def onClickResearchingBtn(self, _):
        self.open_industrial_researching_ui()

    def OnTicking(self):
        self.recipe_refresh_ticks += 1
        if self.recipe_refresh_ticks % RECIPE_REFRESH_INTERVAL == 0:
            self.refresh_visible_recipes()
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        output_item_id = GetValue(data, K_OUTPUT_ITEM_ID, None)
        progress = GetValue(data, K_CRAFTING_PROGRESS, 0.0)
        self.craft_strength = max(0.0, self.craft_strength - 0.01)
        self.warning_bar_display_time = max(0, self.warning_bar_display_time - 1)
        self.update_craft_speed_bar()
        if output_item_id is None:
            self.output_item_previewer.SetVisible(False)
        else:
            self.output_item_previewer.SetVisible(True)
            self.output_item_previewer.SetUiItem(Item(output_item_id))
            UpdateGenericProgressL2R(self.progress_bar, progress)

    def update_craft_speed_bar(self):
        self.craft_speed_bar.SetSpriteClipRatio(
            "fromRightToLeft",
            1 - self.craft_strength,
        )
        if self.craft_strength >= WARNING_BAR_DISPLAY_THRESOLD:
            self.warning_bar_display_time = 60
        if self.warning_bar_display_time > 0:
            if not self.warning_bar_shown:
                self.warning_bar.SetVisible(True)
                self.warning_bar_shown = True
        else:
            if self.warning_bar_shown:
                self.warning_bar.SetVisible(False)
                self.warning_bar_shown = False

    def open_industrial_researching_ui(self):
        from skybluetech_scripts.skybluetech.client.ui.misc.industrial_researching_ui import (
            IndustrialResearchProgressUI,
        )

        self.RemoveUI()
        IndustrialResearchProgressUI.PushUI()

    def refresh_visible_recipes(self):
        """按玩家背包重算可见配方列表。所需物品一件都没有的配方不显示;
        物品不完全的配方标记为 incomplete(红底); 再按搜索词过滤结果物名。"""
        inv_counts = {}  # type: dict[str, int]
        for item in GetLocalPlayerHotbarAndInvItems():
            if item is None or item.count <= 0:
                continue
            inv_counts[item.id] = inv_counts.get(item.id, 0) + item.count
        query = self.search_text.strip().lower()
        visible = []  # type: list[dict]
        for rcp in recipes:
            matched_any, complete = self._check_recipe_availability(rcp, inv_counts)
            if not matched_any:
                continue
            if query and query not in _get_output_hover_name(rcp.output_item_id):
                continue
            visible.append({
                "output_item_id": rcp.output_item_id,
                "id_aux": Item(rcp.output_item_id).GetBasicInfo().id_aux,
                "complete": complete,
            })
        # 可完整合成的配方排在前面(稳定排序保持组内原顺序)
        visible.sort(key=lambda r: not r["complete"])
        self.visible_recipes = visible
        if self.recipes_grid is not None:
            self.recipes_grid.SetPropertyBag({"#maximum_grid_items": len(visible)})

    def _check_recipe_availability(self, rcp, inv_counts):
        # type: (MRecipe, dict[str, int]) -> tuple[bool, bool]
        """贪心分配背包库存判定配方可用性, 返回 (是否至少有一件所需物, 是否全部满足)。"""
        work = dict(inv_counts)
        matched_any = False
        complete = True
        for input in rcp.input_items.values():
            need = input.count
            got = 0
            for item_id in work:
                if got >= need:
                    break
                cnt = work[item_id]
                if cnt <= 0 or not input.match_item_id(item_id):
                    continue
                take = min(cnt, need - got)
                work[item_id] = cnt - int(take)
                got += take
            if got > 0:
                matched_any = True
            if got < need:
                complete = False
        return matched_any, complete

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RECIPES_COLLECTION,
        "#MachineryWorkstationUI.recipe_count",
    )
    def get_recipe_count(self, _index):
        # type: (int) -> int
        return len(self.visible_recipes)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RECIPES_COLLECTION,
        "#MachineryWorkstationUI.recipe_item_id_aux",
    )
    def get_recipe_item_id_aux(self, index):
        # type: (int) -> int
        if index >= len(self.visible_recipes):
            return EMPTY_ITEM_ID_AUX
        return self.visible_recipes[index]["id_aux"]

    @Binder.binding_collection(
        Binder.BF_BindColor,
        RECIPES_COLLECTION,
        "#MachineryWorkstationUI.recipe_bg_color",
    )
    def get_recipe_bg_color(self, index):
        # type: (int) -> tuple[float, float, float]
        if index >= len(self.visible_recipes):
            return NORMAL_BG_COLOR
        if self.visible_recipes[index]["complete"]:
            return NORMAL_BG_COLOR
        return INCOMPLETE_BG_COLOR

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#MachineryWorkstationUI.recipe_select",
    )
    def on_recipe_select(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if index >= len(self.visible_recipes):
            return
        _, x, y, z = self.pos
        MachineryWorkstationTransferRecipe(
            x, y, z, self.visible_recipes[index]["output_item_id"]
        ).send()
        self.refresh_visible_recipes()

    @Binder.binding(
        Binder.BF_EditChanged,
        "#MachineryWorkstationUI.search_recipe",
    )
    def on_search_recipe(self, params):
        # type: (dict) -> None
        self.search_text = params["Text"]
        self.refresh_visible_recipes()
