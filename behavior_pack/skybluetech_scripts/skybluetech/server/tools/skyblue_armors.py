# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    SKYBLUE_BOOTS,
    SKYBLUE_CHESTPLATE,
    SKYBLUE_HELMET,
    SKYBLUE_LEGGINGS,
)
from .actions.register import RegisterArmor

SKYBLUE_ARMOR_SLOTS = {
    SKYBLUE_HELMET: 0,
    SKYBLUE_CHESTPLATE: 1,
    SKYBLUE_LEGGINGS: 2,
    SKYBLUE_BOOTS: 3,
}

for _armor_id, _slot in SKYBLUE_ARMOR_SLOTS.items():
    RegisterArmor(_armor_id, _slot)
