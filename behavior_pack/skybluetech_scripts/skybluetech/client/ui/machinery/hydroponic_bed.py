# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.hydroponic_bed import (
    K_CROP_BLOCK_ID,
    K_GROW_STAGE,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import (
    CombineBlockPaletteToGeometry,
    GetBlockEntityData,
    NewSingleBlockPalette,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
CROP_DISP_PATH = MAIN_PATH / "crop_disp"


@RegistToolDeltaScreen("HydroponicBedUI.main", is_proxy=True)
class HydroponicBedUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.crop_disp = self.GetElement(CROP_DISP_PATH).asNeteasePaperDoll()
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )
        self.last_render_crop_id = None
        self.last_grow_stage = None

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        crop_block_id = GetValue(data, K_CROP_BLOCK_ID, None)
        grow_stage = GetValue(data, K_GROW_STAGE, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        if (
            self.last_render_crop_id == crop_block_id
            and self.last_grow_stage == grow_stage
        ):
            return
        self.last_render_crop_id = crop_block_id
        self.last_grow_stage = grow_stage
        pal = NewSingleBlockPalette(crop_block_id or "minecraft:air", grow_stage)
        geo_id = CombineBlockPaletteToGeometry(pal, "geometry.skybluetech_temp.crop_id")
        self.crop_disp.RenderBlockGeometryModel(
            geo_id,
            scale=4.5,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )
        self.last_render_crop_id = crop_block_id
