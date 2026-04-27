# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client.block import (
    NewSingleBlockPalette,
    CombineBlockPaletteToGeometry,
)
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.hydroponic_bed import (
    HydroponicBedRecipe,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from ...ui.recipe_checker.render_utils import ItemDisplayer
from .define import MachineRecipeRenderer


class HydroponicBedRecipeRenderer(MachineRecipeRenderer):
    render_progress = False
    recipe_icon_id = machinery.HYDROPONIC_BED
    render_ui_def_name = "RecipeCheckerLib.hydroponic_bed_recipes"

    def __init__(self, recipe):
        # type: (HydroponicBedRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.crop_renderer = None
        self.output_renderers = []
        self.stages = recipe.stages

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRenderer.RenderInit(self, panel)
        idx = 1
        self._last_stage = 0
        self.crop_renderer = panel["crop_disp"].asNeteasePaperDoll()
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
        stage = ticks // 30 % self.stages
        if stage != self._last_stage:
            self._last_stage = stage
            self.update_crop_model(stage)

    def update_crop_model(self, stage):
        # type: (int) -> None
        if self.crop_renderer is None:
            return
        pal = NewSingleBlockPalette(self.recipe.crop_block_id, stage)
        geo_id = CombineBlockPaletteToGeometry(
            pal, "geometry.skybluetech_temp.crop_geo_" + self.recipe.crop_block_id
        )
        self.crop_renderer.RenderBlockGeometryModel(
            geo_id,
            scale=4.6,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )


HydroponicBedRecipe.SetRenderer(HydroponicBedRecipeRenderer)
