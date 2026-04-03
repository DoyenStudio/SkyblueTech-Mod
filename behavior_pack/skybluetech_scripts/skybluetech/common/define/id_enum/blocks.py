# coding=utf-8


class Cable:
    STEEL = "skybluetech:item_transport_cable_steel"


class Pipe:
    BRONZE = "skybluetech:pipe_bronze"


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
