IO_ENERGY = "skybluetech:fermenter_io_energy"
IO_FLUID1 = "skybluetech:fermenter_io_fluid1"
IO_FLUID2 = "skybluetech:fermenter_io_fluid2"
IO_GAS = "skybluetech:fermenter_io_gas"
IO_ITEM = "skybluetech:fermenter_io_item1"
MUDBRICK = "minecraft:mud_bricks"
GLASS = "minecraft:glass"
STRUCTURE_PATTERN_MAPPING = {
    "M": MUDBRICK,
    "m": {MUDBRICK, IO_GAS, IO_ENERGY, IO_ITEM},
    "i": {MUDBRICK, IO_FLUID1, IO_FLUID2, IO_ENERGY, IO_ITEM},
    "G": GLASS,
    "g": {GLASS, MUDBRICK, IO_ENERGY}
}
STRUCTURE_PATTERN ={
    0: [
        "iii",
        "iMi",
        "i#i"
    ],
    1: [
        "MGM",
        "G G",
        "MGM"
    ],
    2: [
        "mmm",
        "mgm",
        "mmm"
    ]
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

HI_TEMPERATURE_VITALITY_REDUCE = 0.01
LO_TEMPERATURE_VITALITY_REDUCE = 0.008
VITALITY_ADD_MAX = 0.005
BATERIA_MAX_HUNGER = 1
BATERIA_MIN_HUNGER = -1
VITALITY_HUNGER_REDUCE_MAX = 0.05
HUNGER_REDUCE = 0.01

class FermenterRecipe:
    def __init__(
        self,
        color, # type: int
        vitality_matter, # type: str
        vitality_count, # type: float
        inoculate_time, # type: float
        nutrition_matter, # type: str
        nutrition_count, # type: float
        min_temperature, # type: float
        max_temperature, # type: float
        fit_temperature, # type: float
        max_grow_speed, # type: float
        max_thickness, # type: float
        produce_thickness, # type: float
        out_gas_id, # type: str
        out_gas_volume, # type: float
        out_fluid_id, # type: str
        out_fluid_volume, # type: float
        volume_reduce, # type: float
    ):
        """
        发酵池配方。

        Args:
            color (int): 发酵流体 RGB 颜色, 显示到 GUI
            vitality_matter (str): 接种物
            vitality_count (float): 接种物可增加的菌群浓度
            inoculate_time (float): 接种所需时间
            nutrition_matter (str): 营养物
            nutrition_count (float): 营养物可增加的菌群浓度
            min_temperature (float): 菌群可接受的最小温度
            max_temperature (float): 菌群可接受的最大温度
            fit_temperature (float): 菌群可接受最适温度
            max_grow_speed (float): 菌群最大生长速度
            max_thickness (float): 菌群最大浓度
            produce_thickness (float): 菌群生产的最适浓度
            out_gas_id (str): 产出的气体
            out_gas_volume (float): 单次产生气体的体积
            out_fluid_id (str): 产出的流体
            out_fluid_volume (float): 单次产生流体的体积
            volume_reduce (float): 单次生产消耗的发酵流体量
        """
        self.color = color
        "发酵流体 RGB 颜色, 显示到 GUI"
        self.vitality_matter = vitality_matter
        "接种物"
        self.vitality_count = vitality_count
        "接种物可增加的菌群浓度"
        self.inoculate_time = inoculate_time
        "接种所需时间"
        self.nutrition_matter = nutrition_matter
        "营养物"
        self.nutrition_count = nutrition_count
        "营养物可增加的菌群浓度"
        self.min_temperature = min_temperature
        "菌群可接受的最小温度"
        self.max_temperature = max_temperature
        "菌群可接受的最大温度"
        self.fit_temperature = fit_temperature
        "菌群可接受最适温度"
        self.max_grow_speed = max_grow_speed
        "菌群最大生长速度"
        self.max_thickness = max_thickness
        "菌群最大浓度"
        self.produce_thickness = produce_thickness
        "菌群生产的最适浓度"
        self.out_gas_id = out_gas_id
        "产出的气体"
        self.out_gas_volume = out_gas_volume
        "单次产生气体的体积"
        self.out_fluid_id = out_fluid_id
        "产出的流体"
        self.out_fluid_volume = out_fluid_volume
        "单次产生流体的体积"
        self.volume_reduce = volume_reduce
        "单次生产消耗的发酵流体量"


spec_recipes = {
    1: FermenterRecipe(
        color=0x9a6f4f,
        vitality_matter="minecraft:dirt",
        vitality_count=0.1,
        inoculate_time=5,
        nutrition_matter="skybluetech:bio_dust",
        nutrition_count=0.2,
        min_temperature=25,
        max_temperature=40,
        fit_temperature=30,
        max_grow_speed=0.1,
        max_thickness=0.6,
        produce_thickness=0.4,
        out_gas_id="skybluetech:methane",
        out_gas_volume=10,
        out_fluid_id="skybluetech:methane_mud",
        out_fluid_volume=0.5,
        volume_reduce=0.05,
    )
}

