# coding=utf-8
from ...common.define import flags
from ...common.define.id_enum import Machinery, Upgraders
from ...common.events.machinery.fluid_splitter import (
    FluidSplitterSettingsSetFluid,
    FluidSplitterSettingsSetLabel,
    FluidSplitterSimpleAction,
)
from ...common.machinery_def.fluid_splitter import MAX_FLUID_VOLUME
from ...common.machinery_def.splitter_settings import (
    FLUID_SPLITTER_DEFAULT_FLUID,
    FLUID_SPLITTER_SETTINGS_LIMIT,
    K_RECORD_LABELS,
    K_SETTINGS_LIMIT,
    LoadSplitterSettings,
    SaveSplitterSettings,
)
from ..transmitters.fluid_pipe.logic import (
    PushFluidToFluidContainer,
    fluid_pipe_can_transfer_fluid,
)
from ..transmitters.fluid_pipe.logic import (
    logic_module as fluid_pipe_logic,
)
from .basic import (
    GUIControl,
    MultiFluidContainer,
    OperationListener,
    UpgradeControl,
)
from .core import RegisterMachine


@RegisterMachine
class FluidSplitter(OperationListener, UpgradeControl, MultiFluidContainer, GUIControl):
    block_name = Machinery.FLUID_SPLITTER
    fluid_io_fix_mode = -1
    fluid_input_slots = (0,)
    fluid_output_slots = ()
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    upgrade_slot_start = 0
    allow_upgraders = frozenset({
        Upgraders.GENERIC_SPLIT,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidSplitter, self).__init__(dim, x, y, z, block_entity_data)
        self._cached_recorded_settings = None
        self._sending_fluid = True
        self._ticking_t = 0
        self.handler.SubscribeOnTicking(self._fluid_splitter_on_ticking)
        self.handler.SubscribeOnAddedFluid(self._fluid_splitter_on_added_fluid)

    def _fluid_splitter_on_ticking(self):
        if self._sending_fluid and self._ticking_t % 5 == 0:
            sent = self.ready_try_post_fluid()
            all_empty = all(i.volume <= 0 for i in self.fluids.values())
            # 状态灯: 空 = 缺少输入; 有流体但这一轮一点都没送出去 = 输出受阻
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT, all_empty)
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL, not all_empty and not sent)
            if all_empty:
                self._sending_fluid = False
        self._ticking_t += 1

    def _fluid_splitter_on_added_fluid(self, slot, fluid_id, fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self._sending_fluid = True

    def ready_try_post_fluid(self):
        ok = False
        for slot in self.fluid_input_slots:
            fluid = self.fluids[slot]
            fluid_id = fluid.fluid_id
            fluid_volume = fluid.volume
            if fluid_id is None or fluid_volume <= 0:
                fluid.volume = 0.0
                continue
            if fluid_id is not None and fluid_volume > 0:
                rest_volume = self.try_post_fluid_by_label(fluid_id, fluid_volume, slot)
                ok = ok or rest_volume != fluid_volume
            if fluid.volume <= 0:
                fluid.fluid_id = None
        return ok

    def try_post_fluid_by_label(self, fluid_id, fluid_volume, source_slot=None):
        # type: (str, float) -> float
        if fluid_id is None or fluid_volume is None or fluid_volume <= 0:
            return fluid_volume
        matched_label = self.get_label_by_fluid(fluid_id)
        networks = (
            fluid_pipe_logic
            .GetContainerNode(self.dim, self.x, self.y, self.z, enable_cache=True)
            .get_outputs()
            .values()
        )
        from .. import transferlib
        from .core.pool import GetLoadedMachine
        for network in set(networks):
            if not fluid_pipe_can_transfer_fluid(network.transmitter_id, fluid_id):
                continue
            budget = network.transfer_speed
            for ap in network.get_input_access_points():
                ap_label = ap.get_label()
                if ap_label != matched_label or ap.target_pos == self.xyz:
                    continue
                offered = min(fluid_volume, budget)
                api = transferlib.api
                target_machine = GetLoadedMachine(ap.dim, *ap.target_pos)
                if source_slot is not None and api is not None and not isinstance(target_machine, MultiFluidContainer):
                    try:
                        target = transferlib.at_access(api.FLUID, ap)
                        if target is None:
                            continue
                        source = api.create_fluid_handler(
                            {source_slot: self._radium_fluids[source_slot]},
                            lambda i: self.fluids[i].max_volume, input_slots=())
                        with api.open_transaction() as tx:
                            moved = api.move_fluid(source, target, fluid_id, offered, tx)
                            tx.commit()
                    except api.TransactionError:
                        break
                else:
                    _, rest = PushFluidToFluidContainer(ap, fluid_id, offered)
                    moved = offered - rest
                    if source_slot is not None and moved:
                        self.fluids[source_slot].volume -= moved
                fluid_volume -= moved
                budget -= moved
                if fluid_volume <= 0 or budget <= 0:
                    break
            if fluid_volume <= 0:
                break
        return fluid_volume

    def get_label_by_fluid(self, fluid_id):
        # type: (str) -> int
        for label, _fluid_id in self.record_settings:
            if fluid_id == _fluid_id:
                return label
        return 0 if self.HasUpgrader("skybluetech:upgrader_generic_split") else -1

    def on_add_setting(self):
        if len(self.record_settings) >= self.settings_limit:
            return
        self.record_settings.append((0, FLUID_SPLITTER_DEFAULT_FLUID))
        self.save_settings()

    def on_delete_setting(self, index):
        # type: (int) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings.pop(index)
        self.save_settings()

    def on_set_fluid(self, index, fluid):
        # type: (int, str) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings[index] = (self.record_settings[index][0], fluid)
        self.save_settings()

    def on_set_label(self, index, label):
        # type: (int, int) -> None
        if not 0 <= index < len(self.record_settings):
            return
        self.record_settings[index] = (label, self.record_settings[index][1])
        self.save_settings()

    @property
    def settings_limit(self):
        # type: () -> int
        return self.bdata[K_SETTINGS_LIMIT] or FLUID_SPLITTER_SETTINGS_LIMIT

    @settings_limit.setter
    def settings_limit(self, value):
        # type: (int) -> None
        self.bdata[K_SETTINGS_LIMIT] = value

    @property
    def record_settings(self):
        if self._cached_recorded_settings is None:
            self._cached_recorded_settings = LoadSplitterSettings(
                self.bdata[K_RECORD_LABELS], FLUID_SPLITTER_DEFAULT_FLUID
            )
        return self._cached_recorded_settings

    @record_settings.setter
    def record_settings(self, value):
        # type: (list[tuple[int, str]]) -> None
        self._cached_recorded_settings = value
        self.save_settings()

    def save_settings(self):
        self.bdata[K_RECORD_LABELS] = SaveSplitterSettings(self.record_settings)


@FluidSplitter.ForOperation(FluidSplitterSimpleAction)
def onSimpleAction(event, machine):
    # type: (FluidSplitterSimpleAction, FluidSplitter) -> None
    if event.action == event.ACTION_ADD_SETTING:
        machine.on_add_setting()
    elif event.action == event.ACTION_REMOVE_SETTING and isinstance(event.extra, int):
        machine.on_delete_setting(event.extra)


@FluidSplitter.ForOperation(FluidSplitterSettingsSetLabel)
def onSetLabel(event, machine):
    # type: (FluidSplitterSettingsSetLabel, FluidSplitter) -> None
    if not isinstance(event.label, int) or not isinstance(event.setting_index, int):
        return
    machine.on_set_label(event.setting_index, event.label)


@FluidSplitter.ForOperation(FluidSplitterSettingsSetFluid)
def onSetFluid(event, machine):
    # type: (FluidSplitterSettingsSetFluid, FluidSplitter) -> None
    if (
        not isinstance(event.setting_index, int)
        or not isinstance(event.fluid_id, str)
        or len(event.fluid_id) > 256
    ):
        return
    machine.on_set_fluid(event.setting_index, event.fluid_id)
