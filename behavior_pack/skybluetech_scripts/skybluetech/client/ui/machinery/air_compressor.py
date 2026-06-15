# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_PROGRESS,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.air_compressor import (
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    K_PLACED_DIMENSION,
    recipes,
    GetDimensionName,
    GetRecipeByDimension,
)
from ..recipe_checker import AsRecipeCheckerBtn
from ..machinery_extra_pages import PipeSettingsPageIndirectional
from .define_ex import MachinePanelUIProxyEx, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, FluidDisplayer


POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
FLUID_PATH = MAIN_PATH / "fluid_display"
DIM_TYPE_LABEL_PATH = MAIN_PATH / "databoard/dim_type_label"
AIR_TYPE_LABEL_PATH = MAIN_PATH / "databoard/air_type_label"


def GetFluidDisplayName(fluid_id):
    # type: (str | None) -> str
    if fluid_id is None:
        return "无"
    try:
        return Item(fluid_id).GetBasicInfo().itemName or fluid_id
    except Exception:
        return fluid_id


@RegistToolDeltaScreen("AirCompressorUI.main", is_proxy=True)
class AirCompressorUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))
        self.dim_type_label = self.GetElement(DIM_TYPE_LABEL_PATH).asLabel()
        self.air_type_label = self.GetElement(AIR_TYPE_LABEL_PATH).asLabel()
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        fluid = FluidSlotClient(data)
        placed_dimension = GetValue(data, K_PLACED_DIMENSION, self.pos[0])
        recipe = GetRecipeByDimension(placed_dimension)
        output_fluid_id = recipe.output_fluid_id if recipe is not None else None

        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
        self.dim_type_label.SetText(GetDimensionName(placed_dimension))
        self.air_type_label.SetText(GetFluidDisplayName(output_fluid_id))
