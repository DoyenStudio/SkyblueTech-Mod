# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.common import ExecLater
from skybluetech_scripts.tooldelta.events.client import OnKeyPressInGame
from skybluetech_scripts.tooldelta.api.client import (
    GetItemHoverName,
    GetLocalPlayerHotbarAndInvItems,
    GetLocalPlayerLevelByExp,
)
from skybluetech_scripts.tooldelta.ui import (
    Binder,
    RegistToolDeltaScreen,
    SCREEN_BASE_PATH,
    ToolDeltaScreen,
)
from skybluetech_scripts.tooldelta.utils.py_comp import py2_unicode
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from skybluetech_scripts.skybluetech.common.events.misc.industrial_researching import (
    IndustrialResearchingInscribeRequest,
    IndustrialResearchingQueryRequest,
    IndustrialResearchingQueryResponse,
    IndustrialResearchingSubmitRequest,
)
from skybluetech_scripts.skybluetech.common.misc.industrial_researching import (
    all_researchings,
)

if 0>1:
    from skybluetech_scripts.skybluetech.common.mini_jei.misc.industrial_researching import (
        IndustrialResearchingRecipe,  # noqa: F401
        Input,  # noqa: F401
    )


RESEARCHINGS_SCROLL_PATH = SCREEN_BASE_PATH / "researchings_scroll_view"
CLOSE_BTN_PATH = SCREEN_BASE_PATH / "close_btn"
EXP_BOTTLE_ITEM_ID = "minecraft:experience_bottle"
RESEARCHINGS_COLLECTION = "industrial_researchings_grid"
REQUIREMENTS_COLLECTION = "industrial_research_requirements_grid"
LABEL_NORMAL_COLOR = (0.2588, 0.2588, 0.2588)
LABEL_MISSING_COLOR = (0xAF / 255.0, 0, 0)
LABEL_OK_COLOR = (0.0, 0.5, 0.0)
EMPTY_ITEM_ID_AUX = 131072
ITEM_NAME_CACHE = {}  # type: dict[str, str]
SUBMIT_REFRESH_QUERY_DELAYS = (0.2, 0.8, 1.6)
SUBMIT_UNLOCK_TIMEOUT = 4.0


def _clean_item_name(item_id):
    # type: (str) -> str
    cached = ITEM_NAME_CACHE.get(item_id)
    if cached is not None:
        return cached
    try:
        item_name = GetItemHoverName(item_id) or item_id
    except Exception:
        item_name = item_id
    item_name = item_name.replace("§r", "").replace("§f", "")
    ITEM_NAME_CACHE[item_id] = item_name
    return item_name


def _short_item_name(item_id):
    # type: (str) -> str
    item_name = py2_unicode(_clean_item_name(item_id)).replace(" ", "")
    if len(item_name) > 6:
        return item_name[:6] + ".."
    return item_name


def _safe_percent(now, total):
    # type: (float, float) -> float
    if total <= 0:
        return 1.0
    return max(0.0, min(1.0, float(now) / total))


