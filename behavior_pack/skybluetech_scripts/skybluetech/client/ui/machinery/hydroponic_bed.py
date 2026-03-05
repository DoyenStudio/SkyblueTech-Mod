# coding=utf-8
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.api.client import (
    NewSingleBlockPalette,
    CombineBlockPaletteToGeometry,
)
from ....common.ui_sync.machinery.hydroponic_bed import HydroponicBedUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

from ..recipe_checker import AsRecipeCheckerBtn
from ....common.machinery_def.hydroponic_bed import recipes

POWER_NODE = MAIN_PATH / "power_bar"
CROP_DISP_NODE = MAIN_PATH / "crop_disp"


@RegistToolDeltaScreen("HydroponicBedUI.main", is_proxy=True)
class HydroponicBedUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = HydroponicBedUISync.NewClient(dim, x, y, z)  # type: HydroponicBedUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.crop_disp = self.GetElement(CROP_DISP_NODE).asNeteasePaperDoll()
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            list(recipes.values()),  # pyright: ignore[reportArgumentType]
        )
        self.last_render_crop_id = None
        self.last_grow_stage = None

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.store_rf, self.sync.rf_max)
        if (
            self.last_render_crop_id == self.sync.crop_id
            and self.last_grow_stage == self.sync.grow_stage
        ):
            return
        self.last_render_crop_id = self.sync.crop_id
        self.last_grow_stage = self.sync.grow_stage
        pal = NewSingleBlockPalette(
            self.sync.crop_id or "minecraft:air", self.sync.grow_stage
        )
        geo_id = CombineBlockPaletteToGeometry(pal, "geometry.skybluetech_temp.crop_id")
        self.crop_disp.RenderBlockGeometryModel(
            geo_id,
            scale=4.5,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )
        self.last_render_crop_id = self.sync.crop_id
