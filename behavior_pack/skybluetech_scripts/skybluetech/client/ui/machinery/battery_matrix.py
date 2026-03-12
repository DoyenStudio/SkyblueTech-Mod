# BatteryMatrixUI.battery_slot_nums
# # coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.events.client import (
    PlayerTryPutCustomContainerItemClientEvent,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from ....common.ui_sync.machinery.battery_matrix import BatteryMatrixUISync
from ....common.events.misc.multi_block_structure_check import (
    MultiBlockStructureCheckRequest,
)
from ....common.events.machinery.battery_matrix import (
    BatteryMatrixActionRequest,
    BatteryMatrixCheckCoreBatterysRequest,
    BatteryMatrixPopBatteryRequest,
    BatteryMatrixStoreBatteryRequest,
    BatteryMatrixCoreStatusUpdate,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdateGenericProgressL2R, FormatRF

ENERGY_LABEL_NODE = MAIN_PATH / "battery_icon/energy_label"
TOTAL_POWER_NODE = MAIN_PATH / "total_power"
BATTERY_ICON_NODE = MAIN_PATH / "battery_icon"
STORAGE_WINDOW_NODE = MAIN_PATH / "storage_window"
PUSH_STORAGE_BTN_NODE = STORAGE_WINDOW_NODE / "push_storage_btn"
STORAGE_CLOSE_BTN_NODE = STORAGE_WINDOW_NODE / "close_btn"
OPEN_STORAGE_BTN_NODE = MAIN_PATH / "open_storage_btn"
INPUT_SWITCH_NODE = MAIN_PATH / "input_switch"
OUTPUT_SWITCH_NODE = MAIN_PATH / "output_switch"
INPUT_POWER_LABEL_NODE = MAIN_PATH / "input_power"
OUTPUT_POWER_LABEL_NODE = MAIN_PATH / "output_power"
STRUCTURE_NOT_FINISHED_TIP_NODE = MAIN_PATH / "structure_not_finished_tip"
MULTIBLOCK_STRUCTURE_CHECK_BTN_NODE = MAIN_PATH / "multi_block_structure_check_btn"


@RegistToolDeltaScreen("BatteryMatrixUI.main", is_proxy=True)
class BatteryMatrixUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.energy_label = self.GetElement(ENERGY_LABEL_NODE).asLabel()
        self.total_power = self.GetElement(TOTAL_POWER_NODE).asLabel()
        self.battery_icon = self.GetElement(BATTERY_ICON_NODE)
        self.storage_window = self.GetElement(STORAGE_WINDOW_NODE)
        self.input_switch = self.GetElement(INPUT_SWITCH_NODE).asSwitch()
        self.output_switch = self.GetElement(OUTPUT_SWITCH_NODE).asSwitch()
        self.input_power_label = self.GetElement(INPUT_POWER_LABEL_NODE).asLabel()
        self.output_power_label = self.GetElement(OUTPUT_POWER_LABEL_NODE).asLabel()
        self.structure_not_finished_tip = self.GetElement(
            STRUCTURE_NOT_FINISHED_TIP_NODE
        )
        self.open_storage_btn = (
            self
            .GetElement(OPEN_STORAGE_BTN_NODE)
            .asButton()
            .SetCallback(self.onOpenStorageWindow)
        )
        self.push_storage_btn = (
            self
            .GetElement(PUSH_STORAGE_BTN_NODE)
            .asButton()
            .SetCallback(self.onStoreBatteries)
        )
        self.close_storage_btn = (
            self
            .GetElement(STORAGE_CLOSE_BTN_NODE)
            .asButton()
            .SetCallback(self.onCloseStorageWindow)
        )
        self.multiblock_structute_check_btn = (
            self
            .GetElement(MULTIBLOCK_STRUCTURE_CHECK_BTN_NODE)
            .asButton()
            .SetCallback(self.onCheckMultiBlockStructure)
        )
        self.storage_window.SetVisible(False)
        self._last_structure_flag = None
        self.battery_slots_data = []  # type: list[tuple[str, int, int]]
        dim, x, y, z = self.pos
        self.sync = BatteryMatrixUISync.NewClient(dim, x, y, z)  # type: BatteryMatrixUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.input_switch.SetState(self.sync.enable_input)
        self.output_switch.SetState(self.sync.enable_output)
        self.input_power_label.SetText("输入 %s/t" % FormatRF(self.sync.input_power))
        self.output_power_label.SetText("输出 %s/t" % FormatRF(self.sync.output_power))
        self.energy_label.SetText(
            "{:.1f}%%".format(
                float(self.sync.storage_rf * 100) / (self.sync.rf_max or 1)
            )
        )
        self.total_power.SetText(
            "%s / %s"
            % (FormatRF(self.sync.storage_rf), FormatRF(self.sync.rf_max or 1))
        )
        UpdateGenericProgressL2R(
            self.battery_icon, float(self.sync.storage_rf) / (self.sync.rf_max or 1)
        )
        if self.sync.structure_flag != self._last_structure_flag:
            self.structure_not_finished_tip.SetVisible(self.sync.structure_flag != 0)
            self._last_structure_flag = self.sync.structure_flag

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

    @MachinePanelUIProxy.Listen(BatteryMatrixCoreStatusUpdate)
    def onRecvUpdate(self, event):
        # type: (BatteryMatrixCoreStatusUpdate) -> None
        self.battery_slots_data = event.battery_datas
        print("Okay.")
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
            return 0.5
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
