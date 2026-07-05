# coding=utf-8
from .utils import SimpleEnum


class Machinery(SimpleEnum):
    ALLOY_FURNACE = "skybluetech:alloy_furnace"
    AIR_COMPRESSOR = "skybluetech:air_compressor"
    ASSEMBLER = "skybluetech:assembler"
    BATTERY_MATRIX_CONTROLLER = "skybluetech:battery_matrix_controller"
    BATTERY_MATRIX_CORE = "skybluetech:battery_matrix_core"
    BEDROCK_LAVA_DRILL_CONTROLLER = "skybluetech:bedrock_lava_drill_controller"
    CHARGER = "skybluetech:charger"
    COMPRESSOR = "skybluetech:compressor"
    CREATIVE_GENERATOR = "skybluetech:creative_generator"
    CREATIVE_POWER_ACCEPTOR = "skybluetech:creative_power_acceptor"
    CYRO_HEAT_MELTING_CHAMBER = "skybluetech:cyro_heat_melting_chamber"
    DEEPSLATE_LAVA_VIBRATOR = "skybluetech:deepslate_lava_vibrator"
    DIGGER = "skybluetech:digger"
    DISTILLATION_CHAMBER = "skybluetech:distillation_chamber"
    ELECTRIC_HEATER = "skybluetech:electric_heater"
    ELECTRIC_CRAFTER = "skybluetech:electric_crafter"
    FARMING_STATION = "skybluetech:farming_station"
    FERMENTER = "skybluetech:fermenter_controller"
    FLUID_CONDENSER = "skybluetech:fluid_condenser"
    FLUID_SPLITTER = "skybluetech:fluid_splitter"
    FORESTER = "skybluetech:forester"
    FREEZER = "skybluetech:freezer"
    GAS_BURNING_GENERATOR = "skybluetech:gas_burning_generator"
    GEO_THERMAL_GENERATOR = "skybluetech:geothermal_generator"
    HEAVY_COMPRESSOR = "skybluetech:heavy_compressor"
    HOVER_TEXT_DISPLAYER = "skybluetech:hover_text_displayer"
    HYDROPONIC_BASE = "skybluetech:hydroponic_base"
    HYDROPONIC_BED = "skybluetech:hydroponic_bed"
    HYDROPONIC_BED_SAND = "skybluetech:hydroponic_bed_sand"
    ITEM_SPLITTER = "skybluetech:item_splitter"
    MACERATOR = "skybluetech:macerator"
    MACHINERY_BASE_LIGHT = "skybluetech:machinery_base_light"
    MACHINERY_WORKSTATION = "skybluetech:machinery_workstation"
    MAGMA_CENTRIFUGE = "skybluetech:magma_centrifuge"
    MAGMA_FURNACE = "skybluetech:magma_furnace"
    METAL_PRESS = "skybluetech:metal_press"
    MINI_MINER = "skybluetech:mini_miner"
    MIXED_MACERATOR = "skybluetech:mixed_macerator"
    MIXER = "skybluetech:mixer"
    OIL_EXTRACTOR = "skybluetech:oil_extractor"
    PUMP = "skybluetech:pump"
    REACTING_THERMAL_GENERATOR = "skybluetech:reacting_thermal_generator"
    REDSTONE_FURNACE = "skybluetech:redstone_furnace"
    REDSTONE_GENERATOR = "skybluetech:redstone_generator"
    REDSTONEFLUX_BRAKE = "skybluetech:redstoneflux_brake"
    REPAIRING_ANVIL = "skybluetech:repairing_anvil"
    RF_REPEATER_PLANT = "skybluetech:rf_repeater_plant"
    SOLAR_PANEL = "skybluetech:solar_panel"
    SPLITTER = "skybluetech:splitter"
    TEMPLATE_ASSEMBLER = "skybluetech:template_assembler"
    TESLA_PLANT = "skybluetech:tesla_plant"
    THERMAL_GENERATOR = "skybluetech:thermal_generator"
    THERMOELECTRIC_GENERATOR = "skybluetech:thermoelectric_generator"
    WIND_GENERATOR = "skybluetech:wind_generator"
    WIRELESS_RF_TRANSPORTER = "skybluetech:wireless_rf_transporter"


ALL_MACHINES = {
    Machinery.ALLOY_FURNACE,
    Machinery.AIR_COMPRESSOR,
    Machinery.ASSEMBLER,
    Machinery.BATTERY_MATRIX_CONTROLLER,
    Machinery.BATTERY_MATRIX_CORE,
    Machinery.BEDROCK_LAVA_DRILL_CONTROLLER,
    Machinery.CHARGER,
    Machinery.COMPRESSOR,
    Machinery.CREATIVE_GENERATOR,
    Machinery.CREATIVE_POWER_ACCEPTOR,
    Machinery.CYRO_HEAT_MELTING_CHAMBER,
    Machinery.DEEPSLATE_LAVA_VIBRATOR,
    Machinery.DIGGER,
    Machinery.DISTILLATION_CHAMBER,
    Machinery.ELECTRIC_HEATER,
    Machinery.ELECTRIC_CRAFTER,
    Machinery.FARMING_STATION,
    Machinery.FERMENTER,
    Machinery.FLUID_CONDENSER,
    Machinery.FLUID_SPLITTER,
    Machinery.FORESTER,
    Machinery.FREEZER,
    Machinery.GAS_BURNING_GENERATOR,
    Machinery.GEO_THERMAL_GENERATOR,
    Machinery.HEAVY_COMPRESSOR,
    Machinery.HOVER_TEXT_DISPLAYER,
    Machinery.HYDROPONIC_BASE,
    Machinery.HYDROPONIC_BED,
    Machinery.HYDROPONIC_BED_SAND,
    Machinery.ITEM_SPLITTER,
    Machinery.MACERATOR,
    Machinery.MACHINERY_BASE_LIGHT,
    Machinery.MACHINERY_WORKSTATION,
    Machinery.MAGMA_CENTRIFUGE,
    Machinery.MAGMA_FURNACE,
    Machinery.METAL_PRESS,
    Machinery.MINI_MINER,
    Machinery.MIXED_MACERATOR,
    Machinery.MIXER,
    Machinery.OIL_EXTRACTOR,
    Machinery.REACTING_THERMAL_GENERATOR,
    Machinery.PUMP,
    Machinery.REDSTONE_FURNACE,
    Machinery.REDSTONE_GENERATOR,
    Machinery.REPAIRING_ANVIL,
    Machinery.RF_REPEATER_PLANT,
    Machinery.SOLAR_PANEL,
    Machinery.SPLITTER,
    Machinery.TESLA_PLANT,
    Machinery.THERMAL_GENERATOR,
    Machinery.THERMOELECTRIC_GENERATOR,
    Machinery.WIND_GENERATOR,
    Machinery.WIRELESS_RF_TRANSPORTER,
}
