# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.pump import PumpRecipe
from .define import MachineRecipeRenderer


def RenderPumpPreview(source_block_id, paper_doll):
    palette = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
    if palette is None or not palette.DeserializeBlockPalette({
        "extra": {},
        "void": False,
        "actor": {},
        # 原生调色板按 (z, x, y) 存储，电动泵在上一层。
        "volume": (1, 1, 2),
        "common": {(source_block_id, 0): [0], (Machinery.PUMP, 0): [1]},
        "eliminateAir": True,
    }):
        return False
    geometry_name = "geometry.skybluetech.pump_recipe." + source_block_id.replace(":", "_")
    geometry_id = CF.CreateBlockGeometry(LEVEL_ID).CombineBlockPaletteToGeometry(
        palette, geometry_name
    )
    if geometry_id is None:
        return False
    return paper_doll.RenderBlockGeometryModel({
        "block_geometry_model_name": geometry_id,
        "scale": 1.9,
        "init_rot_x": -72,
        "init_rot_y": 0,
        "init_rot_z": 30,
    })


class PumpRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = Machinery.PUMP
    render_ui_def_name = "RecipeCheckerLib.pump_recipes"

    def RenderInit(self, panel):
        MachineRecipeRenderer.RenderInit(self, panel)
        preview = panel["content/body/pump_preview"].asNeteasePaperDoll()
        preview.SetVisible(bool(RenderPumpPreview(self.recipe.source_block_id, preview.base)))

    def ProgressTip(self):
        return ["§7无需配方输入"]


PumpRecipe.SetRenderer(PumpRecipeRenderer)
