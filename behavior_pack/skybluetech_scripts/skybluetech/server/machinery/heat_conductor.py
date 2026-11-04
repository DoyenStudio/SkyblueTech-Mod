# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.server.machinery.basic import HeatCtrl
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine


@RegisterMachine
class HeatConductor(HeatCtrl):
    """独立储热的六面导热块；沿邻接热体逐段交换热量。"""

    block_name = Machinery.HEAT_CONDUCTOR
    is_non_energy_machine = True
    store_rf_max = 0
    energy_io_mode = (2, 2, 2, 2, 2, 2)
    heat_power = 0
    spread_heat = True
    heat_capacity = 1.0
    heat_conductance = 0.5
    env_conductance = 0.0002
    heat_input_faces = None
    heat_output_faces = None
    heat_faces_follow_rotation = False
