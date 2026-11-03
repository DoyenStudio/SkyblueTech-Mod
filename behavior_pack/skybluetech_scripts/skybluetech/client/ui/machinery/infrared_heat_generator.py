# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.infrared_heat_generator import (
    MAX_KELVIN,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen

from skybluetech_scripts.skybluetech.client.ui.machinery.electric_heater import (
    ElectricHeaterUI,
)


@RegistToolDeltaScreen("InfraredHeatGeneratorUI.main", is_proxy=True)
class InfraredHeatGeneratorUI(ElectricHeaterUI):
    max_kelvin = MAX_KELVIN
