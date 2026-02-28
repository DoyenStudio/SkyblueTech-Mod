# coding=utf-8
#
from .actions.register import RegisterTool, SetOriginTierSpeed

ITEM_ID = "skybluetech:skyblue_pickaxe"
TIER_SPEED = 6.0


RegisterTool(ITEM_ID)
SetOriginTierSpeed(ITEM_ID, TIER_SPEED)
