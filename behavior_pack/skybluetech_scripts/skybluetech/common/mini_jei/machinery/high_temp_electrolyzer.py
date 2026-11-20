# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.heated_machine import HeatedMachineRecipe


class HighTempElectrolyzerRecipe(HeatedMachineRecipe):
    recipe_icon_id = Machinery.HIGH_TEMP_ELECTROLYZER
    heat_source = "底面供热"
