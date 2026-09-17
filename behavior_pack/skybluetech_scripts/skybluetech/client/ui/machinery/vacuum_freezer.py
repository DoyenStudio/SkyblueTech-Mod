# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
)
from skybluetech_scripts.skybluetech.common.events.machinery.vacuum_freezer import (
    VacuumFreezerSubmitModifiesEvent,
)
from skybluetech_scripts.skybluetech.common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_DESTROY_FLAG,
    K_HEAT_VALUE,
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.vacuum_freezer import (
    ALL_RECIPES,
    K_EXPECTED_KELVIN,
    K_MAX_POWER,
    K_RECIPE,
    MAX_EXPECTED_KELVIN,
    MAX_FLUID_VOLUMES,
    STORE_RF_MAX,
    all_recipes,
    clamp_expected_kelvin,
    clamp_power,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen, UBaseCtrl
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import (
    FluidDisplayer,
    FormatStructureLackedBlockPoses,
    GetStructureLackedBlockPoses,
    GetStructureLackedBlocks,
    UpdateGenericProgressL2R,
    UpdatePowerBar,
)

POWER_BAR_PATH = MAIN_PATH / "power_bar"
PROGRESS_PATH = MAIN_PATH / "progress1"
INPUT_FLUID_PATH = MAIN_PATH / "input_fluid_disp"
OUTPUT_FLUID_PATH = MAIN_PATH / "output_fluid_disp"
DATABOARD_LABEL_PATH = MAIN_PATH / "databoard/label"
KELVIN_INPUT_PATH = MAIN_PATH / "databoard/input_kelvin"
POWER_INPUT_PATH = MAIN_PATH / "databoard/input_power"
STRUCTURE_NOT_FINISHED_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"
STRUCTURE_DESC_LABEL_PATH = STRUCTURE_NOT_FINISHED_TIP_PATH / "desc_label"
MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH = MAIN_PATH / "multi_block_structure_check_btn"
RECIPE_CHECK_BTN_PATH = MAIN_PATH / "recipe_check_btn"

# 与 VacuumFreezerUI.json 里两个编辑框的 $text_box_name 保持一致
KELVIN_BOX_NAME = "#vacuum_freezer.kelvin"
POWER_BOX_NAME = "#vacuum_freezer.power"


def FormatKelvinInput(kelvin):
    # type: (float) -> str
    "把温度格式化成输入框里的文本: 整数不带小数点, 小数最多两位。"
    return ("%.2f" % kelvin).rstrip("0").rstrip(".")


@RegistToolDeltaScreen("VacuumFreezerUI.main", is_proxy=True)
class VacuumFreezerUI(MachinePanelUIProxy):
    def OnCreate(self):
        _, x, y, z = self.pos
        self.power_bar = self.GetElement(POWER_BAR_PATH)
        self.progress = self.GetElement(PROGRESS_PATH)
        self.databoard_label = self.GetElement(DATABOARD_LABEL_PATH).asLabel()
        self.kelvin_input = self.GetElement(KELVIN_INPUT_PATH).asTextEditBox()
        self.power_input = self.GetElement(POWER_INPUT_PATH).asTextEditBox()
        self.input_fluid_displayer = FluidDisplayer(
            self.GetElement(INPUT_FLUID_PATH)
        )
        self.output_fluid_displayer = FluidDisplayer(
            self.GetElement(OUTPUT_FLUID_PATH)
        )
        self.structure_not_finished_tip = self.GetElement(
            STRUCTURE_NOT_FINISHED_TIP_PATH
        )
        self.structure_desc_label = self.GetElement(STRUCTURE_DESC_LABEL_PATH).asLabel()
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        # 打开本机的配方页, 与 MaceratorUI 等机器一致; 用的是全量配方组, 需要升级卡的
        # 配方也列出来(配方页上会标"需要机器升级")
        AsRecipeCheckerBtn(
            self.GetElement(RECIPE_CHECK_BTN_PATH).asButton(),
            all_recipes,
        )
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None
        # 服务端当前的设定值, 玩家只改动其中一个输入框时用于补全另一个
        self.server_power = 0.0
        self.server_kelvin = MAX_EXPECTED_KELVIN
        block_nbt = GetBlockEntityData(x, y, z)
        if block_nbt is None:
            return
        ex_data = block_nbt.get("exData")
        if ex_data is None:
            return
        # 功率为 0 / 温度等于上限(环境温度)说明玩家从没设过, 让输入框保持空白
        max_power = GetValue(ex_data, K_MAX_POWER, 0) or 0
        self.power_input.SetText(str(int(max_power)) if max_power else "")
        kelvin = (
            GetValue(ex_data, K_EXPECTED_KELVIN, MAX_EXPECTED_KELVIN)
            or MAX_EXPECTED_KELVIN
        )
        if kelvin == MAX_EXPECTED_KELVIN:
            self.kelvin_input.SetText("")
        else:
            self.kelvin_input.SetText(FormatKelvinInput(kelvin))

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        destroy_flag = GetValue(data, K_DESTROY_FLAG, 0)
        structure_lacked_blocks = GetStructureLackedBlocks(data)
        structure_lacked_poses = GetStructureLackedBlockPoses(data)
        current_kelvin = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT) or Thermal.ENV_HEAT
        )
        expected_kelvin = (
            GetValue(data, K_EXPECTED_KELVIN, MAX_EXPECTED_KELVIN)
            or MAX_EXPECTED_KELVIN
        )
        max_power = GetValue(data, K_MAX_POWER, 0) or 0
        progress = GetValue(data, K_PROGRESS, 0.0) or 0.0
        # 配方效率 = 当前温度下正在跑的那条配方的推进速率(离最适温度有多近), 与机器端
        # ProcessOnce 同一公式。要按服务端同步来的下标取: 温度窗口是配方自带的, 不同配方
        # 差得很远(液空 80K / 冰 265K), 取错配方这个读数就是错的; 没有配方在跑时显示 0。
        recipe_index = GetValue(data, K_RECIPE, -1)
        recipe = (
            ALL_RECIPES[recipe_index]
            if 0 <= recipe_index < len(ALL_RECIPES)
            else None
        )
        efficiency = (
            recipe.GetRateAtKelvin(current_kelvin) if recipe is not None else 0.0
        )
        self.server_power = max_power
        self.server_kelvin = expected_kelvin
        input_fluid = FluidSlotClient(data, 0)
        output_fluid = FluidSlotClient(data, 1)
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.input_fluid_displayer.update(
            input_fluid.fluid_id, input_fluid.volume, MAX_FLUID_VOLUMES[0]
        )
        self.output_fluid_displayer.update(
            output_fluid.fluid_id, output_fluid.volume, MAX_FLUID_VOLUMES[1]
        )
        self.databoard_label.SetText(
            "当前温度： %.1fK\n设定温度： %sK\n额定功率： %d RF/t\n配方效率： %.1f%%%%"
            % (
                current_kelvin,
                FormatKelvinInput(expected_kelvin),
                int(max_power),
                efficiency * 100.0,
            )
        )
        if (
            destroy_flag != self.last_destroy_flag
            or structure_lacked_blocks != self.last_structure_lacked_blocks
            or structure_lacked_poses != self.last_structure_lacked_poses
        ):
            self.structure_not_finished_tip.SetVisible(destroy_flag != 0)
            self.last_destroy_flag = destroy_flag
            self.last_structure_lacked_blocks = dict(structure_lacked_blocks)
            self.last_structure_lacked_poses = structure_lacked_poses
            if (
                destroy_flag == DEACTIVE_FLAG_STRUCTURE_BROKEN
                and structure_lacked_poses
            ):
                self.structure_desc_label.SetText(
                    FormatStructureLackedBlockPoses(structure_lacked_poses)
                )
            elif (
                destroy_flag == DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK
                and structure_lacked_blocks
            ):
                self.structure_desc_label.SetText(
                    "缺失组件： "
                    + "， ".join(
                        GetItemHoverName(b) + "x" + str(n)
                        for b, n in structure_lacked_blocks.items()
                    )
                )
            else:
                self.structure_desc_label.SetText("多方块结构未完成")

    def onCheckMultiBlockStructure(self, _):
        _, x, y, z = self.pos
        MultiBlockStructureCheckRequest(x, y, z).send()

    def onSubmit(self):
        # type: () -> None
        # 与服务端共用同一套夹取规则; 服务端收到后仍会再校验一次
        power = clamp_power(self._get_box_value(self.power_input, self.server_power))
        kelvin = clamp_expected_kelvin(
            self._get_box_value(self.kelvin_input, self.server_kelvin)
        )
        if power is None or kelvin is None:
            return
        _, x, y, z = self.pos
        VacuumFreezerSubmitModifiesEvent(x, y, z, power, kelvin).send()

    @Binder.binding(Binder.BF_EditFinished, POWER_BOX_NAME)
    def onPowerEdited(self, params):
        # type: (dict) -> None
        text = params["Text"]
        if text == "":
            return
        try:
            value = clamp_power(float(text))
        except ValueError:
            self.power_input.SetText("")
            return
        if value is None:
            self.power_input.SetText("")
            return
        # 夹紧到本机能力范围: 功率不能为负, 也不能超过储电上限支持的值
        self.power_input.SetText(str(value))
        self.onSubmit()

    @Binder.binding(Binder.BF_EditFinished, KELVIN_BOX_NAME)
    def onKelvinEdited(self, params):
        # type: (dict) -> None
        text = params["Text"]
        if text == "":
            return
        try:
            value = clamp_expected_kelvin(float(text))
        except ValueError:
            self.kelvin_input.SetText("")
            return
        if value is None:
            self.kelvin_input.SetText("")
            return
        # 夹紧到本机能力范围: 低于 MIN_EXPECTED_KELVIN 到不了, 高于环境温度没意义
        self.kelvin_input.SetText(FormatKelvinInput(value))
        self.onSubmit()

    def _get_box_value(self, box, fallback):
        # type: (UBaseCtrl, float) -> float
        text = box.asTextEditBox().GetText()
        if text is None or text.strip() == "":
            return fallback
        try:
            return float(text)
        except ValueError:
            return fallback
