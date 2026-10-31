# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.hydroponic_bed_sand import (
    HydroponicBedSandRecipe,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.machinery_def.hydroponic_bed_sand import (
    POWER_COST,
)
from .hydroponic_bed import HydroponicBedRecipeRenderer


class HydroponicBedSandRecipeRenderer(HydroponicBedRecipeRenderer):
    render_progress = False
    recipe_icon_id = machinery.Machinery.HYDROPONIC_BED_SAND
    render_ui_def_name = "RecipeCheckerLib.hydroponic_bed_sand_recipes"
    RETURN_SEED = False
    POWER_COST = POWER_COST

    def __init__(self, recipe):
        # type: (HydroponicBedSandRecipe) -> None
        HydroponicBedRecipeRenderer.__init__(self, recipe)
        self.palette = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
        self.palette.DeserializeBlockPalette({
            "extra": {},
            "void": False,
            "actor": {},
            "volume": (1, 1, 1),
            "common": {(self.recipe.crop_block_id, 0): [0]},
            "eliminateAir": True,
        })
        self.geo_id = CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
            self.palette,
            'geometry.skybluetech_temp.crop_geo_' + self.recipe.crop_block_id,
        )
        self.view_grow_progress = 0

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        self.view_grow_progress = min(
            1, self.view_grow_progress + self.recipe.once_grow_progress * 0.2
        )
        self.update_animation(self.view_grow_progress)
        self.update_crop_model(self.view_grow_progress)
        if self.view_grow_progress >= 1:
            self.view_grow_progress = 0

    def DeRender(self, panel):
        # type: (UBaseCtrl) -> None
        HydroponicBedRecipeRenderer.DeRender(self, panel)
        self.palette = None
        self.geo_id = None

    def update_crop_model(self, progress):
        # type: (float) -> None
        if self.crop_renderer is None:
            return
        self.crop_renderer.RenderBlockGeometryModel(
            self.geo_id,
            scale=0.5 + 4 * progress,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )
        self.crop_renderer.SetFullPos(
            "y",
            UICtrlPosData(follow_type="parent", absolute_value=-20 * progress + 8),
        )


HydroponicBedSandRecipe.SetRenderer(HydroponicBedSandRecipeRenderer)
