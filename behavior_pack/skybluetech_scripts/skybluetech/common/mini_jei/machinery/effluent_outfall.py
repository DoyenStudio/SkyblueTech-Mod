# coding=utf-8
from ...define.global_config import BUCKET_VOLUME
from ...define.id_enum import Machinery
from .define import CategoryType, Input, MachineRecipeBase


class EffluentOutfallRecipe(MachineRecipeBase):
    recipe_icon_id = Machinery.EFFLUENT_OUTFALL
    SETTLEMENT_TICKS = 20
    BIOME_LABELS = {
        "any": "任意群系",
        "river_ocean": "河流或海洋群系",
        "water": "河流、海洋或沼泽群系",
    }

    def __init__(self, fluid_id, rate=None, biome_group=None, volume_per_second=None):
        # 兼容扩展包按旧接口传入的 mB/t。新配方显式指定每秒量。
        if rate is not None:
            if volume_per_second is not None or rate <= 0 or int(rate) != rate:
                raise ValueError("Expected a single positive integer discharge rate")
            volume_per_second = 2 if rate == 1 else rate * self.SETTLEMENT_TICKS
        if volume_per_second is not None and (
            volume_per_second <= 0 or int(volume_per_second) != volume_per_second
        ):
            raise ValueError("Expected positive integer discharge volume per second")
        if biome_group not in self.BIOME_LABELS:
            raise ValueError("Unknown outfall biome group: " + biome_group)
        self.fluid_id = fluid_id
        self.volume_per_second = volume_per_second
        self.biome_group = biome_group
        # 一桶展示量需要若干次结算；不限速液体在下一次结算时全部排出。
        seconds = 1
        if volume_per_second is not None:
            seconds = int((BUCKET_VOLUME + volume_per_second - 1) // volume_per_second)
        MachineRecipeBase.__init__(
            self, {CategoryType.FLUID: {0: Input(fluid_id, BUCKET_VOLUME)}}, {},
            seconds * self.SETTLEMENT_TICKS,
        )

    def RateText(self):
        if self.volume_per_second is None:
            return "不限速"
        return "%d mB/s" % self.volume_per_second

    @property
    def rate(self):
        if self.volume_per_second is not None:
            return self.volume_per_second / float(self.SETTLEMENT_TICKS)
        return None

    def BiomeText(self):
        return "§7放置群系： §f" + self.BIOME_LABELS[self.biome_group]

    def Marshal(self):
        return {
            "fluid_id": self.fluid_id,
            "volume_per_second": self.volume_per_second,
            "biome_group": self.biome_group,
        }

    @classmethod
    def Unmarshal(cls, data):
        if "volume_per_second" in data:
            return cls(data["fluid_id"], biome_group=data["biome_group"],
                       volume_per_second=data["volume_per_second"])
        return cls(data["fluid_id"], data["rate"], data["biome_group"])

    def __hash__(self):
        return hash((self.fluid_id, self.volume_per_second, self.biome_group))
