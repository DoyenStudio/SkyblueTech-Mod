# coding=utf-8
from .basic import MachineryOperationC2S


class ElectricMachineryWorkstationSelectRecipe(MachineryOperationC2S):
    name = "st:EMWSR"
    extra_attrs = ("output_item_id",)

    def __init__(self, x, y, z, output_item_id, player_id=""):
        MachineryOperationC2S.__init__(self, x, y, z, player_id)
        self.output_item_id = output_item_id
