# coding=utf-8
#
from .actions.register import RegisterTool, SetOriginTierSpeed


ITEM_ID = "skybluetech:skyblue_hoe"
TIER_SPEED = 6.0
DIRTLIKE_BLOCK = {"minecraft:dirt", "minecraft:grass_block"}
HOE_POWER_COST = 200


RegisterTool(ITEM_ID)
SetOriginTierSpeed(ITEM_ID, TIER_SPEED)

