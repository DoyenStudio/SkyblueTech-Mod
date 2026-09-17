# coding=utf-8
from skybluetech_scripts.skybluetech.common.events.machinery.electric_crafter import (
    ElectricCrafterUpdateRecipe,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electric_crafter import (
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdateGenericProgressL2R, UpdatePowerBar

PROGRESS_PATH = MAIN_PATH / "progress"
POWER_PATH = MAIN_PATH / "power_bar"
GRID_PATH = MAIN_PATH / "crafting_grid"

MASK_REL_PATH = "item_cell_overlay_ref/mask"
ITEM_RENDERED_REL_PATH = "item_cell_overlay_ref/item_renderer"

DEFAULT_GRAY_COLOR = 0x8F * 1.0 / 0xFF


@RegistToolDeltaScreen("ElectricCrafterUI.main", is_proxy=True)
class ElectricCrafterUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPageIndirectional,)

    def OnCreate(self):
        self.power = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PROGRESS_PATH)
        self.grid = self.GetElement(GRID_PATH).asGrid()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        UpdatePowerBar(self.power, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)

    @MachinePanelUIProxyEx.Listen(ElectricCrafterUpdateRecipe)
    def onUpdateRecipe(self, event):
        # type: (ElectricCrafterUpdateRecipe) -> None
        for i, item_and_aux in enumerate(event.slotitems):
            slot = self.grid.GetGridItem(i % 3, i // 3)
            mask = slot[MASK_REL_PATH].asImage()
            ir = slot[ITEM_RENDERED_REL_PATH].asItemRenderer()
            if item_and_aux is None:
                gray = DEFAULT_GRAY_COLOR * 0.5
                mask.SetSpriteColor((gray, gray, gray))
                ir.SetVisible(False)
            else:
                gray = DEFAULT_GRAY_COLOR
                mask.SetSpriteColor((gray, gray, gray))
                ir.SetVisible(True)
                ir.SetUiItem(Item(*item_and_aux))
