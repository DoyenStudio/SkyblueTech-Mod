# coding=utf-8
from math import isinf, isnan

from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.define import UICtrlPosData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.tooldelta.utils.nbt import ValueOf
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
    K_DESTROY_FLAG,
    K_HEAT_VALUE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    K_FLUID_CAPACITY,
    K_FLUID_PORT_COUNT,
    K_FLUID_VOLUMES,
    MAX_DISPLAY_TEMPERATURE,
    MIN_DISPLAY_TEMPERATURE,
    recipes,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import AsRecipeCheckerBtn
from skybluetech_scripts.skybluetech.client.ui.machinery.define import (
    MAIN_PATH,
    MachinePanelUIProxy,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import (
    FluidDisplayer,
    FormatBlockName,
    FormatFluidVolume,
    FormatKelvin,
    FormatStructureLackedBlockPoses,
    GetStructureLackedBlockPoses,
    GetStructureLackedBlocks,
)

INPUT_FLUID_PATH = MAIN_PATH / "input_fluid_disp"
OUTPUT_FLUID_PATH = MAIN_PATH / "output_fluid_disp"
DATA_LABEL_PATH = MAIN_PATH / "databoard/data_label"
TEMPERATURE_LABEL_PATH = MAIN_PATH / "temperature/temperature_label"
TEMPERATURE_CLIP_PATH = MAIN_PATH / "temperature/bar/clip_panel"
STRUCTURE_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"


def _read_fluid_volumes(data, index=None):
    # type: (dict, int | None) -> dict[str, float]
    suffix = "" if index is None else str(index)
    values = ValueOf(data.get(K_FLUID_VOLUMES + suffix))
    if not isinstance(values, dict):
        return {}
    volumes = {}
    for fluid_id, value in values.items():
        try:
            volume = float(ValueOf(value))
        except (TypeError, ValueError, OverflowError):
            continue
        if volume > 0.0 and not isnan(volume) and not isinf(volume):
            volumes[fluid_id] = volume
    return volumes


class PondFluidDisplayer(FluidDisplayer):
    def __init__(self, ctrl):
        self.port_count = 0
        self.fluid_volumes = {}
        super(PondFluidDisplayer, self).__init__(ctrl)

    def update_summary(self, data, index):
        # type: (dict, int) -> None
        self.port_count = GetValue(data, K_FLUID_PORT_COUNT + str(index), 0)
        self.fluid_volumes = _read_fluid_volumes(data, index)
        pool_volumes = _read_fluid_volumes(data)
        capacity = GetValue(data, K_FLUID_CAPACITY, 0.0)
        fluid = FluidSlotClient(data, index)
        # 选种仍按本侧快照；液面统一用同种液体的全池储量 / 全池总容积。
        self.update(fluid.fluid_id, pool_volumes.get(fluid.fluid_id, 0.0), capacity)

    def _get_target_relative_volume(self):
        if self.max_volume is None or self.max_volume <= 0.0:
            return 0.0
        return super(PondFluidDisplayer, self)._get_target_relative_volume()

    def _update_hover(self):
        databoard = self.ctrl._root._vars.get("disp_board")
        databoard_src = self.ctrl._root._vars.get("disp_board_src")
        if databoard is None or databoard_src is not self.ctrl:
            return
        item_comp = CF.CreateItem(LEVEL_ID)
        display_name = (
            item_comp.GetItemHoverName(self.fluid_id) or self.fluid_id
            if self.fluid_id is not None
            else u"空"
        )
        if isinstance(display_name, bytes):
            display_name = display_name.decode("utf-8")
        lines = [
            u"§d本侧接口数： §f%d" % self.port_count,
            u"§6卤水池总容积： §f%s" % FormatFluidVolume(self.max_volume or 0.0),
            u"§b液面液体： §f%s" % display_name,
            u"§b同种全池储量： §f%s" % FormatFluidVolume(self.fluid_volume or 0.0),
            u"§a本侧各类液量：",
        ]
        for fluid_id in sorted(self.fluid_volumes):
            fluid_name = item_comp.GetItemHoverName(fluid_id) or fluid_id
            if isinstance(fluid_name, bytes):
                fluid_name = fluid_name.decode("utf-8")
            lines.append(
                u"§f%s： %s"
                % (fluid_name, FormatFluidVolume(self.fluid_volumes[fluid_id]))
            )
        if not self.fluid_volumes:
            lines.append(u"§f空")
        lines.append(u"§7液面 = 同种全池储量 / 卤水池总容积")
        (databoard / "image/label").asLabel().SetText(u"\n".join(lines))


@RegistToolDeltaScreen("BrineEvaporationPondUI.main", is_proxy=True)
class BrineEvaporationPondUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.input_fluid_displayer = PondFluidDisplayer(self.GetElement(INPUT_FLUID_PATH))
        self.output_fluid_displayer = PondFluidDisplayer(self.GetElement(OUTPUT_FLUID_PATH))
        self.data_label = self.GetElement(DATA_LABEL_PATH).asLabel()
        self.temperature_label = self.GetElement(TEMPERATURE_LABEL_PATH).asLabel()
        self.temperature_clip = self.GetElement(TEMPERATURE_CLIP_PATH)
        self.temperature_clip["mask"].asImage().SetSpriteClipRatio(
            "fromTopToBottom", 0.0
        )
        self.temperature_clip.SetFullSize(
            "y", UICtrlPosData("parent", relative_value=0.0)
        )
        self.last_temperature_ratio = 0.0
        self.structure_tip = self.GetElement(STRUCTURE_TIP_PATH)
        self.structure_desc_label = self.GetElement(
            STRUCTURE_TIP_PATH / "desc_label"
        ).asLabel()
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def _update_fluid_summary(self, data):
        # 控制器同步多口只读汇总；各接口中的实际库存保持独立。
        self.input_fluid_displayer.update_summary(data, 0)
        self.output_fluid_displayer.update_summary(data, 1)
        input_volumes = self.input_fluid_displayer.fluid_volumes
        output_volumes = self.output_fluid_displayer.fluid_volumes
        self.data_label.SetText(
            "输入(%d口)\n%s\n%d种液体\n输出(%d口)\n%s\n%d种液体"
            % (
                self.input_fluid_displayer.port_count,
                FormatFluidVolume(sum(input_volumes.values())),
                len(input_volumes),
                self.output_fluid_displayer.port_count,
                FormatFluidVolume(sum(output_volumes.values())),
                len(output_volumes),
            )
        )

    def OnTicking(self):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block_data is None:
            return
        data = block_data.get("exData")
        if data is None:
            return
        self._update_fluid_summary(data)

        current_temperature = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT)
        )
        self.temperature_label.SetText(FormatKelvin(current_temperature))
        temperature_ratio = max(
            0.0,
            min(
                1.0,
                (current_temperature - MIN_DISPLAY_TEMPERATURE)
                / (MAX_DISPLAY_TEMPERATURE - MIN_DISPLAY_TEMPERATURE),
            ),
        )
        if temperature_ratio != self.last_temperature_ratio:
            # 外框高 80px、内条高 78px; 同步缩放 2px 边距, 最低温度时裁切高度为 0。
            self.temperature_clip.SetFullSize(
                "y", UICtrlPosData(
                    "parent",
                    relative_value=temperature_ratio,
                    absolute_value=-2.0 * temperature_ratio,
                )
            )
            self.last_temperature_ratio = temperature_ratio

        destroy_flag = GetValue(data, K_DESTROY_FLAG, DEACTIVE_FLAG_STRUCTURE_BROKEN)
        lacked_blocks = GetStructureLackedBlocks(data)
        lacked_poses = GetStructureLackedBlockPoses(data)
        if (
            destroy_flag == self.last_destroy_flag
            and lacked_blocks == self.last_structure_lacked_blocks
            and lacked_poses == self.last_structure_lacked_poses
        ):
            return
        self.last_destroy_flag = destroy_flag
        self.last_structure_lacked_blocks = dict(lacked_blocks)
        self.last_structure_lacked_poses = lacked_poses
        self.structure_tip.SetVisible(destroy_flag != 0)
        if destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN and lacked_poses:
            text = FormatStructureLackedBlockPoses(lacked_poses)
        elif destroy_flag == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK and lacked_blocks:
            text = "缺失组件： " + "， ".join(
                "%sx%d" % (FormatBlockName(block_id), count)
                for block_id, count in sorted(lacked_blocks.items())
            )
        else:
            text = "多方块结构未完成"
        self.structure_desc_label.SetText(text)