@RegistToolDeltaScreen("IndustrialResearchProgressUI.main")
class IndustrialResearchProgressUI(ToolDeltaScreen):
    def __init__(self, screen_name, screen_instance, params=None):
        ToolDeltaScreen.__init__(self, screen_name, screen_instance, params)
        self.ready = False
        self.researched_items = {}  # type: dict[str, int]
        self.requirements_window = None
        self.current_recipe = None  # type: IndustrialResearchingRecipe | None
        self.researching_items = []  # type: list[dict]
        self.requirement_items = []  # type: list[dict]
        self.item_id_aux_cache = {}  # type: dict[str, int]
        self.can_submit_research = False
        self.submitting_research = False
        self.pending_research_item_id = None  # type: str | None
        self.submit_query_seq = 0

    def OnCreate(self):
        self.ready = False
        self.researched_items = {}
        self.requirements_window = None
        self.current_recipe = None
        self.researching_items = []
        self.requirement_items = []
        self.can_submit_research = False
        self.submitting_research = False
        self.pending_research_item_id = None
        self.submit_query_seq = 0
        self.recipes = list(all_researchings)
        self.update_researching_items()
        self.researchings_grid = (
            self
            .GetElement(RESEARCHINGS_SCROLL_PATH)
            .asScrollView()
            .GetContent()
            .asGrid()
        )
        self.researchings_grid.SetPropertyBag({
            "#maximum_grid_items": len(self.recipes)
        })
        self.GetElement(CLOSE_BTN_PATH).asButton().SetCallback(
            lambda _: self.RemoveUI()
        )
        self.send_query_request()

    def OnDestroy(self):
        self.close_requirements_window()

    def send_query_request(self):
        # type: () -> None
        IndustrialResearchingQueryRequest().send()

    def render_researchings(self):
        # type: () -> None
        self.update_researching_items()
        self.researchings_grid.SetPropertyBag({
            "#maximum_grid_items": len(self.researching_items)
        })

    def update_researching_items(self):
        # type: () -> None
        if len(self.researching_items) != len(self.recipes):
            self.researching_items = [
                {
                    "recipe": recipe,
                    "item_id": recipe.result_item_id,
                    "item_id_aux": self.get_item_id_aux(recipe.result_item_id),
                    "item_name": _clean_item_name(recipe.result_item_id),
                    "researched": recipe.result_item_id in self.researched_items,
                }
                for recipe in self.recipes
            ]
            return
        for item in self.researching_items:
            item["researched"] = item["item_id"] in self.researched_items

    def open_requirements_window(self, recipe):
        # type: (IndustrialResearchingRecipe) -> None
        if not self.ready:
            return
        if self.submitting_research:
            return
        self.close_requirements_window()
        window = self.AddElement(
            "IndustrialResearchProgressUI.requirements_window",
            "requirements_window",
        )
        window.SetLayer(20)
        self.requirements_window = window
        self.current_recipe = recipe
        self.can_submit_research = False
        self.submitting_research = False
        self.pending_research_item_id = None
        window["close_btn"].asButton().SetCallback(
            lambda _: self.close_requirements_window()
        )
        window["bg/title"].asLabel().SetText(
            "研究 " + _short_item_name(recipe.result_item_id) + " 需要："
        )

        grid = window["requirements_grid"].asGrid()
        self.update_requirement_items()
        grid.SetPropertyBag({"#maximum_grid_items": len(self.requirement_items)})
        self.update_inscribe_button()
        self.update_submit_button()

    def update_requirement_items(self):
        # type: () -> None
        if self.current_recipe is None:
            self.requirement_items = []
            self.can_submit_research = False
            return
        recipe = self.current_recipe
        researched = recipe.result_item_id in self.researched_items
        item_counts = self.get_local_item_counts()
        player_level = GetLocalPlayerLevelByExp()
        can_submit = True
        items = []
        requirements = list(recipe.require_items)  # type: list[Input | None]
        requirements.append(None)
        for input_item in requirements:
            if input_item is None:
                if researched:
                    items.append(
                        self.create_requirement_item_data(
                            EXP_BOTTLE_ITEM_ID,
                            "✔ 已完成",
                            LABEL_OK_COLOR,
                            1.0,
                            False,
                        )
                    )
                    continue
                enough = player_level >= recipe.require_exp_level
                can_submit = can_submit and enough
                items.append(
                    self.create_requirement_item_data(
                        EXP_BOTTLE_ITEM_ID,
                        "%d/%d" % (player_level, recipe.require_exp_level),
                        LABEL_NORMAL_COLOR if enough else LABEL_MISSING_COLOR,
                        _safe_percent(player_level, recipe.require_exp_level),
                        False,
                    )
                )
            else:
                if researched:
                    items.append(
                        self.create_requirement_item_data(
                            input_item.id,
                            "✔ 已完成",
                            LABEL_OK_COLOR,
                            1.0,
                            True,
                        )
                    )
                    continue
                own_count = self.count_matched_items(input_item, item_counts)
                enough = own_count >= input_item.count
                can_submit = can_submit and enough
                items.append(
                    self.create_requirement_item_data(
                        input_item.id,
                        "%d/%d" % (own_count, input_item.count),
                        LABEL_NORMAL_COLOR if enough else LABEL_MISSING_COLOR,
                        _safe_percent(own_count, input_item.count),
                        True,
                    )
                )
        self.requirement_items = items
        self.can_submit_research = can_submit and not researched and not self.submitting_research

    def create_requirement_item_data(
        self, item_id, label, label_color, progress_percent, check_recipe
    ):
        # type: (str, str, tuple[float, float, float], float, bool) -> dict
        return {
            "item_id": item_id,
            "item_id_aux": self.get_item_id_aux(item_id),
            "label": label,
            "label_color": label_color,
            "progress_clip": 1 - _safe_percent(progress_percent, 1.0),
            "check_recipe": check_recipe,
        }

    def close_requirements_window(self):
        if self.requirements_window is not None:
            self.requirements_window.Remove(warning=False)
            self.requirements_window = None
            self.current_recipe = None
            self.requirement_items = []
            self.can_submit_research = False

    def is_current_recipe_researched(self):
        # type: () -> bool
        return (
            self.current_recipe is not None
            and self.current_recipe.result_item_id in self.researched_items
        )

    def update_inscribe_button(self):
        # type: () -> None
        if self.requirements_window is None:
            return
        researched = self.is_current_recipe_researched()
        self.requirements_window["take_btn/disable_mask"].SetVisible(not researched)
        self.requirements_window["take_btn"].asButton().SetCallback(
            lambda _: self.on_click_inscribe_btn()
        )

    def update_submit_button(self):
        # type: () -> None
        if self.requirements_window is None:
            return
        self.requirements_window["submit_btn/disable_mask"].SetVisible(
            not self.can_submit_research
        )

    def on_click_inscribe_btn(self):
        # type: () -> None
        if not self.is_current_recipe_researched():
            return
        IndustrialResearchingInscribeRequest(self.current_recipe.result_item_id).send()  # pyright: ignore[reportOptionalMemberAccess]
        self.RemoveUI()

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#IndustrialResearchProgressUI.submit_btn",
    )
    def on_submit_btn_pressed(self, params):
        # type: (dict) -> None
        self.handle_submit_btn()

    def handle_submit_btn(self):
        # type: () -> None
        if not self.can_submit_research:
            return
        if self.current_recipe is None:
            return
        self.submitting_research = True
        self.pending_research_item_id = self.current_recipe.result_item_id
        self.can_submit_research = False
        self.update_submit_button()
        IndustrialResearchingSubmitRequest(self.current_recipe.result_item_id).send()

        self.schedule_submit_refresh_queries(self.current_recipe.result_item_id)

    def schedule_submit_refresh_queries(self, item_id):
        # type: (str) -> None
        self.submit_query_seq += 1
        seq = self.submit_query_seq
        for delay in SUBMIT_REFRESH_QUERY_DELAYS:
            ExecLater(
                delay,
                self.send_submit_refresh_query,
                item_id,
                seq,
            )
        ExecLater(SUBMIT_UNLOCK_TIMEOUT, self.unlock_submit_if_pending, item_id, seq)

    def send_submit_refresh_query(self, item_id, seq):
        # type: (str, int) -> None
        if not self.submitting_research:
            return
        if seq != self.submit_query_seq or item_id != self.pending_research_item_id:
            return
        self.send_query_request()

    def unlock_submit_if_pending(self, item_id, seq):
        # type: (str, int) -> None
        if not self.submitting_research:
            return
        if seq != self.submit_query_seq or item_id != self.pending_research_item_id:
            return
        self.submitting_research = False
        self.pending_research_item_id = None
        if self.requirements_window is not None:
            self.update_requirement_items()
            self.update_submit_button()

    def get_local_item_counts(self):
        # type: () -> dict[str, int]
        counts = {}
        for item in GetLocalPlayerHotbarAndInvItems():
            if item is None:
                continue
            counts[item.id] = counts.get(item.id, 0) + item.count
        return counts

    def count_matched_items(self, input_item, item_counts):
        # type: (Input, dict[str, int]) -> int
        count = 0
        for item_id, item_count in item_counts.items():
            if input_item.match_item_id(item_id):
                count += item_count
        return count

    def get_item_id_aux(self, item_id):
        # type: (str) -> int
        cached = self.item_id_aux_cache.get(item_id)
        if cached is not None:
            return cached
        try:
            item_id_aux = Item(item_id).GetBasicInfo().id_aux
        except Exception:
            item_id_aux = EMPTY_ITEM_ID_AUX
        self.item_id_aux_cache[item_id] = item_id_aux
        return item_id_aux

    @ToolDeltaScreen.Listen(IndustrialResearchingQueryResponse)
    def on_recv_query_response(self, event):
        # type: (IndustrialResearchingQueryResponse) -> None
        researched_items = event.researched_items or {}
        was_submitting = self.submitting_research
        pending_item_id = self.pending_research_item_id
        finish_submitting = (
            was_submitting
            and pending_item_id in researched_items
        )
        self.researched_items = researched_items
        self.ready = True
        if finish_submitting:
            self.submitting_research = False
            self.pending_research_item_id = None
        self.render_researchings()
        if self.requirements_window is not None:
            self.update_requirement_items()
            self.requirements_window["requirements_grid"].SetPropertyBag({
                "#maximum_grid_items": len(self.requirement_items)
            })
            self.update_submit_button()
        self.update_inscribe_button()

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RESEARCHINGS_COLLECTION,
        "#IndustrialResearchProgressUI.researching_count",
    )
    def get_researching_count(self, _index):
        # type: (int) -> int
        return len(self.researching_items)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RESEARCHINGS_COLLECTION,
        "#IndustrialResearchProgressUI.researching_item_id_aux",
    )
    def get_researching_item_id_aux(self, index):
        # type: (int) -> int
        if index >= len(self.researching_items):
            return EMPTY_ITEM_ID_AUX
        return self.researching_items[index]["item_id_aux"]

    @Binder.binding_collection(
        Binder.BF_BindString,
        RESEARCHINGS_COLLECTION,
        "#IndustrialResearchProgressUI.researching_item_name",
    )
    def get_researching_item_name(self, index):
        # type: (int) -> str
        if index >= len(self.researching_items):
            return ""
        return self.researching_items[index]["item_name"]

    @Binder.binding_collection(
        Binder.BF_BindBool,
        RESEARCHINGS_COLLECTION,
        "#IndustrialResearchProgressUI.researching_ok_visible",
    )
    def get_researching_ok_visible(self, index):
        # type: (int) -> bool
        if index >= len(self.researching_items):
            return False
        return self.researching_items[index]["researched"]

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#IndustrialResearchProgressUI.researching_selected",
    )
    def on_researching_selected(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if not self.ready or index >= len(self.researching_items):
            return
        self.open_requirements_window(self.researching_items[index]["recipe"])

    @Binder.binding_collection(
        Binder.BF_BindInt,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_count",
    )
    def get_requirement_count(self, _index):
        # type: (int) -> int
        return len(self.requirement_items)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_item_id_aux",
    )
    def get_requirement_item_id_aux(self, index):
        # type: (int) -> int
        if index >= len(self.requirement_items):
            return EMPTY_ITEM_ID_AUX
        return self.requirement_items[index]["item_id_aux"]

    @Binder.binding_collection(
        Binder.BF_BindString,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_label",
    )
    def get_requirement_label(self, index):
        # type: (int) -> str
        if index >= len(self.requirement_items):
            return ""
        return self.requirement_items[index]["label"]

    @Binder.binding_collection(
        Binder.BF_BindColor,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_label_color",
    )
    def get_requirement_label_color(self, index):
        # type: (int) -> tuple[float, float, float]
        if index >= len(self.requirement_items):
            return LABEL_NORMAL_COLOR
        return self.requirement_items[index]["label_color"]

    @Binder.binding_collection(
        Binder.BF_BindFloat,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_progress_clip",
    )
    def get_requirement_progress_clip(self, index):
        # type: (int) -> float
        if index >= len(self.requirement_items):
            return 1.0
        return self.requirement_items[index]["progress_clip"]

    @Binder.binding_collection(
        Binder.BF_BindBool,
        REQUIREMENTS_COLLECTION,
        "#IndustrialResearchProgressUI.requirement_check_recipe_visible",
    )
    def get_requirement_check_recipe_visible(self, index):
        # type: (int) -> bool
        if index >= len(self.requirement_items):
            return False
        return self.requirement_items[index]["check_recipe"]

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#IndustrialResearchProgressUI.requirement_check_recipe",
    )
    def on_requirement_check_recipe(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if index >= len(self.requirement_items):
            return
        if not self.requirement_items[index]["check_recipe"]:
            return
        CheckRecipe(self.requirement_items[index]["item_id"])

    @ToolDeltaScreen.Listen(OnKeyPressInGame)
    def onKeyPress(self, event):
        # type: (OnKeyPressInGame) -> None
        if event.key == event.KeyBoardType.KEY_ESCAPE and event.isDown:
            if self.requirements_window is not None:
                self.close_requirements_window()
                return
            self.RemoveUI()
