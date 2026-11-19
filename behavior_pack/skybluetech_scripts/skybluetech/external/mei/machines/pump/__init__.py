# coding=utf-8
from skybluetech_scripts.skybluetech.client.mini_jei.machinery.pump import (
    RenderPumpPreview,
)

from ... import bridge, exports
from .._common import BuildMachine, _LayoutScriptFor
from .._layouts import LAYOUTS


CATEGORY_ID = "skybluetech:pump"
_UI_SCRIPT = None


def _Decorate(recipe, parts):
    parts["data"]["source_block_id"] = recipe.source_block_id
    parts["data"]["conditions"] = ["§7无需配方输入"]


def _BuildUIScript():
    base = _LayoutScriptFor(CATEGORY_ID, LAYOUTS[CATEGORY_ID])

    class PumpUIScript(base):
        def InitControls(self):
            base.InitControls(self)
            block_id = self.Recipe.Data["source_block_id"]
            preview = self.Child("/pump_preview")
            if preview is None or not RenderPumpPreview(block_id, preview.asNeteasePaperDoll()):
                bridge.Error("电动泵方块预览渲染失败：{}".format(block_id))

    return PumpUIScript


def Build():
    global _UI_SCRIPT
    icon_id, recipes = exports.Collection("PumpRecipe")
    if _UI_SCRIPT is None:
        _UI_SCRIPT = _BuildUIScript()
    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.pump",
        recipes=recipes,
        sort_index=126,
        decorate=_Decorate,
        ui_script=_UI_SCRIPT,
    )
