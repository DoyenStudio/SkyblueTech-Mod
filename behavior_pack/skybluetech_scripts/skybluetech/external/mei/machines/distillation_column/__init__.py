# coding=utf-8
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin
from .._common import BuildMachine
from ... import exports


def Decorate(recipe, parts):
    for name in ("min_temperature", "max_temperature", "fit_temperature"):
        parts["data"][name] = getattr(recipe, name)
    if getattr(recipe, "chamber_multiplier", None):
        parts["data"]["conditions"] = [
            "§7[§bi§7] 小型蒸馏仓§f适用配方\n§7[§6!§7] 过高的温度将导致原料§6损耗加剧\n§f批次耗时： %.2f s"
            % (recipe.tick_duration / 20.0),
        ]
        return
    parts["data"]["conditions"] = [
        "§7[§bi§7] §f充分蒸馏§7时的每批产量\n§7[§bi§7] §7实际产率§f随温度变化§7\n§f批次耗时： %.1f s"
        % (recipe.tick_duration / 20.0),
    ]


def Labels(recipe):
    data = recipe.Data
    return {
        "/kelvin_disp/min": "> " + FormatKelvin(data["min_temperature"]),
        "/kelvin_disp/max": "≤ " + FormatKelvin(data["max_temperature"]),
        "/kelvin_disp/fit": "≈ " + FormatKelvin(data["fit_temperature"]),
    }


def Build():
    icon_id, recipes = exports.Collection("DistillationColumnRecipe")
    return BuildMachine(
        category_id="skybluetech:distillation_column",
        icon_id=icon_id,
        name_key="skybluetech.mei.category.distillation_column",
        recipes=recipes,
        sort_index=117,
        decorate=Decorate,
        labels=Labels,
    )
