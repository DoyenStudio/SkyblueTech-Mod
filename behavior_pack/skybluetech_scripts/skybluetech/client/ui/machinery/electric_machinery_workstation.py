# coding=utf-8
from skybluetech_scripts.skybluetech.common.events.machinery.electric_machinery_workstation import (
    ElectricMachineryWorkstationSelectRecipe,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electric_machinery_workstation import (
    K_OUTPUT_ITEM_ID,
    K_SELECTED_RECIPE,
    OUTPUT_SLOT,
    SOLDER_ITEM_ID,
    SOLDER_SLOT,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .machinery_workstation import (
    EMPTY_ITEM_ID_AUX,
    NORMAL_BG_COLOR,
    RESULT_LABEL_INCOMPLETE_COLOR,
    RESULT_LABEL_NORMAL_COLOR,
    _get_output_display_name,
    _get_output_hover_name,
)
from .utils import GetPreviewMaskColor, UpdateGenericProgressL2R, UpdatePowerBar

PLEASE_SELECT_RECIPE_TEXT = "在右侧配方栏选择配方"
RECIPES_COLLECTION = "electric_machinery_workstation_recipes_grid"
CONTAINER_COLLECTION = "netease_container"
PREVIEW_SLOT_COUNT = 11
SELECTED_BG_COLOR = (85 / 255.0, 170 / 255.0, 1.0)


@RegistToolDeltaScreen("ElectricMachineryWorkstationUI.main", is_proxy=True)
class ElectricMachineryWorkstationUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.search_text = ""
        self.visible_recipes = []
        self.selected_recipe_id = None
        self._preview_recipe_id = ""
        self._preview_recipe = None
        self._preview_id_auxes = [None] * PREVIEW_SLOT_COUNT  # type: list[int | None]
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.progress_bar = self.GetElement(MAIN_PATH / "progress")
        self.result_item_label = self.GetElement(
            MAIN_PATH / "result_item_label"
        ).asLabel()
        self.recipes_grid = (
            self
            .GetElement(MAIN_PATH / "right_half/recipes_view")
            .asScrollView()
            .GetContent()
            .asGrid()
        )
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), recipes
        )
        # 开界面时先取一次方块实体数据, 让首帧渲染就有正确状态
        data = GetBlockEntityData(*self.pos[1:])
        if data is not None:
            self.selected_recipe_id = GetValue(
                data["exData"], K_SELECTED_RECIPE, None
            )
        self.refresh_visible_recipes()
        self.update_recipe_preview()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        selected_recipe_id = GetValue(data, K_SELECTED_RECIPE, None)
        if selected_recipe_id != self.selected_recipe_id:
            self.selected_recipe_id = selected_recipe_id
            self.refresh_visible_recipes()
        output_id = GetValue(data, K_OUTPUT_ITEM_ID, None)
        self.update_recipe_preview()
        progress = GetValue(data, K_PROGRESS, 0.0) if output_id else 0.0
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress_bar, progress)
        display_id = output_id or self.selected_recipe_id
        self.result_item_label.SetText(
            _get_output_display_name(display_id) if display_id else PLEASE_SELECT_RECIPE_TEXT
        )
        self.result_item_label.SetColor(
            RESULT_LABEL_INCOMPLETE_COLOR
            if self.selected_recipe_id and not output_id
            else RESULT_LABEL_NORMAL_COLOR
        )

    def update_recipe_preview(self):
        # Use the same slot overlay as ElectricCrafterUI; no real items are inserted.
        if self._preview_recipe_id == self.selected_recipe_id:
            return
        self._preview_recipe_id = self.selected_recipe_id
        self._preview_recipe = next(
            (r for r in recipes if r.output_item_id == self.selected_recipe_id), None
        )
        self._preview_id_auxes = [
            self._get_preview_id_aux(index) for index in range(PREVIEW_SLOT_COUNT)
        ]

    def _get_preview_id_aux(self, index):
        # type: (int) -> int | None
        recipe = self._preview_recipe
        if recipe is None:
            return None
        if index == OUTPUT_SLOT:
            return Item(recipe.output_item_id).GetBasicInfo().id_aux
        if index == SOLDER_SLOT:
            # 焊锡不属于机件加工台的配方, 是本机固定的输入要求
            return Item(SOLDER_ITEM_ID).GetBasicInfo().id_aux
        required = recipe.input_items.get(index)
        if required is None:
            return None
        item_id = required.id
        if required.is_tag:
            item_id = next(iter(sorted(GetItemsByTag(item_id))), None)
        if item_id is None:
            return None
        return Item(item_id, max(0, required.aux)).GetBasicInfo().id_aux

    def _preview_id_aux_at(self, index):
        # type: (int) -> int | None
        if index < 0 or index >= PREVIEW_SLOT_COUNT:
            return None
        return self._preview_id_auxes[index]

    def refresh_visible_recipes(self):
        """列出全部加工台配方，只按产物名称搜索。"""
        query = self.search_text.strip().lower()
        visible = []  # type: list[dict]
        for rcp in recipes:
            if query and query not in _get_output_hover_name(rcp.output_item_id):
                continue
            visible.append({
                "output_item_id": rcp.output_item_id,
                "id_aux": Item(rcp.output_item_id).GetBasicInfo().id_aux,
            })
        self.visible_recipes = visible
        if self.recipes_grid is not None:
            self.recipes_grid.SetPropertyBag({"#maximum_grid_items": len(visible)})

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RECIPES_COLLECTION,
        "#ElectricMachineryWorkstationUI.recipe_count",
    )
    def get_recipe_count(self, _index):
        # type: (int) -> int
        return len(self.visible_recipes)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        RECIPES_COLLECTION,
        "#ElectricMachineryWorkstationUI.recipe_item_id_aux",
    )
    def get_recipe_item_id_aux(self, index):
        # type: (int) -> int
        if index >= len(self.visible_recipes):
            return EMPTY_ITEM_ID_AUX
        return self.visible_recipes[index]["id_aux"]

    @Binder.binding_collection(
        Binder.BF_BindColor,
        RECIPES_COLLECTION,
        "#ElectricMachineryWorkstationUI.recipe_bg_color",
    )
    def get_recipe_bg_color(self, index):
        # type: (int) -> tuple[float, float, float]
        if index >= len(self.visible_recipes):
            return NORMAL_BG_COLOR
        if self.visible_recipes[index]["output_item_id"] == self.selected_recipe_id:
            return SELECTED_BG_COLOR
        return NORMAL_BG_COLOR

    @Binder.binding(
        Binder.BF_ButtonClickUp,
        "#ElectricMachineryWorkstationUI.recipe_select",
    )
    def on_recipe_select(self, params):
        # type: (dict) -> None
        index = params["#collection_index"]
        if index >= len(self.visible_recipes):
            return
        recipe = self.visible_recipes[index]
        self.selected_recipe_id = recipe["output_item_id"]
        self.update_recipe_preview()
        _, x, y, z = self.pos
        ElectricMachineryWorkstationSelectRecipe(
            x, y, z, recipe["output_item_id"]
        ).send()
        self.refresh_visible_recipes()

    @Binder.binding(
        Binder.BF_EditChanged,
        "#ElectricMachineryWorkstationUI.search_recipe",
    )
    def on_search_recipe(self, params):
        # type: (dict) -> None
        self.search_text = params["Text"]
        self.refresh_visible_recipes()

    @Binder.binding_collection(
        Binder.BF_BindBool,
        CONTAINER_COLLECTION,
        "#ElectricMachineryWorkstationUI.crafting_preview_visible",
    )
    def get_crafting_preview_visible(self, _index):
        # type: (int) -> bool
        return self._preview_recipe is not None

    @Binder.binding_collection(
        Binder.BF_BindBool,
        CONTAINER_COLLECTION,
        "#ElectricMachineryWorkstationUI.crafting_preview_item_visible",
    )
    def get_crafting_preview_item_visible(self, index):
        # type: (int) -> bool
        return self._preview_id_aux_at(index) is not None

    @Binder.binding_collection(
        Binder.BF_BindInt,
        CONTAINER_COLLECTION,
        "#ElectricMachineryWorkstationUI.crafting_preview_item_id_aux",
    )
    def get_crafting_preview_item_id_aux(self, index):
        # type: (int) -> int
        id_aux = self._preview_id_aux_at(index)
        return EMPTY_ITEM_ID_AUX if id_aux is None else id_aux

    @Binder.binding_collection(
        Binder.BF_BindColor,
        CONTAINER_COLLECTION,
        "#ElectricMachineryWorkstationUI.crafting_preview_mask_color",
    )
    def get_crafting_preview_mask_color(self, index):
        # type: (int) -> tuple[float, float, float]
        return GetPreviewMaskColor(self._preview_id_aux_at(index))

    @Binder.binding(
        Binder.BF_BindBool,
        "#ElectricMachineryWorkstationUI.solder_preview_visible",
    )
    def get_solder_preview_visible(self):
        # type: () -> bool
        return self._preview_recipe is not None

    @Binder.binding(
        Binder.BF_BindBool,
        "#ElectricMachineryWorkstationUI.solder_preview_item_visible",
    )
    def get_solder_preview_item_visible(self):
        # type: () -> bool
        return self._preview_id_aux_at(SOLDER_SLOT) is not None

    @Binder.binding(
        Binder.BF_BindInt,
        "#ElectricMachineryWorkstationUI.solder_preview_item_id_aux",
    )
    def get_solder_preview_item_id_aux(self):
        # type: () -> int
        id_aux = self._preview_id_aux_at(SOLDER_SLOT)
        return EMPTY_ITEM_ID_AUX if id_aux is None else id_aux

    @Binder.binding(
        Binder.BF_BindColor,
        "#ElectricMachineryWorkstationUI.solder_preview_mask_color",
    )
    def get_solder_preview_mask_color(self):
        # type: () -> tuple[float, float, float]
        return GetPreviewMaskColor(self._preview_id_aux_at(SOLDER_SLOT))

    @Binder.binding(
        Binder.BF_BindBool,
        "#ElectricMachineryWorkstationUI.output_preview_visible",
    )
    def get_output_preview_visible(self):
        # type: () -> bool
        return self._preview_recipe is not None

    @Binder.binding(
        Binder.BF_BindBool,
        "#ElectricMachineryWorkstationUI.output_preview_item_visible",
    )
    def get_output_preview_item_visible(self):
        # type: () -> bool
        return self._preview_id_aux_at(OUTPUT_SLOT) is not None

    @Binder.binding(
        Binder.BF_BindInt,
        "#ElectricMachineryWorkstationUI.output_preview_item_id_aux",
    )
    def get_output_preview_item_id_aux(self):
        # type: () -> int
        id_aux = self._preview_id_aux_at(OUTPUT_SLOT)
        return EMPTY_ITEM_ID_AUX if id_aux is None else id_aux

    @Binder.binding(
        Binder.BF_BindColor,
        "#ElectricMachineryWorkstationUI.output_preview_mask_color",
    )
    def get_output_preview_mask_color(self):
        # type: () -> tuple[float, float, float]
        return GetPreviewMaskColor(self._preview_id_aux_at(OUTPUT_SLOT))
