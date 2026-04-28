# coding=utf-8


class Cable:
    STEEL = "skybluetech:item_transport_cable_steel"
    INVAR = "skybluetech:item_transport_cable_invar"


class Pipe:
    BRONZE = "skybluetech:pipe_bronze"
    CUPRONICKEL = "skybluetech:pipe_cupronickel"
    ULTRAHEATINUM = "skybluetech:pipe_ultraheatinum"


class Wire:
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


class Ore:
    TIN = "skybluetech:tin_ore"
    LEAD = "skybluetech:lead_ore"
    NICKEL = "skybluetech:nickel_ore"
    PLATINUM = "skybluetech:platinum_ore"
    SILVER = "skybluetech:silver_ore"
    TIN_DEEPSLATE = "skybluetech:deepslate_tin_ore"
    LEAD_DEEPSLATE = "skybluetech:deepslate_lead_ore"
    NICKEL_DEEPSLATE = "skybluetech:deepslate_nickel_ore"
    PLATINUM_DEEPSLATE = "skybluetech:deepslate_platinum_ore"
    SILVER_DEEPSLATE = "skybluetech:deepslate_silver_ore"


class Tank:
    BRONZE = "skybluetech:tank_bronze"
    INVAR = "skybluetech:tank_invar"
    STEEL = "skybluetech:tank_steel"
    PLATINUM = "skybluetech:tank_platinum"
    CREATIVE = "skybluetech:tank_creative"

    @classmethod
    def all(cls):
        return {
            cls.BRONZE,
            cls.INVAR,
            cls.STEEL,
            cls.PLATINUM,
            cls.CREATIVE,
        }


FAMICOM = "skybluetech:famicom"
RESIN_COLLECTOR = "skybluetech:resin_collector"
DUST_BLOCK = "skybluetech:dust_block"
MACHINERY_FRAME = "skybluetech:machinery_frame"
