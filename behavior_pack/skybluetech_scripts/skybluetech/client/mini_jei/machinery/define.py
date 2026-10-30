# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.skybluetech.common.mini_jei import Recipe
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    MachineRecipeBase,
    MachineRecipe,
    GeneratorRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import FluidDisplayer
from ..core import RecipeRenderer


class MachineRecipeRendererBase(RecipeRenderer):
    def __init__(self, recipe):
        # type: (Recipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        recipe = self.recipe
        input_items = recipe.inputs.get("item", {})
        for slot, input in input_items.items():
            item = input.id
            is_tag = input.is_tag
            if is_tag:
                try:
                    item_id = next(iter(GetItemsByTag(item)))
                    item_aux = 0
                except StopIteration:
                    raise ValueError("tag2item not found: " + item)
            else:
                item_id = item
                item_aux = input.aux if input.aux != -1 else 0 # TODO: 如果 aux=-1, 应当渲染所有 aux 对应的方块
            ItemDisplayer(
                panel["slot%d" % slot],
                Item(item_id, item_aux, count=int(input.count)),
                tag=item if is_tag else None,
                not_consumed=input.count == 0,
            )
        output_items = recipe.outputs.get("item", {})
        for slot, output in output_items.items():
            item_id = output.id
            ItemDisplayer(
                panel["slot%d" % slot],
                Item(item_id, 0, count=int(output.count)),
                prob=output.prob,
            )
        input_fluids = recipe.inputs.get("fluid", {})
        if input_fluids:
            max_input_fluid_volume = max(
                input_fluids.values(), key=lambda x: x.count
            ).count
        for slot, input in input_fluids.items():
            FluidDisplayer(
                panel["fluid%d" % slot], input.id, input.count, max_input_fluid_volume
            )
        output_fluids = recipe.outputs.get("fluid", {})
        if output_fluids:
            max_output_fluid_volume = max(
                output_fluids.values(), key=lambda x: x.count
            ).count
        for slot, output in output_fluids.items():
            FluidDisplayer(
                panel["fluid%d" % slot],
                output.id,
                output.count,
                max_output_fluid_volume,
            )


def _has(panel, name):
    # type: (UBaseCtrl, str) -> bool
    try:
        panel[name]
    except ValueError:
        return False
    return True


def _secs(ticks):
    # type: (float) -> str
    t = ticks / 20.0
    return "%.1f" % t if t < 100 else "%d" % round(t)


class _AnimatedRenderer(MachineRecipeRendererBase):
    """
    配方行使用与机器界面同款的组件, 按控件名驱动:
      progress     进度 (原版箭头 / 机器原有贴图 / 扁平图标 / 内凹管道), UpdateProgress 按组件标记的方向填充
      progress_tip 盖在进度上的悬停层: 耗时 + 各机器的附加条件 (温度要求、维度等, 见 ProgressTip)
      power_bar    能量条 (energy_meter): 耗电从满格随进度扣, 发电随进度充满, 悬停写耗能 / 产能
      flame        火焰 (burn_flame): 随进度燃尽
    """

    render_progress = True

    def ProgressTip(self):
        # type: () -> list[str]
        """进度悬停的附加行 (子类覆写): 温度要求、维度、需要的升级等。"""
        return []

    def PowerTip(self):
        # type: () -> str | None
        return None

    def PowerTotal(self):
        # type: () -> float
        return 0

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        from ...ui.machinery.utils import SetHoverText, UpdatePowerBar

        MachineRecipeRendererBase.RenderInit(self, panel)
        # 机器里有、这条配方不用的流体槽 (同 MEI: 照画成空槽), 悬停写明是空的
        used = set(self.recipe.inputs.get("fluid", {})) | set(self.recipe.outputs.get("fluid", {}))
        for i in range(8):
            if i not in used and _has(panel, "fluid%d" % i):
                SetHoverText(panel["fluid%d" % i], "§7空（这条配方不用）")
        self.has_progress = _has(panel, "progress")
        self.has_flame = _has(panel, "flame")
        self.has_power = _has(panel, "power_bar") and self.PowerTip() is not None
        if _has(panel, "progress_tip"):
            lines = []
            if self.recipe.tick_duration:
                lines.append("§7耗时： §f%s 秒" % _secs(self.recipe.tick_duration))
            lines.extend(self.ProgressTip())
            SetHoverText(panel["progress_tip"], "\n".join(lines) or "§7（只表示流向）")
        if self.has_power:
            self.RenderPower(panel, 0.0)
        elif _has(panel, "power_bar"):
            UpdatePowerBar(panel["power_bar"], 0, 1, hover="§7（不耗电）")

    def RenderPower(self, panel, p):
        # type: (UBaseCtrl, float) -> None
        raise NotImplementedError

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        from ...ui.machinery.utils import UpdateProgress

        td = self.recipe.tick_duration * 3
        if not self.render_progress or td <= 0:  # 连续过程 (蒸馏 / 蒸发) 只画静态箭头
            return
        p = (render_ticks * 2.0) % td / td
        if self.has_progress:
            UpdateProgress(panel["progress"], p)
        if self.has_flame:
            UpdateProgress(panel["flame"], 1 - p)
        if self.has_power:
            self.RenderPower(panel, p)


class MachineRecipeRenderer(_AnimatedRenderer):
    def __init__(self, recipe):
        # type: (MachineRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def PowerTotal(self):
        return self.recipe.power_cost * self.recipe.tick_duration

    def PowerTip(self):
        from ...ui.machinery.utils import FormatRF

        if not self.recipe.power_cost:
            return None
        return "§7耗能： §f%s/t（共 %s）" % (FormatRF(self.recipe.power_cost), FormatRF(self.PowerTotal()))

    def RenderPower(self, panel, p):
        # 耗电: 从满格随进度扣 (同 MEI 配方页)
        from ...ui.machinery.utils import UpdatePowerBar

        total = max(1, self.PowerTotal())
        UpdatePowerBar(panel["power_bar"], (1 - p) * total, total, hover=self.PowerTip())


class GeneratorRecipeRenderer(_AnimatedRenderer):
    def __init__(self, recipe):
        # type: (GeneratorRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def PowerTotal(self):
        return self.recipe.output_power * self.recipe.tick_duration

    def PowerTip(self):
        from ...ui.machinery.utils import FormatRF

        return "§7产能： §f%s/t（共 %s）" % (FormatRF(self.recipe.output_power), FormatRF(self.PowerTotal()))

    def RenderPower(self, panel, p):
        # 发电: 随进度充满 (同 MEI 配方页)
        from ...ui.machinery.utils import UpdatePowerBar

        total = max(1, self.PowerTotal())
        UpdatePowerBar(panel["power_bar"], p * total, total, hover=self.PowerTip())


__all__ = [
    "MachineRecipe",
    "MachineRecipeBase",
    "GeneratorRecipe",
]
