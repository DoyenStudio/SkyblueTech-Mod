# coding=utf-8
from .utils import SimpleEnum


# 方块 ID 保留旧值，兼容现有存档。
class ItemPipe(SimpleEnum):
    STEEL = "skybluetech:item_transport_cable_steel"
    INVAR = "skybluetech:item_transport_cable_invar"


class FluidPipe(SimpleEnum):
    ACIDPROOF = "skybluetech:pipe_acidproof"
    BRONZE = "skybluetech:pipe_bronze"
    CHEMICAL = "skybluetech:pipe_chemical"
    CUPRONICKEL = "skybluetech:pipe_cupronickel"
    ULTRAHEATINUM = "skybluetech:pipe_ultraheatinum"


class Wire(SimpleEnum):
    TIN = "skybluetech:wire_tin"
    TIN_INSULATED = "skybluetech:wire_insulated_tin"
    COPPER = "skybluetech:wire_copper"
    COPPER_INSULATED = "skybluetech:wire_insulated_copper"
    SILVER = "skybluetech:wire_silver"
    SILVER_INSULATED = "skybluetech:wire_insulated_silver"
    SUPER_CONDUCT = "skybluetech:wire_superconduct"
    SUPER_CONDUCT_INSULATED = "skybluetech:wire_insulated_superconduct"
    CREATIVE = "skybluetech:wire_creative"
    CREATIVE_INSULATED = "skybluetech:wire_insulated_creative"


class Ore(SimpleEnum):
    ALUMINUM = "skybluetech:aluminum_ore"
    TIN = "skybluetech:tin_ore"
    LEAD = "skybluetech:lead_ore"
    NICKEL = "skybluetech:nickel_ore"
    PLATINUM = "skybluetech:platinum_ore"
    SILVER = "skybluetech:silver_ore"
    TITANIUM = "skybluetech:titanium_ore"
    URANIUM = "skybluetech:uranium_ore"
    TIN_DEEPSLATE = "skybluetech:deepslate_tin_ore"
    LEAD_DEEPSLATE = "skybluetech:deepslate_lead_ore"
    NICKEL_DEEPSLATE = "skybluetech:deepslate_nickel_ore"
    PLATINUM_DEEPSLATE = "skybluetech:deepslate_platinum_ore"
    SILVER_DEEPSLATE = "skybluetech:deepslate_silver_ore"
    URANIUM_DEEPSLATE = "skybluetech:deepslate_uranium_ore"
    NETHER_SULFUR = "skybluetech:nether_sulfur_ore"


class Tank(SimpleEnum):
    BRONZE = "skybluetech:tank_bronze"
    INVAR = "skybluetech:tank_invar"
    STEEL = "skybluetech:tank_steel"
    PLATINUM = "skybluetech:tank_platinum"
    CREATIVE = "skybluetech:tank_creative"


FAMICOM = "skybluetech:famicom"
RESIN_COLLECTOR = "skybluetech:resin_collector"
DUST_BLOCK = "skybluetech:dust_block"
MACHINERY_FRAME = "skybluetech:machinery_frame"
