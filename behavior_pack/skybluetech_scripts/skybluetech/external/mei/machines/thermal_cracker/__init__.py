# coding=utf-8
from .._common import BuildMachine, IngredientForCell
from ... import exports

_SCRIPT = None


def Decorate(recipe, parts):
    parts["data"]["conditions"] = recipe.conditions()
    parts["data"]["is_batch"] = bool(recipe.recipe_id)


def BuildUIScript(base):
    global _SCRIPT
    if _SCRIPT is not None:
        return _SCRIPT

    class ThermalCrackerUIScript(base):
        def InitControls(self):
            base.InitControls(self)
            for outputs, table, controls in (
                (False, self.INPUT_TABLE, self.InputControls),
                (True, self.OUTPUT_TABLE, self.OutputControls),
            ):
                for index, (kind, slot) in enumerate(table):
                    control = controls[index]
                    if control is not None:
                        control.SetVisible(IngredientForCell(self.Recipe, slot, kind, outputs) is not None)

        def IsContinuous(self):
            return not self.Recipe.Data["is_batch"]

        def ProgressHoverText(self):
            return "\n".join(self.Recipe.Data["conditions"])

    _SCRIPT = ThermalCrackerUIScript
    return _SCRIPT


def Build():
    icon_id, recipes = exports.Collection("ThermalCrackerRecipe")
    category, source, script = BuildMachine(
        category_id="skybluetech:thermal_cracker", icon_id=icon_id,
        name_key="skybluetech.mei.category.thermal_cracker",
        recipes=recipes, sort_index=119, decorate=Decorate,
    )
    return category, source, BuildUIScript(script)
