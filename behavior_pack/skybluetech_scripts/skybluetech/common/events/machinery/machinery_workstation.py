# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent
from .basic import MachineryOperationC2S


class MachineryWorkstationDoCraft(MachineryOperationC2S):
    name = "st:MWDC"
    extra_attrs = ("crafting_strength",)

    def __init__(self, x, y, z, craft_strength, player_id=""):
        # type: (int, int, int, float, str) -> None
        # TODO: do not trust client
        self.x = x
        self.y = y
        self.z = z
        self.craft_strength = craft_strength
        self.player_id = player_id


class MachineryWorkstationTransferRecipe(MachineryOperationC2S):
    name = "st:MWTR"
    extra_attrs = ("output_item_id",)

    def __init__(self, x, y, z, output_item_id, player_id=""):
        # type: (int, int, int, str, str) -> None
        # TODO: item id too long
        self.x = x
        self.y = y
        self.z = z
        self.output_item_id = output_item_id
        self.player_id = player_id
