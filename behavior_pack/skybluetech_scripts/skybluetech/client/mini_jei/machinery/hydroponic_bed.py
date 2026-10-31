# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.hydroponic_bed import (
    HydroponicBedRecipe,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.machinery_def.hydroponic_bed import POWER_COST
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import UpdateRecipePower
from ...ui.machinery.utils import FormatRF, SetHoverText, UpdateProgress
from ..core import RecipeRenderer


class HydroponicBedRecipeRenderer(RecipeRenderer):
    render_progress = False
    recipe_icon_id = machinery.Machinery.HYDROPONIC_BED
    render_ui_def_name = "RecipeCheckerLib.hydroponic_bed_recipes"
    RETURN_SEED = True
    POWER_COST = POWER_COST

    @classmethod
    def GetRenderHeight(cls, recipe):
        # type: (HydroponicBedRecipe) -> int
        outputs = len(recipe.harvest_outputs) + (1 if cls.RETURN_SEED else 0)
        extra_rows = (max(0, outputs - 3) + 2) // 3
        return 62 + 20 * extra_rows

    def __init__(self, recipe):
        # type: (HydroponicBedRecipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.crop_renderer = None
        self.power_ctrl = None
        self.progress_ctrl = None
        self.seed_item_disp = None
        self.output_renderers = []
        self.stages = max(1, getattr(recipe, "stages", 1))

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self._last_stage = 0
        content = panel["content"]
        body = content["body"]
        self.power_ctrl = content["power"]
        self.progress_ctrl = body["progress"]
        self.crop_renderer = panel["content/body/shell/crop"].asNeteasePaperDoll()
        self.seed_item_disp = ItemDisplayer(
            panel["content/body/seed/0"], Item(self.recipe.seed_item)
        )
        outputs = []
        if self.RETURN_SEED:
            outputs.append((Item(self.recipe.seed_item), 1.0))
        for output in self.recipe.harvest_outputs:
            outputs.append((
                Item(output.id, max(0, output.aux), count=int(output.count)),
                output.prob,
            ))
        outputs_panel = body["outputs"]
        height = self.GetRenderHeight(self.recipe)
        if height > 62:
            # 只给新增产物腾出行空间，20px 槽位与作物预览保持原来的像素尺寸。
            content_width = content.GetSize()[0]
            panel.SetSize((panel.GetSize()[0], height))
            content.SetSize((content_width, height))
            content["background"].SetSize((content_width, height))
            body.SetSize((content_width, height))
            body["seed"].SetSize((content_width, height))
            outputs_panel.SetSize((content_width, height))
        self.output_renderers = []
        for index in range(max(3, len(outputs))):
            if index < 3:
                ctrl = outputs_panel[str(index)]
            else:
                ctrl = outputs_panel.AddElement(
                    "SkybluePanelLib.recipe_slot", "extra_output%d" % index,
                )
                ctrl.SetAnchorFrom("top_left")
                ctrl.SetAnchorTo("top_left")
                ctrl.SetPos((22 + 20 * (index % 3), 38 + 20 * (index // 3)))
            ctrl.SetVisible(index < len(outputs))
            if index < len(outputs):
                item, probability = outputs[index]
                self.output_renderers.append(ItemDisplayer(ctrl, item, prob=probability))
        SetHoverText(panel["content/body/progress_hover"], "§7作物生长预览")
        self.update_animation(0.0)
        self.update_crop_model(0)

    def RenderUpdate(self, panel, ticks):
        # type: (UBaseCtrl, int) -> None
        progress = float(ticks % (30 * self.stages)) / (30 * self.stages)
        self.update_animation(progress)
        stage = ticks // 30 % self.stages
        if stage != self._last_stage:
            self._last_stage = stage
            self.update_crop_model(stage)

    def update_animation(self, progress):
        # type: (float) -> None
        UpdateProgress(self.progress_ctrl, progress)
        UpdateRecipePower(
            self.power_ctrl, 1.0 - progress, 17,
            "§7耗能功率： §f%s/t" % FormatRF(self.POWER_COST),
        )

    def DeRender(self, panel):
        # type: (UBaseCtrl) -> None
        self.crop_renderer = None
        self.power_ctrl = None
        self.progress_ctrl = None
        self.seed_item_disp = None
        self.output_renderers = []

    def update_crop_model(self, stage):
        # type: (int) -> None
        if self.crop_renderer is None:
            return
        pal = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
        pal.DeserializeBlockPalette({
            "extra": {},
            "void": False,
            "actor": {},
            "volume": (1, 1, 1),
            "common": {(self.recipe.crop_block_id, stage): [0]},
            "eliminateAir": True,
        })
        geo_id = CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
            pal,
            'geometry.skybluetech_temp.crop_geo_' + self.recipe.crop_block_id,
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
