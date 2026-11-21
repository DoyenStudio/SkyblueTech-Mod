# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

from ...common.define.id_enum import Machinery
from ...common.machinery_def import oilfuel_generator
from .basic import GeneratorProcessor, MultiFluidContainer
from .core import RegisterMachine


# 模型北面是燃油口；方块实体的 Y 轴正旋转将北面转向东面。
MODEL_YAW = {"north": 0, "east": 90, "south": 180, "west": -90}


@RegisterMachine
class OilFuelGenerator(GeneratorProcessor, MultiFluidContainer):
    block_name = Machinery.OILFUEL_GENERATOR
    store_rf_max = oilfuel_generator.STORE_RF_MAX
    process_fluid = True
    recipes = oilfuel_generator.recipes
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_input_slots = (0,)
    fluid_input_slots_by_face = {RelativeFacingStrEnum.FRONT: fluid_input_slots}
    fluid_slot_max_volumes = {0: oilfuel_generator.MAX_INPUT_FUEL_VOLUME}
    upgrade_slots = 0

    def __init__(self, dim, x, y, z, block_entity_data):
        super(OilFuelGenerator, self).__init__(dim, x, y, z, block_entity_data)
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(self.xyz, dim) or {}
        yaw = MODEL_YAW.get(states.get("minecraft:cardinal_direction"), 0)
        if self.bdata[oilfuel_generator.K_MODEL_YAW] != yaw:
            self.bdata[oilfuel_generator.K_MODEL_YAW] = yaw
