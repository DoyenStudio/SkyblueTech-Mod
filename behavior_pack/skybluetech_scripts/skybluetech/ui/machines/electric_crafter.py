# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, UBaseCtrl
from ...define.events.machinery.electric_crafter import ElectricCrafterUpdateRecipe
from ...ui_sync.machines.electric_crafter import ElectricCrafterUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdateGenericProgressL2R, UpdatePowerBar

PROGRESS_NODE = MAIN_PATH / "progress"
POWER_NODE = MAIN_PATH / "power_bar"
GRID_NODE = MAIN_PATH / "crafting_grid"

MASK_REL_PATH = "item_cell/bg/mask"
ITEM_RENDERED_REL_PATH = "item_cell/bg/item_renderer"


@RegistToolDeltaScreen("ElectricCrafterUI.main", is_proxy=True)
class ElectricCrafterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ElectricCrafterUISync.NewClient(dim, x, y, z) # type: ElectricCrafterUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PROGRESS_NODE)
        self.grid = self.GetElement(GRID_NODE).asGrid()

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power, self.sync.rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress)

    @MachinePanelUIProxy.Listen(ElectricCrafterUpdateRecipe)
    def onUpdateRecipe(self, event):
        # type: (ElectricCrafterUpdateRecipe) -> None
        for i, item_and_aux in enumerate(event.slotitems):
            slot = self.grid.GetGridItem(i % 3, i // 3)
            mask = slot[MASK_REL_PATH].asImage()
            ir = slot[ITEM_RENDERED_REL_PATH].asItemRenderer()
            if item_and_aux is None:
                mask.SetSpriteColor((0.5, 0.5, 0.5))
                ir.SetVisible(False)
            else:
                mask.SetSpriteColor((1, 1, 1))
                ir.SetVisible(True)
                ir.SetUiItem(Item(*item_and_aux))

