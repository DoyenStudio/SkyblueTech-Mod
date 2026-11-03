# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import DistillationColumn
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_column import (
    DistillationColumnRecipe,
)
from skybluetech_scripts.skybluetech.client.mini_jei.machinery.define import (
    MachineRecipeRendererBase,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import (
    FormatKelvin,
    SetHoverText,
)


class DistillationColumnRecipeRenderer(MachineRecipeRendererBase):
    recipe_icon_id = DistillationColumn.CONTROLLER
    render_ui_def_name = "RecipeCheckerLib.distillation_column_recipes"

    def RenderInit(self, panel):
        MachineRecipeRendererBase.RenderInit(self, panel)
        recipe = self.recipe
        for name, prefix, temperature in (
            ("min", "> ", recipe.min_temperature),
            ("max", "≤ ", recipe.max_temperature),
            ("fit", "≈ ", recipe.fit_temperature),
        ):
            self.GetControl(
                panel, "content/body/kelvin_disp/" + name
            ).asLabel().SetText(prefix + FormatKelvin(temperature, "%.0f %sK"))
        for slot in range(len(recipe.output_fluids) + 1, 5):
            SetHoverText(
                self.GetSlotControl(panel, "fluid", slot, True), "§7空闲"
            )
        SetHoverText(
            self.GetControl(panel, "progress_tip"),
            "§7[§bi§7] §f充分回收§7时的每批产量\n§7[§bi§7] §7实际产率§f随温度变化§7\n§f批次耗时： %.1f s"
            % (recipe.tick_duration / 20.0),
        )


DistillationColumnRecipe.SetRenderer(DistillationColumnRecipeRenderer)
