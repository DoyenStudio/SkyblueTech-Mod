# coding=utf-8
#
import random
import uuid
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.api.client.block import (
    NewSingleBlockPalette,
    CombineBlockPaletteToGeometry,
)
from ....common.define.id_enum import machinery
from ..core import ItemDisplayer
from .define import CategoryType, MachineRecipe, Input, Output, UBaseCtrl

gUid = 0


def uid():
    global gUid
    gUid += 1
    return gUid


class HydroponicBedRecipe(MachineRecipe):
    render_progress = False
    recipe_icon_id = machinery.HYDROPONIC_BED
    render_ui_def_name = "RecipeCheckerLib.hydroponic_bed_recipes"

    def __init__(
        self,
        crop_block_id,  # type: str
        seed_item,  # type: str
        grow_stage_ticks,  # type: int
        stages,  # type: int
        seed_output_probs,  # type: list[float]
        harvest_outputs,  # type: list[Output]
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(seed_item, 1)}},
            {CategoryType.ITEM: {i + 1: j for i, j in enumerate(harvest_outputs)}},
            0,
            0,
        )
        self.crop_block_id = crop_block_id
        self.seed_item = seed_item
        self.grow_stage_ticks = grow_stage_ticks
        self.stages = stages
        self.seed_output_probs = seed_output_probs
        self.harvest_outputs = harvest_outputs

    def rand_seed_count(self):
        r = random.random()
        for i, prob in enumerate(self.seed_output_probs):
            r -= prob
            if r <= 0:
                return i + 0  # at least 1
        # ...
        return len(self.seed_output_probs)

    def rand_harvest_output(self):
        for output in self.harvest_outputs:
            if output.prob >= random.random():
                yield output

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self._last_stage = 0
        self.crop_render = panel["crop_disp"].asNeteasePaperDoll()
        ItemDisplayer(panel["seed_item"], Item(self.seed_item))
        outputs_stack = panel["outputs_stack"]
        for output in [Output(self.seed_item)] + self.harvest_outputs:
            ctrl = outputs_stack.AddElement(
                "SkybluePanelLib.item_displayer", "crop_item_disp%s" % uid()
            )
            ItemDisplayer(ctrl, Item(output.id), prob=output.prob)
        self.updateCropModel(0)

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        stage = ticks // 30 % self.stages
        if stage != self._last_stage:
            self._last_stage = stage
            self.updateCropModel(stage)

    def updateCropModel(self, stage):
        # type: (int) -> None
        pal = NewSingleBlockPalette(self.crop_block_id, stage)
        geo_id = CombineBlockPaletteToGeometry(
            pal, "geometry.skybluetech_temp.crop_geo_" + self.crop_block_id
        )
        self.crop_render.RenderBlockGeometryModel(
            geo_id,
            scale=4.6,
            init_rot_x=-90,
            init_rot_y=0,
            init_rot_z=90,
            rotation_axis=(0, 1, 0),
        )


c2k = lambda c: c + 273
