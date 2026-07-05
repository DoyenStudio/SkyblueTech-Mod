# coding=utf-8
from skybluetech_scripts.tooldelta.define import UICtrlPosData, Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.tooldelta.api.client import (
    NewSingleBlockPalette,
    CombineBlockPaletteToGeometry,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.hydroponic_bed_sand import (
    HydroponicBedSandRecipe,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ..core import RecipeRenderer


class HydroponicBedSandRecipeRenderer(RecipeRenderer):
    render_progress = False
    recipe_icon_id = machinery.Machinery.HYDROPONIC_BED_SAND
    render_ui_def_name = "RecipeCheckerLib.hydroponic_bed_sand_recipes"

    def __init__(self, recipe):
        # type: (HydroponicBedSandRecipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.crop_renderer = None
        self.output_renderers = []
        self.palette = NewSingleBlockPalette(self.recipe.crop_block_id, 0)
        self.geo_id = CombineBlockPaletteToGeometry(
            self.palette,
            "geometry.skybluetech_temp.crop_geo_" + self.recipe.crop_block_id,
        )
        self.view_grow_progress = 0

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        idx = 1
        self.crop_renderer = panel["visualer/crop_disp"].asNeteasePaperDoll()
        self.seed_item_disp = ItemDisplayer(
            panel["seed_item"], Item(self.recipe.seed_item)
        )
        outputs_stack = panel["outputs_stack"]
        ctrl = outputs_stack.AddElement(
            "SkybluePanelLib.item_displayer", "crop_item_disp%s" % idx
        )
        self.output_seed_item_disp = ItemDisplayer(ctrl, Item(self.recipe.seed_item))
        for output in self.recipe.harvest_outputs:
            ctrl = outputs_stack.AddElement(
                "SkybluePanelLib.item_displayer", "crop_item_disp%s" % idx
            )
            self.output_renderers.append(
                ItemDisplayer(ctrl, Item(output.id), prob=output.prob)
            )
        self.update_crop_model(0)

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        self.view_grow_progress = min(
            1, self.view_grow_progress + self.recipe.once_grow_progress * 0.2
        )
        self.update_crop_model(self.view_grow_progress)
        if self.view_grow_progress >= 1:
            self.view_grow_progress = 0

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
