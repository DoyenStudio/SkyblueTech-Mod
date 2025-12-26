# coding=utf-8
#
from ...define.id_enum import machinery
from ...utils.fmt import FormatKelvin
from .recipe_cls import CategoryType, MachineRecipe, Input, Output, UBaseCtrl


class DistillatorChamberRecipe(MachineRecipe):
    render_progress = False
    recipe_icon_id = machinery.DISTILLATION_CHAMBER
    render_ui_def_name = "RecipeCheckerUI.distillation_chamber_recipes"

    def __init__(
        self,
        input_fluid, # type: str
        input_volume, # type: float
        output_fluid, # type: str
        output_volume, # type: float
        min_temperature, # type: float
        fit_temperature, # type: float
        max_temperature, # type: float
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: {1: Output(output_fluid, output_volume)}},
            0, 0
        )
        self.collection_name = input_fluid
        self.consume = input_volume
        self.produce = output_volume
        self.produce_matter = output_fluid
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.fit_temperature = fit_temperature

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipe.RenderInit(self, panel)
        panel["right_board/tip_text"].asLabel().SetText(FormatKelvin(self.fit_temperature))
        panel["right_board/tip_text2"].asLabel().SetText(
            "> %s\n< %s" % (
                FormatKelvin(self.min_temperature),
                FormatKelvin(self.max_temperature),
            )
        )

c2k = lambda c: c + 273