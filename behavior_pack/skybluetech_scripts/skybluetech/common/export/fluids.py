# coding=utf-8
"""流体分类及 UI 材质。世界液体、桶和储罐纹理仍需资源定义。"""
from ..define.id_enum.fluids import (
    Fluids, Acid, Gas, Oil, Vanilla, Common, CommonGas, CommonOil, CommonLiquid,
    HotFluid, ExtremeHotFluid, HotLava, DeepLava, Molten,
)
from ..define.fluids.define import BasicFluidTexture
from ..define.fluids.texture import (
    RegisterFluidTexture, GetFluidTexture, AIR, WATER, WATER_VAPOR, LAVA,
    MOLTEN_METAL, VANILLA_WATER, VANILLA_LAVA, DEEPSLATE_LAVA,
    METHANE_MUD, BASIC_FLUID, LIQUID_RESIN_STATIC,
)

__all__ = [
    "Fluids", "Acid", "Gas", "Oil", "Vanilla", "Common", "CommonGas", "CommonOil",
    "CommonLiquid", "HotFluid", "ExtremeHotFluid", "HotLava", "DeepLava", "Molten",
    "BasicFluidTexture", "RegisterFluidTexture", "GetFluidTexture",
    "AIR", "WATER", "WATER_VAPOR", "LAVA", "MOLTEN_METAL", "VANILLA_WATER",
    "VANILLA_LAVA", "DEEPSLATE_LAVA", "METHANE_MUD", "BASIC_FLUID", "LIQUID_RESIN_STATIC",
]
