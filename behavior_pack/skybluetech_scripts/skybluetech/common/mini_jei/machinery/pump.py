# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.global_config import BUCKET_VOLUME
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import (
    CategoryType,
    MachineRecipe,
    Output,
)


class PumpRecipe(MachineRecipe):
    """电动泵抽取世界流体源的虚拟配方。"""

    recipe_icon_id = Machinery.PUMP

    def __init__(self, source_block_id):
        # type: (str) -> None
        MachineRecipe.__init__(
            self,
            inputs={},
            outputs={CategoryType.FLUID: {0: Output(source_block_id, BUCKET_VOLUME)}},
            power_cost=0,
            tick_duration=0,
        )
        self.source_block_id = source_block_id

    def Marshal(self):
        return {"source_block_id": self.source_block_id}

    @classmethod
    def Unmarshal(cls, data):
        return cls(data["source_block_id"])
