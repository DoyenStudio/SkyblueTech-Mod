# coding=utf-8
from ..define.id_enum import Plates, Ingots
from ..mini_jei.tools.metal_hammer import MetalHammerRecipe as MHRecipe, Input

_recipes = [
    MHRecipe(Input("minecraft:copper_ingot"), Plates.COPPER),
    MHRecipe(Input("minecraft:iron_ingot"), Plates.IRON),
    MHRecipe(Input("minecraft:gold_ingot"), Plates.GOLD),
    MHRecipe(Input(Ingots.TIN), Plates.TIN),
    MHRecipe(Input(Ingots.PLATINUM), Plates.PLATINUM),
    MHRecipe(Input(Ingots.SILVER), Plates.SILVER),
    MHRecipe(Input(Ingots.BRONZE), Plates.BRONZE),
]

recipes = {i.hammer_in.id: i for i in _recipes}
