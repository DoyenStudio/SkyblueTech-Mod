# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from ....common.mini_jei.machinery.machinery_workstation import (
    MachineryWorkstationRecipe,
)
from .base import BaseComp, BasePage, TextComp, RegisterPage


@RegisterPage("skybluetech:machinery_workstation_recipe_page")
class MachineryWorkstationRecipePage(BasePage):
    def __init__(self, size=None, position=None):
        # type: (tuple[int, int] | None, tuple[int, int] | None) -> None
        BasePage.__init__(self, size, position)
        self.tip_comp = TextComp()
        self.recipe_comp = MachineryWorkstationRecipeComp()
        self.AddComps(self.tip_comp, self.recipe_comp)
        self.data = None

    def SetData(
        self,
        data,  # type: dict
    ):
        self.data = data
        return self

    def Show(self):
        self.tip_comp.SetDataBeforeShow("此机械在§3机件加工台§r的制造配方", 12)
        if self.data is not None:
            recipe_conf = self.data["recipe"]
            self.recipe_comp.SetDataBeforeShow(
                MachineryWorkstationRecipe.from_dict(recipe_conf)
            )
        BasePage.Show(self)
        self.ResetCompsPosition()
        self.tip_comp.AlignTopToY(self.Top())
        self.recipe_comp.AlignCenterToPosition(self.Center())
        return self


class MachineryWorkstationRecipeComp(BaseComp):
    def __init__(self):
        # type: () -> None
        BaseComp.__init__(
            self,
            "skybluetech:machinery_workstation_recipe_comp",
            "GuidanceComps.main",
            "machinery_workstation_recipe_comp",
            recycled=False,
        )
        self.display_recipe = None

    def SetDataBeforeShow(
        self,
        recipe,  # type: MachineryWorkstationRecipe
    ):
        self.display_recipe = recipe
        return self

    def Show(self):
        BaseComp.Show(self)
        if self.display_recipe is not None:
            self.display_recipe.RenderInit(UBaseCtrl.convertFrom(self.GetRootUINode()))
        return self
