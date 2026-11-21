# coding=utf-8
from ...define.global_config import BUCKET_VOLUME
from ...define.id_enum import Machinery
from .define import CategoryType, Input, MachineRecipeBase


class EffluentOutfallRecipe(MachineRecipeBase):
    recipe_icon_id = Machinery.EFFLUENT_OUTFALL
    BIOME_LABELS = {
        "any": "任意群系",
        "river_ocean": "河流或海洋群系",
        "water": "河流、海洋或沼泽群系",
    }

    def __init__(self, fluid_id, rate, biome_group):
        # type: (str, int | None, str) -> None
        if rate is not None and (rate <= 0 or int(rate) != rate):
            raise ValueError("Expected positive integer discharge rate")
        if biome_group not in self.BIOME_LABELS:
            raise ValueError("Unknown outfall biome group: " + biome_group)
        self.fluid_id = fluid_id
        self.rate = rate
        self.biome_group = biome_group
        # 配方页用一桶作展示量，耗时只驱动进度条。
        ticks = int((BUCKET_VOLUME + rate - 1) // rate) if rate is not None else 0
        MachineRecipeBase.__init__(
            self, {CategoryType.FLUID: {0: Input(fluid_id, BUCKET_VOLUME)}}, {}, ticks,
        )

    def RateText(self):
        return "不限速" if self.rate is None else "%d mB/t" % self.rate

    def BiomeText(self):
        return "§7放置群系： §f" + self.BIOME_LABELS[self.biome_group]

    def Marshal(self):
        return {"fluid_id": self.fluid_id, "rate": self.rate, "biome_group": self.biome_group}

    @classmethod
    def Unmarshal(cls, data):
        return cls(data["fluid_id"], data["rate"], data["biome_group"])

    def __hash__(self):
        return hash((self.fluid_id, self.rate, self.biome_group))
