# coding=utf-8

IO_ENERGY = "skybluetech:fermenter_io_energy"
IO_FLUID1 = "skybluetech:fermenter_io_fluid1"
IO_FLUID2 = "skybluetech:fermenter_io_fluid2"
IO_GAS = "skybluetech:fermenter_io_gas"
IO_ITEM = "skybluetech:fermenter_io_item1"
MUDBRICK = "minecraft:mud_bricks"
GLASS = "minecraft:glass"
STRUCTURE_PATTERN_MAPPING = {
    "M": MUDBRICK,
    "m": [MUDBRICK, IO_GAS, IO_ENERGY, IO_ITEM],
    "i": [MUDBRICK, IO_FLUID1, IO_FLUID2, IO_ENERGY, IO_ITEM],
    "G": GLASS,
    "g": [GLASS, MUDBRICK, IO_ENERGY],
}
STRUCTURE_PATTERN = {
    0: [
        "i#i",
        "iMi",
        "iii",
    ],
    1: [
        "MGM",
        "G G",
        "MGM",
    ],
    2: [
        "mmm",
        "mgm",
        "mmm",
    ],
}
STRUCTURE_REQUIRE_BLOCKS = {
    IO_ENERGY: 1,
    IO_ITEM: 1,
    IO_FLUID1: 1,
    IO_FLUID2: 1,
    IO_GAS: 1,
}

TEMPERATURE_MIN = 10
TEMPERATURE_MAX = 50
POOL_MAX_VOLUME = 16000

HI_TEMPERATURE_VITALITY_REDUCE = 0.05
LO_TEMPERATURE_VITALITY_REDUCE = 0.04
VITALITY_ADD_MAX = 0.05
VITALITY_HUNGER_REDUCE_MAX = 0.05
THICKNESS_OVERFLOW_VITALITY_REDUCE = 2


class FermenterRecipe:
    def __init__(
        self,
        color,  # type: int
        vitality_matter,  # type: str
        inoculate_mud_volume,  # type: float
        inoculate_time,  # type: float
        nutrition_matter,  # type: str
        nutrition_value,  # type: float
        nutrition_recover_vitality,  # type: float
        hunger_reduce_speed,  # type: float
        min_temperature,  # type: float
        max_temperature,  # type: float
        fit_temperature,  # type: float
        max_grow_speed,  # type: float
        max_thickness,  # type: float
        produce_thickness,  # type: float
        out_gas_id,  # type: str
        out_gas_rate,  # type: float
        out_fluid_id,  # type: str
        out_fluid_rate,  # type: float
        volume_reduce_rate,  # type: float
    ):
        """
        发酵池配方。

        Args:
            color (int): 发酵流体 RGB 颜色, 显示到 GUI
            vitality_matter (str): 接种物
            vitality_count (float): 接种物可增加的菌群浓度
            inoculate_mud_volume (float): 接种物可增加的底物体积
            inoculate_time (float): 接种所需时间
            nutrition_matter (str): 营养物
            nutrition_value (float): 营养物可回复的饱腹值 (0, 1); 实际营养值=回复值/底物体积
            nutrition_recover_vitality (float): 营养物可恢复的菌群活力值
            hunger_reduce_speed (float): 饱腹值减少速度
            min_temperature (float): 菌群可接受的最小温度
            max_temperature (float): 菌群可接受的最大温度
            fit_temperature (float): 菌群可接受最适温度
            max_grow_speed (float): 菌群最大生长速度: 底物增加=生长速度x总体积x水占比
            max_thickness (float): 菌群最大浓度
            produce_thickness (float): 菌群生产的最适浓度
            out_gas_id (str): 产出的气体
            out_gas_rate (float): 气体产出速度: 单次产出体积=产出速度x底物体积
            out_fluid_id (str): 产出的流体
            out_fluid_rate (float): 流体产出速度: 单次产出体积=产出速度x底物体积
            volume_reduce_rate (float): 生产消耗: 单次发酵液消耗体积=生产消耗x总体积
        """
        self.color = color
        self.vitality_matter = vitality_matter
        self.inoculate_mud_volume = inoculate_mud_volume
        self.inoculate_time = inoculate_time
        self.nutrition_matter = nutrition_matter
        self.nutrition_value = nutrition_value
        self.nutrition_recover_vitality = nutrition_recover_vitality
        self.hunger_reduce_speed = hunger_reduce_speed
        self.min_temperature = min_temperature
        self.max_temperature = max_temperature
        self.fit_temperature = fit_temperature
        self.max_grow_speed = max_grow_speed
        self.max_thickness = max_thickness
        self.produce_thickness = produce_thickness
        self.fit_thickness = (self.max_thickness + self.produce_thickness) / 2
        self.out_gas_id = out_gas_id
        self.out_gas_rate = out_gas_rate
        self.out_fluid_id = out_fluid_id
        self.out_fluid_rate = out_fluid_rate
        self.volume_reduce_rate = volume_reduce_rate


spec_recipes = {
    1: FermenterRecipe(
        color=0x9A6F4F,
        vitality_matter="minecraft:dirt",
        inoculate_mud_volume=1,
        inoculate_time=5,
        nutrition_matter="skybluetech:bio_dust",
        nutrition_value=200,
        nutrition_recover_vitality=0.05,
        hunger_reduce_speed=0.01,
        min_temperature=25,
        max_temperature=40,
        fit_temperature=30,
        max_grow_speed=0.05,
        max_thickness=0.6,
        produce_thickness=0.4,
        out_gas_id="skybluetech:methane",
        out_gas_rate=0.05,
        out_fluid_id="skybluetech:methane_mud",
        out_fluid_rate=0.005,
        volume_reduce_rate=0.02,
    )
}
