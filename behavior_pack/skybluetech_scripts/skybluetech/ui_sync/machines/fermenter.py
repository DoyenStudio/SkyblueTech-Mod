# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_STORE_RF = "r"
K_STORE_RF_MAX = "m"
K_MUD_TEMPERATURE = "t"
K_MUD_THICKNESS = "th"
K_CONTENT_VOLUME = "v"
K_EXPECTED_TEMPERATURE = "et"
K_EXPECTED_WATER_MAX_VOLUME = "ew"
K_OUT_GAS_ID = "og"
K_OUT_GAS_VOLUME = "ogv"
K_OUT_GAS_MAX_VOLUME = "ogm"
K_OUT_FLUID_ID = "of"
K_OUT_FLUID_VOLUME = "ofv"
K_OUT_FLUID_MAX_VOLUME = "ofm"
K_RECIPE = "re"
K_STRUCTURE_STATUS = "s"
K_STRUCTURE_LACK_BLOCKS = "sl"
K_GAS_PRODUCT_SPEED = "gp"
K_FLUID_PRODUCT_SPEED = "fp"


class FermenterUISync(MachineUISync):
    store_rf = 0
    store_rf_max = 0
    mud_temperature = 0.0
    mud_thickness = 0.0
    content_volume_pc = 0.0
    expected_temperature = 0.0
    expected_water_max_volume = 0.0
    recipe_id = 0
    structure_status = 0
    structure_lack_blocks = {} # type: dict[str, int]
    out_gas_id = None # type: str | None
    out_gas_volume = 0.0
    out_gas_max_volume = 0.0
    out_fluid_id = None # type: str | None
    out_fluid_volume = 0.0
    out_fluid_max_volume = 0.0
    gas_product_speed = 0.0
    fluid_product_speed = 0.0

    def Unmarshal(self, data):
        self.store_rf = data[K_STORE_RF]
        self.store_rf_max = data[K_STORE_RF_MAX]
        self.mud_temperature = data[K_MUD_TEMPERATURE]
        self.mud_thickness = data[K_MUD_THICKNESS]
        self.content_volume_pc = data[K_CONTENT_VOLUME]
        self.recipe_id = data[K_RECIPE]
        self.structure_status = data[K_STRUCTURE_STATUS]
        self.structure_lack_blocks = data[K_STRUCTURE_LACK_BLOCKS]
        self.expected_temperature = data[K_EXPECTED_TEMPERATURE]
        self.expected_water_max_volume = data[K_EXPECTED_WATER_MAX_VOLUME]
        self.out_gas_id = data[K_OUT_GAS_ID]
        self.out_gas_volume = data[K_OUT_GAS_VOLUME]
        self.out_gas_max_volume = data[K_OUT_GAS_MAX_VOLUME]
        self.out_fluid_id = data[K_OUT_FLUID_ID]
        self.out_fluid_volume = data[K_OUT_FLUID_VOLUME]
        self.out_fluid_max_volume = data[K_OUT_FLUID_MAX_VOLUME]
        self.gas_product_speed = data[K_GAS_PRODUCT_SPEED]
        self.fluid_product_speed = data[K_FLUID_PRODUCT_SPEED]

    def Marshal(self):
        return {
            K_STORE_RF: self.store_rf,
            K_STORE_RF_MAX: self.store_rf_max,
            K_MUD_TEMPERATURE: self.mud_temperature,
            K_MUD_THICKNESS: self.mud_thickness,
            K_CONTENT_VOLUME: self.content_volume_pc,
            K_RECIPE: self.recipe_id,
            K_STRUCTURE_STATUS: self.structure_status,
            K_STRUCTURE_LACK_BLOCKS: self.structure_lack_blocks,
            K_EXPECTED_TEMPERATURE: self.expected_temperature,
            K_EXPECTED_WATER_MAX_VOLUME: self.expected_water_max_volume,
            K_OUT_GAS_ID: self.out_gas_id,
            K_OUT_GAS_VOLUME: self.out_gas_volume,
            K_OUT_GAS_MAX_VOLUME: self.out_gas_max_volume,
            K_OUT_FLUID_ID: self.out_fluid_id,
            K_OUT_FLUID_VOLUME: self.out_fluid_volume,
            K_OUT_FLUID_MAX_VOLUME: self.out_fluid_max_volume,
            K_GAS_PRODUCT_SPEED: self.gas_product_speed,
            K_FLUID_PRODUCT_SPEED: self.fluid_product_speed,
        }
