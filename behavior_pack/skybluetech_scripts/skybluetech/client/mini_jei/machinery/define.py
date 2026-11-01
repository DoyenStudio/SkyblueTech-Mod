# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.mini_jei import Recipe
from skybluetech_scripts.skybluetech.common.define.recipe_layouts import LAYOUTS
from skybluetech_scripts.skybluetech.common.mini_jei.machinery import (
    MachineRecipeBase,
    MachineRecipe,
    GeneratorRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import (
    FluidDisplayer,
    InputDisplayer,
    UpdateRecipePower,
)
from ..core import RecipeRenderer


class MachineRecipeRendererBase(RecipeRenderer):
    def __init__(self, recipe):
        # type: (Recipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe
        self.controls = {}
        self.input_displayers = []  # type: list[InputDisplayer]
        # 仅本包已迁移的薄包装使用共享布局；附属自己的旧布局仍按原路径渲染。
        prefix = "RecipeCheckerLib."
        suffix = "_recipes"
        name = self.render_ui_def_name
        self.layout = None
        if name.startswith(prefix) and name.endswith(suffix):
            self.layout = LAYOUTS.get("skybluetech:" + name[len(prefix):-len(suffix)])

    def GetControl(self, panel, name):
        # type: (UBaseCtrl, str) -> UBaseCtrl
        if self.layout is not None:
            name = {
                "power_bar": "content/power",
                "progress": "content/body/progress",
                "progress_tip": "content/body/progress_hover",
                "flame": "content/body/flame",
            }.get(name, name)
        if name not in self.controls:
            self.controls[name] = panel[name]
        return self.controls[name]

    def GetSlotControl(self, panel, kind, slot, outputs=False):
        # type: (UBaseCtrl, str, int, bool) -> UBaseCtrl
        if self.layout is None:
            return self.GetControl(panel, ("fluid" if kind == "fluid" else "slot") + str(slot))
        side = "outputs" if outputs else "inputs"
        for index, (entry_kind, entry_slot) in enumerate(self.layout[side]):
            if entry_kind == kind and entry_slot is not None and int(entry_slot) == int(slot):
                path = "content/body/%s/%d" % ("output" if outputs else "input", index)
                return self.GetControl(panel, path)
        raise ValueError("No %s %s:%s in recipe layout %s" % (side, kind, slot, self.render_ui_def_name))

    def GetCatalystControl(self, panel, index, legacy_name):
        # type: (UBaseCtrl, int, str) -> UBaseCtrl
        path = "content/body/cat/%d" % index if self.layout is not None else legacy_name
        return self.GetControl(panel, path)

    def DeRender(self, panel):
        self.input_displayers = []
        self.controls.clear()

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        self.input_displayers = []
        inputs = self.GetDisplayInputs()
        outputs = self.GetDisplayOutputs()
        input_items = inputs.get("item", {})
        for slot, input in input_items.items():
            ctrl = self.GetSlotControl(panel, "item", slot)
            if input.is_tag:
                self.input_displayers.append(InputDisplayer(ctrl, input))
            else:
                item_aux = input.aux if input.aux != -1 else 0 # TODO: 如果 aux=-1, 应当渲染所有 aux 对应的方块
                ItemDisplayer(
                    ctrl,
                    Item(input.id, item_aux, count=int(input.count)),
                    not_consumed=input.count == 0,
                )
        output_items = outputs.get("item", {})
        for slot, output in output_items.items():
            item_id = output.id
            ItemDisplayer(
                self.GetSlotControl(panel, "item", slot, outputs=True),
                Item(item_id, output.aux, count=int(output.count)),
                prob=output.prob,
            )
        input_fluids = inputs.get("fluid", {})
        if input_fluids:
            max_input_fluid_volume = max(
                input_fluids.values(), key=lambda x: x.count
            ).count
        for slot, input in input_fluids.items():
            FluidDisplayer(
                self.GetSlotControl(panel, "fluid", slot), input.id, input.count,
                max_input_fluid_volume, not_consumed=input.count == 0,
            )
        output_fluids = outputs.get("fluid", {})
        if output_fluids:
            max_output_fluid_volume = max(
                output_fluids.values(), key=lambda x: x.count
            ).count
        for slot, output in output_fluids.items():
            FluidDisplayer(
                self.GetSlotControl(panel, "fluid", slot, outputs=True),
                output.id,
                output.count,
                max_output_fluid_volume,
                prob=output.prob,
            )

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        for displayer in self.input_displayers:
            displayer.tick(render_ticks)


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
        from ...ui.machinery.utils import SetHoverText

        MachineRecipeRendererBase.RenderInit(self, panel)
        # 机器里有、这条配方不用的流体槽 (同 MEI: 照画成空槽), 悬停写明是空的
        if self.layout is not None:
            for side, values in (("input", self.GetDisplayInputs()), ("output", self.GetDisplayOutputs())):
                for index, (kind, slot) in enumerate(self.layout[side + "s"]):
                    if kind == "fluid" and slot not in values.get("fluid", {}):
                        SetHoverText(self.GetControl(panel, "content/body/%s/%d" % (side, index)), "§7空（这条配方不用）")
            self.has_progress = self.layout["progress"] is not None
            self.has_flame = self.layout["flame"]
            has_power_bar = self.layout["power"] is not None
            has_progress_tip = True
        else:
            used = set(self.GetDisplayInputs().get("fluid", {})) | set(self.GetDisplayOutputs().get("fluid", {}))
            for i in range(8):
                if i not in used and _has(panel, "fluid%d" % i):
                    SetHoverText(self.GetControl(panel, "fluid%d" % i), "§7空（这条配方不用）")
            self.has_progress = _has(panel, "progress")
            self.has_flame = _has(panel, "flame")
            has_power_bar = _has(panel, "power_bar")
            has_progress_tip = _has(panel, "progress_tip")
        self.has_power = has_power_bar and self.PowerTip() is not None
        if has_progress_tip:
            lines = []
            if self.recipe.tick_duration:
                lines.append("§7耗时： §f%s 秒" % _secs(self.recipe.tick_duration))
            lines.extend(self.ProgressTip())
            SetHoverText(self.GetControl(panel, "progress_tip"), "\n".join(lines) or "§7（只表示流向）")
        if self.has_power:
            self.RenderPower(panel, 1.0 if self.recipe.tick_duration <= 1 and self.layout is not None and self.layout["power"] == "gen" else 0.0)
        elif has_power_bar:
            self.UpdatePower(panel, 0.0, "§7（不耗电）")

    def UpdatePower(self, panel, level, hover):
        # type: (UBaseCtrl, float, str) -> None
        ctrl = self.GetControl(panel, "power_bar")
        if self.layout is not None:
            UpdateRecipePower(ctrl, level, self.layout["segments"], hover)
        else:
            from ...ui.machinery.utils import UpdatePowerBar
            UpdatePowerBar(ctrl, level, 1, hover=hover)

    def RenderPower(self, panel, p):
        # type: (UBaseCtrl, float) -> None
        raise NotImplementedError

    def RenderUpdate(self, panel, render_ticks):
        # type: (UBaseCtrl, int) -> None
        from ...ui.machinery.utils import UpdateProgress, UpdateFlame

        MachineRecipeRendererBase.RenderUpdate(self, panel, render_ticks)
        td = self.recipe.tick_duration * 3
        if not self.render_progress or td <= 3:  # 连续过程 (蒸馏 / 蒸发) 只画静态箭头
            if self.has_flame:
                UpdateFlame(self.GetControl(panel, "flame"), 1.0)
            return
        p = (render_ticks * 2.0) % td / td
        if self.has_progress:
            UpdateProgress(self.GetControl(panel, "progress"), p)
        if self.has_flame:
            UpdateFlame(self.GetControl(panel, "flame"), 1 - p)
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
        self.UpdatePower(panel, 1 - p, self.PowerTip())


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
        self.UpdatePower(panel, p, self.PowerTip())


__all__ = [
    "MachineRecipe",
    "MachineRecipeBase",
    "GeneratorRecipe",
]
