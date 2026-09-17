# coding=utf-8
from skybluetech_scripts.skybluetech.common.events.machinery.template_assembler import (
    TemplateAssemblerUpdateRecipeEvent,
    TemplateAssemblerUpdateRecipeEvent2,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.template_assembler import (
    K_TEMPLATE_ITEM_COUNT,
    K_TEMPLATE_ITEM_ID,
    K_TEMPLATE_ITEM_IS_TAG,
    K_TEMPLATE_ITEMS,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPageIndirectional
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdateGenericProgressL2R, UpdatePowerBar

PROGRESS_PATH = MAIN_PATH / "progress"
POWER_PATH = MAIN_PATH / "power_bar"
GRID_PATH = MAIN_PATH / "crafting_grid"

MASK_REL_PATH = "item_cell_overlay_ref/mask"
ITEM_RENDERED_REL_PATH = "item_cell_overlay_ref/item_renderer"

COLOR_GRAY = 0x8B * 1.0 / 0xFF


@RegistToolDeltaScreen("TemplateAssemblerUI.main", is_proxy=True)
class TemplateAssemblerUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPageIndirectional,)

    def OnCreate(self):
        self.power = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PROGRESS_PATH)
        self.template_items_required = [None] * 9  # type: list[int | None]
        self.template_items_count_required = [0] * 9  # type: list[int]
        self.update_item_required()
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        UpdatePowerBar(self.power, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)

    @MachinePanelUIProxyEx.Listen(TemplateAssemblerUpdateRecipeEvent)
    @MachinePanelUIProxyEx.Listen(TemplateAssemblerUpdateRecipeEvent2)
    def on_update_recipe_event(self, event):
        self.update_item_required()

    def update_item_required(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        template_items = data.get(K_TEMPLATE_ITEMS, [])
        for i in range(9):
            try:
                item_data = template_items[i]
                item_id_or_tag = (
                    GetValue(item_data, K_TEMPLATE_ITEM_ID, "minecraft:barrier")
                    or "minecraft:barrier"
                )
                is_tag = GetValue(item_data, K_TEMPLATE_ITEM_IS_TAG, False)
                count = GetValue(item_data, K_TEMPLATE_ITEM_COUNT, 0)
            except IndexError:
                item_id_or_tag = None
                is_tag = False
                count = 0
            if item_id_or_tag is None:
                self.template_items_required[i] = None
                self.template_items_count_required[i] = 0
            else:
                if is_tag:
                    item_id = next(iter(GetItemsByTag(item_id_or_tag)))
                else:
                    item_id = str(item_id_or_tag)
                self.template_items_required[i] = Item(item_id).GetBasicInfo().id_aux
                self.template_items_count_required[i] = count

    @Binder.binding_collection(
        Binder.BF_BindBool,
        "netease_container",
        "#TemplateAssemblerUI.crafting_slot_item_visual_visible",
    )
    def get_grid_item_visible(self, index):
        # type: (int) -> bool
        return self.template_items_required[index] is not None

    @Binder.binding_collection(
        Binder.BF_BindColor,
        "netease_container",
        "#TemplateAssemblerUI.crafting_slot_item_visual_mask_color",
    )
    def get_grid_item_mask_color(self, index):
        # type: (int) -> tuple[float, float, float]
        return (
            (COLOR_GRAY * 0.5, COLOR_GRAY * 0.5, COLOR_GRAY * 0.5)
            if self.template_items_required[index] is not None
            else (COLOR_GRAY, COLOR_GRAY, COLOR_GRAY)
        )

    @Binder.binding_collection(
        Binder.BF_BindInt,
        "netease_container",
        "#TemplateAssemblerUI.crafting_slot_item_visual_id_aux",
    )
    def get_grid_item_id_aux(self, index):
        # type: (int) -> int
        return self.template_items_required[index] or 0

    @Binder.binding_collection(
        Binder.BF_BindString,
        "netease_container",
        "#TemplateAssemblerUI.crafting_slot_item_visual_count",
    )
    def get_grid_item_count(self, index):
        # type: (int) -> str
        return (
            str(self.template_items_count_required[index])
            if self.template_items_count_required[index] > 0
            else ""
        )
