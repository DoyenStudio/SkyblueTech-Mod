# coding=utf-8
from mod.server.blockEntityData import BlockEntityData
from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent
from ..define.events.machinery.fluid_splitter import (
    FluidSplitterSettingsListUpdate,
    FluidSplitterSettingsSetFluid,
    FluidSplitterSettingsSetLabel,
    FluidSplitterSimpleAction,
)
from skybluetech_scripts.tooldelta.api.timer import ExecLater
from ..define.id_enum.machinery import FLUID_SPLITTER as MACHINE_ID
from ..transmitters.pipe.logic import (
    logic_module as pipe_logic,
    PushFluidToFluidContainer,
)
from ..ui_sync.machinery.fluid_splitter import FluidSplitterUISync, FluidSlotSync
from ..utils.action_commit import SafeGetMachine
from .basic import MultiFluidContainer, GUIControl, UpgradeControl, RegisterMachine

K_RECORD_LABELS = "record_settings"
K_SETTINGS_LIMIT = "settings_limit"

DEFAULT_SETTINGS_LIMIT = 3


@RegisterMachine
class FluidSplitter(GUIControl, MultiFluidContainer, UpgradeControl):
    block_name = MACHINE_ID
    fluid_io_fix_mode = -1
    fluid_input_slots = {0}
    fluid_output_slots = set()
    fluid_slot_max_volumes = (4000,)
    upgrade_slot_start = 0
    allow_upgrader_tags = {"skybluetech:upgraders/generic_split"}

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        UpgradeControl.__init__(self, dim, x, y, z, block_entity_data)
        MultiFluidContainer.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = FluidSplitterUISync.NewServer(self).Activate()
        self.CallSync()
        self._cached_recorded_settings = None

    def OnTicking(self):
        if self._sending_fluid:
            self.RequireAnyFluidFromNetwork()
            ok = self.readyTryPostFluid()
            if not ok:
                self._sending_fluid = False
            self.CallSync()

    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.OnTryActivate()

    def readyTryPostFluid(self):
        ok = False
        for slot in self.fluid_input_slots:
            fluid = self.fluids[slot]
            fluid_id = fluid.fluid_id
            fluid_volume = fluid.volume
            if fluid_id is not None and fluid_volume > 0:
                rest_volume = self.tryPostFluidByLabel(fluid_id, fluid_volume)
                ok = ok or rest_volume != fluid_volume
                fluid.volume = rest_volume
            if fluid.volume <= 0:
                fluid.fluid_id = None
        return ok

    def tryPostFluidByLabel(self, fluid_id, fluid_volume):
        # type: (str, float) -> float
        matched_label = self.getLabelByFluid(fluid_id)
        networks = (
            i
            for i in pipe_logic.GetContainerNode(
                self.dim, self.x, self.y, self.z, enable_cache=True
            ).outputs.values()
            if i is not None
        )
        for network in networks:
            for ap in network.group_inputs:
                ap_label = ap.get_label()
                if ap_label == matched_label:
                    _, fluid_volume = PushFluidToFluidContainer(
                        ap, fluid_id, fluid_volume
                    )
                    if fluid_volume <= 0:
                        break
        return fluid_volume

    def getLabelByFluid(self, fluid_id):
        # type: (str) -> int
        for label, _fluid_id in self.record_settings:
            if fluid_id == _fluid_id:
                return label
        return 0 if self.HasUpgrader("skybluetech:upgrader_generic_split") else -1

    def OnSync(self):
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()

    def OnClick(self, event):
        # type: (ServerBlockUseEvent) -> None
        GUIControl.OnClick(self, event)
        ExecLater(
            0.1,
            lambda: FluidSplitterSettingsListUpdate(self.record_settings).send(
                event.playerId
            ),
        )

    def OnUnload(self):
        # type: () -> None
        UpgradeControl.OnUnload(self)
        GUIControl.OnUnload(self)

    def onAddSetting(self, player_id):
        # type: (str) -> None
        if len(self.record_settings) >= self.settings_limit:
            return
        self.record_settings.append((0, "minecraft:water"))
        self.save_settings()
        FluidSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onDeleteSetting(self, player_id, index):
        # type: (str, int) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings.pop(index)
        self.record_settings = self.record_settings
        FluidSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onSetFluid(self, player_id, index, fluid):
        # type: (str, int, str) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings[index] = (self.record_settings[index][0], fluid)
        self.save_settings()
        FluidSplitterSettingsListUpdate(self.record_settings).send(player_id)

    def onSetLabel(self, player_id, index, label):
        # type: (str, int, int) -> None
        if index >= len(self.record_settings):
            return
        self.record_settings[index] = (label, self.record_settings[index][1])
        self.save_settings()
        FluidSplitterSettingsListUpdate(self.record_settings).send(player_id)

    @property
    def settings_limit(self):
        # type: () -> int
        return self.bdata[K_SETTINGS_LIMIT] or DEFAULT_SETTINGS_LIMIT

    @settings_limit.setter
    def settings_limit(self, value):
        # type: (int) -> None
        self.bdata[K_SETTINGS_LIMIT] = value

    @property
    def record_settings(self):
        if self._cached_recorded_settings is None:
            record_settings = self.bdata[K_RECORD_LABELS] or ["0-minecraft:water"]
            self._cached_recorded_settings = [
                (int(i.split("-")[0]), str(i.split("-")[1])) for i in record_settings
            ]
        return self._cached_recorded_settings

    @record_settings.setter
    def record_settings(self, value):
        # type: (list[tuple[int, str]]) -> None
        self._cached_recorded_settings = value
        self.bdata[K_RECORD_LABELS] = ["%d-%s" % (a, b) for a, b in value]

    def save_settings(self):
        self.bdata[K_RECORD_LABELS] = [
            "%d-%s" % (a, b) for a, b in self.record_settings
        ]


@FluidSplitterSimpleAction.Listen()
def onSimpleAction(event):
    # type: (FluidSplitterSimpleAction) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, FluidSplitter):
        return
    if event.action == event.ACTION_ADD_SETTING:
        m.onAddSetting(event.player_id)
    elif event.action == event.ACTION_REMOVE_SETTING:
        m.onDeleteSetting(event.player_id, event.extra)


@FluidSplitterSettingsSetLabel.Listen()
def onSetLabel(event):
    # type: (FluidSplitterSettingsSetLabel) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, FluidSplitter):
        return
    if not isinstance(event.label, int) or not isinstance(event.setting_index, int):
        return
    m.onSetLabel(event.player_id, event.setting_index, event.label)


@FluidSplitterSettingsSetFluid.Listen()
def onSetFluid(event):
    # type: (FluidSplitterSettingsSetFluid) -> None
    m = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(m, FluidSplitter):
        return
    if (
        not isinstance(event.setting_index, int)
        or not isinstance(event.fluid_id, str)
        or len(event.fluid_id) > 256
    ):
        return
    m.onSetFluid(event.player_id, event.setting_index, event.fluid_id)
