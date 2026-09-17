# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.hydroponic_bed_sand import (
    K_CROP_BLOCK_ID,
    K_GROW_PROGRESS,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import (
    CombineBlockPaletteToGeometry,
    GetBlockEntityData,
    NewSingleBlockPalette,
)
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
CROP_DISP_PATH = MAIN_PATH / "visualer/crop_disp"


@RegistToolDeltaScreen("HydroponicBedSandUI.main", is_proxy=True)
class HydroponicBedSandUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.crop_disp = self.GetElement(CROP_DISP_PATH).asNeteasePaperDoll()
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )
        self.last_render_crop_block_id = None
        self.last_progress = None

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        crop_block_id = GetValue(data, K_CROP_BLOCK_ID, None)
        grow_progress = GetValue(data, K_GROW_PROGRESS, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        if (
            self.last_render_crop_block_id == crop_block_id
            and self.last_progress == grow_progress
        ):
            return
        self.last_render_crop_block_id = crop_block_id
        self.last_progress = grow_progress
        pal = NewSingleBlockPalette(crop_block_id or "minecraft:air", 0)
        geo_id = CombineBlockPaletteToGeometry(
            pal, "geometry.skybluetech_temp.crop_block_id"
        )
        self.crop_disp.RenderBlockGeometryModel(
            geo_id,
            scale=0.5 + 4 * grow_progress,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )
        self.crop_disp.SetFullPos(
            "y",
            UICtrlPosData(follow_type="parent", absolute_value=-20 * grow_progress + 8),
        )
        self.last_render_crop_block_id = crop_block_id
