# BatteryMatrixUI.battery_slot_nums
# # coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.client import (
    GetBlockEntityData,
    GetItemHoverName,
)
from skybluetech_scripts.tooldelta.events.client import (
    PlayerTryPutCustomContainerItemClientEvent,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.tooldelta.utils.py_comp import py2_long
from skybluetech_scripts.skybluetech.common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_STRUCTURE_BROKEN,
    DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK,
)
from skybluetech_scripts.skybluetech.common.events.machinery.battery_matrix import (
    BatteryMatrixActionRequest,
    BatteryMatrixCheckCoreBatterysRequest,
    BatteryMatrixPopBatteryRequest,
    BatteryMatrixStoreBatteryRequest,
    BatteryMatrixCoreStatusUpdate,
    BatteryMatrixStatesUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_DESTROY_FLAG,
)
from skybluetech_scripts.skybluetech.common.machinery_def.battery_matrix import (
    K_INPUT_POWER,
    K_OUTPUT_POWER,
    K_STORE_RF,
    K_RF_MAX,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import (
    UpdateGenericProgressL2R,
    FormatRF,
    GetStructureLackedBlocks,
    GetStructureLackedBlockPoses,
    FormatStructureLackedBlockPoses,
)

ENERGY_LABEL_PATH = MAIN_PATH / "battery_icon/energy_label"
TOTAL_POWER_PATH = MAIN_PATH / "total_power"
BATTERY_ICON_PATH = MAIN_PATH / "battery_icon"
STORAGE_WINDOW_PATH = MAIN_PATH / "storage_window"
PUSH_STORAGE_BTN_PATH = STORAGE_WINDOW_PATH / "push_storage_btn"
STORAGE_CLOSE_BTN_PATH = STORAGE_WINDOW_PATH / "close_btn"
OPEN_STORAGE_BTN_PATH = MAIN_PATH / "open_storage_btn"
INPUT_SWITCH_PATH = MAIN_PATH / "input_switch"
OUTPUT_SWITCH_PATH = MAIN_PATH / "output_switch"
INPUT_POWER_LABEL_PATH = MAIN_PATH / "input_power"
OUTPUT_POWER_LABEL_PATH = MAIN_PATH / "output_power"
STRUCTURE_NOT_FINISHED_TIP_PATH = MAIN_PATH / "structure_not_finished_tip"
STRUCTURE_DESC_LABEL_PATH = STRUCTURE_NOT_FINISHED_TIP_PATH / "desc_label"
MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH = MAIN_PATH / "multi_block_structure_check_btn"


@RegistToolDeltaScreen("BatteryMatrixUI.main", is_proxy=True)
class BatteryMatrixUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.energy_label = self.GetElement(ENERGY_LABEL_PATH).asLabel()
        self.total_power = self.GetElement(TOTAL_POWER_PATH).asLabel()
        self.battery_icon = self.GetElement(BATTERY_ICON_PATH)
        self.storage_window = self.GetElement(STORAGE_WINDOW_PATH)
        self.input_switch = self.GetElement(INPUT_SWITCH_PATH).asSwitch()
        self.output_switch = self.GetElement(OUTPUT_SWITCH_PATH).asSwitch()
        self.input_power_label = self.GetElement(INPUT_POWER_LABEL_PATH).asLabel()
        self.output_power_label = self.GetElement(OUTPUT_POWER_LABEL_PATH).asLabel()
        self.structure_not_finished_tip = self.GetElement(
            STRUCTURE_NOT_FINISHED_TIP_PATH
        )
        self.structure_desc_label = self.GetElement(STRUCTURE_DESC_LABEL_PATH).asLabel()
        self.open_storage_btn = (
            self
            .GetElement(OPEN_STORAGE_BTN_PATH)
            .asButton()
            .SetCallback(self.onOpenStorageWindow)
        )
        self.push_storage_btn = (
            self
            .GetElement(PUSH_STORAGE_BTN_PATH)
            .asButton()
            .SetCallback(self.onStoreBatteries)
        )
        self.close_storage_btn = (
            self
            .GetElement(STORAGE_CLOSE_BTN_PATH)
            .asButton()
            .SetCallback(self.onCloseStorageWindow)
        )
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_PATH)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        self.storage_window.SetVisible(False)
        self.last_destroy_flag = None
        self.last_structure_lacked_blocks = None
        self.last_structure_lacked_poses = None
        self.battery_slots_data = []  # type: list[tuple[str, int, int]]

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        input_power = GetValue(data, K_INPUT_POWER, 0)
        output_power = GetValue(data, K_OUTPUT_POWER, 0)
        storage_rf = GetValue(data, K_STORE_RF, 0.0)
        rf_max = GetValue(data, K_RF_MAX, 1) or 1
        destroy_flag = GetValue(data, K_DESTROY_FLAG, 0)
        structure_lacked_blocks = GetStructureLackedBlocks(data)
        structure_lacked_poses = GetStructureLackedBlockPoses(data)
        self.input_power_label.SetText("输入 %s/t" % FormatRF(input_power))
        self.output_power_label.SetText("输出 %s/t" % FormatRF(output_power))
        self.energy_label.SetText("{:.1f}%%".format(float(storage_rf * 100) / rf_max))
        if rf_max != 1.0:
            self.total_power.SetText("%s / %s" % (FormatRF(storage_rf), FormatRF(rf_max)))
        else:
            self.total_power.SetText("请打开仓储界面放入电池")
        UpdateGenericProgressL2R(self.battery_icon, float(storage_rf) / rf_max)
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

    def onOpenStorageWindow(self, _):
        _, x, y, z = self.pos
        BatteryMatrixCheckCoreBatterysRequest(x, y, z).send()

    def onCloseStorageWindow(self, _):
        self.storage_window.SetVisible(False)

    def onStoreBatteries(self, _):
        _, x, y, z = self.pos
        BatteryMatrixStoreBatteryRequest(x, y, z).send()

    def onCheckMultiBlockStructure(self, _):
        _, x, y, z = self.pos
        MultiBlockStructureCheckRequest(x, y, z).send()

    @MachinePanelUIProxy.Listen(BatteryMatrixStatesUpdate)
    def onStateUpdate(self, event):
        # type: (BatteryMatrixStatesUpdate) -> None
        self.input_switch.SetState(event.enable_input)
        self.output_switch.SetState(event.enable_output)

    @MachinePanelUIProxy.Listen(BatteryMatrixCoreStatusUpdate)
    def onRecvUpdate(self, event):
        # type: (BatteryMatrixCoreStatusUpdate) -> None
        self.battery_slots_data = event.battery_datas
        if event.first:
            self.storage_window.SetVisible(True)

    @MachinePanelUIProxy.Listen(PlayerTryPutCustomContainerItemClientEvent)
    def onPutItemIn(self, event):
        # type: (PlayerTryPutCustomContainerItemClientEvent) -> None
        _, x, y, z = self.pos
        if event.x == x and event.y == y and event.z == z:
            if not self.storage_window.GetVisible():
                event.cancel()

    @Binder.binding(Binder.BF_ToggleChanged, "#BatteryMatrixUI.input_switch")
    def onInputSwitchChanged(self, args):
        _, x, y, z = self.pos
        BatteryMatrixActionRequest(
            x, y, z, BatteryMatrixActionRequest.OPERATION_INPUT, args["state"]
        ).send()

    @Binder.binding(Binder.BF_ToggleChanged, "#BatteryMatrixUI.output_switch")
    def onOutputSwitchChanged(self, args):
        _, x, y, z = self.pos
        BatteryMatrixActionRequest(
            x, y, z, BatteryMatrixActionRequest.OPERATION_OUTPUT, args["state"]
        ).send()

    @Binder.binding_collection(
        Binder.BF_BindInt, "battery_slots_grid", "#BatteryMatrixUI.battery_slot_nums"
    )
    def onGetSlotsCount(self, args):
        return len(self.battery_slots_data)

    @Binder.binding_collection(
        Binder.BF_BindFloat,
        "battery_slots_grid",
        "#BatteryMatrixUI.energy_bar_mask_clip",
    )
    def onGetClip(self, index):
        # type: (int) -> float
        if index >= len(self.battery_slots_data):
            return 0.5
        else:
            _, store_rf, store_rf_max = self.battery_slots_data[index]
            return 1 - (float(store_rf) / store_rf_max)

    @Binder.binding_collection(
        Binder.BF_BindInt,
        "battery_slots_grid",
        "#BatteryMatrixUI.battery_slot_item_id_aux",
    )
    def onGetItemIdAux(self, index):
        # type: (int) -> int
        if index >= len(self.battery_slots_data):
            return 0
        else:
            item_id = self.battery_slots_data[index][0]
            return Item(item_id).GetBasicInfo().id_aux

    @Binder.binding(Binder.BF_ButtonClickUp, "#BatteryMatrixUI.slot_btn")
    def onClickSlotBtn(self, args):
        _, x, y, z = self.pos
        idx = args["#collection_index"]
        BatteryMatrixPopBatteryRequest(x, y, z, idx).send()
