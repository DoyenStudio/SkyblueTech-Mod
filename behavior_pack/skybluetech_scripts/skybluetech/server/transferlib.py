# coding=utf-8
"""Optional Radium component; item transport requires version 1.2."""
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID, GetLevelComponent
from skybluetech_scripts.tooldelta.events.server import OnSimTickServerEvent
from ..common.define.facing import FACING_EN, OPPOSITE_FACING
from ..common.machinery_def.basic.multi_fluid_container import FLUID_VOLUME_EPSILON
from .machinery.core.pool import GetLoadedMachine, cached_machines
from .machinery.core.registry import registered_machines

api = None
_probe_ticks = 0
_refresh_pending = False


def loaded(machine):
    return GetLoadedMachine(machine.dim, *machine.xyz) is machine


def invalidate():
    if api is not None:
        api.invalidate()


def prepare(machine):
    if api is None:
        return
    from .machinery.basic.multi_fluid_container import MultiFluidContainer
    from .machinery.creative_power_acceptor import CreativePowerAcceptor
    from .machinery.battery_matrix_core import BatteryMatrixCore
    if isinstance(machine, MultiFluidContainer):
        machine._radium_fluids = dict(
            (slot, fluid_cell(machine, slot, tank)) for slot, tank in machine.fluids.items()
        )
    if isinstance(machine, BatteryMatrixCore):
        prepare_batteries(machine)
    elif isinstance(machine, CreativePowerAcceptor):
        machine._radium_void = api.create_voiding_energy(machine.AddPower, lambda: loaded(machine))
    elif not machine.is_non_energy_machine:
        machine._radium_rf = api.create_cell(
            0, read=lambda: int(machine.store_rf), apply=machine.StageTransferPower,
            persist=machine.PersistTransferPower, valid=lambda: loaded(machine))


def prepare_batteries(core):
    if api is None:
        return
    for slot in core.slots:
        if hasattr(slot, "_radium_cell"):
            continue
        slot._radium_cell = api.create_cell(
            0, read=lambda s=slot: s.store_rf,
            apply=lambda amount, s=slot: setattr(s, "store_rf", amount),
            persist=core.save_core_data, owner=core,
            valid=lambda s=slot: loaded(core) and s in core.slots)


def fluid_cell(machine, index, tank):
    def read():
        return tank.fluid_id, tank.volume

    def apply(state):
        # The host treats this residual as empty when reloading the block entity.
        if 0 < state[1] <= FLUID_VOLUME_EPSILON:
            raise api.TransactionError("Fluid remainder is below the tank storage threshold")
        tank._cached_fluid_id, tank._cached_volume = state

    def persist():
        tank.bdata[tank.k_id] = tank.fluid_id
        tank.bdata[tank.k_vol] = 1.0 if tank.volume == float("inf") else tank.volume

    def changed(changes):
        for _, (old_id, old), (new_id, new) in changes:
            if old_id and (old_id != new_id or new < old):
                machine._on_reduced_fluid(index, old_id, old if old_id != new_id else old-new, True)
            if new_id and (new_id != old_id or new > old):
                machine._on_added_fluid(index, new_id, new if new_id != old_id else new-old, True)

    return api.create_cell(read(), read=read, apply=apply, persist=persist,
                           changed=changed, valid=lambda: loaded(machine))


class CreativeTankPort(object):
    """An empty creative tank voids pipe input. Only manual filling configures it."""
    def __init__(self, handler):
        self.handler = handler

    def __getattr__(self, name):
        return getattr(self.handler, name)

    def insert(self, fluid_id, amount, tx, slot=None):
        import math
        from skybluetech_scripts.tooldelta.utils.py_comp import py2_long
        if isinstance(amount, bool) or not isinstance(amount, (int, py2_long, float)):
            raise TypeError("invalid fluid amount")
        amount = float(amount)
        if amount < 0 or math.isnan(amount) or math.isinf(amount):
            raise ValueError("invalid fluid amount")
        if tx.manager is not self.manager:
            raise api.TransactionError("foreign transaction")
        tx.guard(self.handler.valid)
        if slot not in (None, 0) or not self.is_valid(0, fluid_id):
            return 0.0
        if self.get_resource(0, tx) is not None:
            return 0.0
        tx.guard(lambda: self.is_valid(0, fluid_id))
        return amount


def fluid_port(dim, pos, face):
    machine = GetLoadedMachine(dim, *pos)
    cells = getattr(machine, "_radium_fluids", None)
    if face is None or not cells:
        return None

    def slots():
        relative = None
        if machine.fluid_input_slots_by_face is not None or machine.fluid_output_slots_by_face is not None:
            relative = machine.GetRelativeFacing(FACING_EN[face])
        modes = machine.fluid_io_mode
        # Machines declaring only slot lists inherit the all-disabled base tuple.
        mode = -1 if modes == (2,) * 6 and hasattr(machine, "fluid_io_fix_mode") else modes[face]
        return (machine.GetFluidInputSlotsForFace(relative) if mode in (-1, 0) else (),
                machine.GetFluidOutputSlotsForFace(relative) if mode in (-1, 1) else ())

    inputs, outputs = slots()
    visible = set(inputs) | set(outputs)
    if not visible:
        return None
    handler = api.create_fluid_handler(
        dict((i, cells[i]) for i in visible), lambda i: machine.fluids[i].max_volume,
        input_slots=inputs, output_slots=outputs,
        accepts=lambda i, r: plain(r) and machine.IsValidFluidInput(i, r),
        valid=lambda: loaded(machine) and slots() == (inputs, outputs))
    from .machinery.tanks.tank_creative import CreativeTank
    return CreativeTankPort(handler) if isinstance(machine, CreativeTank) else handler


def plain(resource):
    return resource is not None and not api.get_fluid_properties(resource)


def battery_port(machine):
    from .machinery.battery_matrix_core import BatteryMatrixCore
    core = machine.TryGetLoadedMachine(BatteryMatrixCore)
    if not core or not core.slots or machine.GetStructureDestroyFlag():
        return None
    slots = tuple(core.slots)

    def valid():
        return (loaded(machine) and loaded(core) and not machine.GetStructureDestroyFlag()
                and machine.TryGetLoadedMachine(BatteryMatrixCore) is core and tuple(core.slots) == slots)

    def incoming(amount):
        machine._last_input += amount
        machine.CallSync()

    def outgoing(amount):
        machine._last_output += amount

    handlers = [api.create_energy_handler(
        (s._radium_cell,), lambda _, slot=s: slot.store_rf_max,
        can_insert=lambda: machine.enable_input,
        can_extract=lambda: machine.enable_output and machine.IsActive(),
        max_insert=s.input_power, max_extract=s.output_power,
        on_insert=incoming, on_extract=outgoing, owner=machine) for s in slots]
    return api.combine_energy(handlers, valid=valid)


def ordinary_energy(machine):
    cell = getattr(machine, "_radium_rf", None)
    if cell is None:
        return None

    def inserted(amount):
        from .machinery.basic import GUIControl, PowerControl
        from .machinery.assembler import Assembler
        from ..common.define import flags
        if isinstance(machine, PowerControl):
            machine.PowerEnough()
        if isinstance(machine, Assembler) and machine.store_rf and machine.HasDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK):
            machine.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        if isinstance(machine, GUIControl):
            machine.CallSync()
        if hasattr(machine, "_input_sum"):
            machine._input_sum += amount

    def extracted(amount):
        if hasattr(machine, "_output_sum"):
            machine._output_sum += amount

    return api.create_energy_handler(
        (cell,), lambda _: machine.store_rf_max,
        can_insert=lambda: getattr(machine, "enable_input", True),
        can_extract=lambda: getattr(machine, "enable_output", True),
        max_insert=lambda: machine.GetEnergyTransferLimits(5)[0],
        max_extract=lambda: machine.GetEnergyTransferLimits(5)[1],
        valid=lambda: loaded(machine), on_insert=inserted, on_extract=extracted, owner=machine)


def energy_port(dim, pos, face):
    from .machinery.battery_matrix import BatteryMatrix
    from .machinery.interfaces import EnergyInputInterface, EnergyOutputInterface
    from .machinery.rf_repeater_plant.core import RFRepeaterPlant, MODE_OUTPUT
    port = GetLoadedMachine(dim, *pos)
    if face is None or port is None or port.energy_io_mode[face] not in (0, 1):
        return None
    redirected = isinstance(port, (EnergyInputInterface, EnergyOutputInterface))
    machine = port.getMachineRef() if redirected else port
    if machine is None or not loaded(machine):
        return None
    if isinstance(machine, BatteryMatrix):
        handler = battery_port(machine)
    elif isinstance(machine, RFRepeaterPlant) and port.energy_io_mode[face] == 0:
        def destinations():
            return tuple(GetLoadedMachine(dim, *p) for p, mode in machine.nodes_in_network.items()
                         if mode == MODE_OUTPUT and isinstance(GetLoadedMachine(dim, *p), RFRepeaterPlant))
        targets = destinations()
        handlers = [api.create_energy_handler((m._radium_rf,), lambda _, m=m: m.store_rf_max,
                    can_extract=False, valid=lambda m=m: loaded(m),
                    on_insert=lambda amount, m=m: m.CallSync(), owner=m) for m in targets]
        handler = api.combine_energy(handlers, valid=lambda: destinations() == targets) if handlers else None
    elif hasattr(machine, "_radium_void"):
        handler = machine._radium_void
    else:
        handler = ordinary_energy(machine)
    if handler is None:
        return None
    mode = port.energy_io_mode[face]
    return api.energy_view(handler, can_insert=mode == 0, can_extract=mode == 1,
                           valid=lambda: loaded(port) and loaded(machine) and port.energy_io_mode[face] == mode
                           and (not redirected or port.getMachineRef() is machine))


def supports_items():
    version = getattr(api, "API_VERSION", ())
    return bool(version and version[0] == 1 and tuple(version) >= (1, 2, 0))


def query(capability, dim, pos, face):
    if capability == "radium:item" and not supports_items():
        return None
    if api is not None and pos is not None:
        return api.query(capability, dim, pos, face)


def at_access(capability, ap):
    return query(capability, ap.dim, ap.target_pos, OPPOSITE_FACING[ap.access_facing])


def has_port(capability, dim, pos, face=None):
    if api is None or dim is None or pos is None:
        return False
    faces = range(6) if face is None else (face,)
    try:
        return any(query(capability, dim, pos, f) is not None for f in faces)
    except api.TransactionError:
        return False


@OnSimTickServerEvent.Listen()
def discover(_):
    global api, _probe_ticks, _refresh_pending
    if api is not None:
        if _refresh_pending:
            _refresh_pending = False
            refresh_networks()
        return
    _probe_ticks += 1
    if _probe_ticks % 20 != 1:
        return
    candidate = GetLevelComponent("radium", "transfer")
    version = getattr(candidate, "API_VERSION", ())
    if tuple(version[:2]) < (1, 1) or version[0] != 1:
        return
    try:
        with candidate.open_transaction():
            pass
    except candidate.TransactionError:
        return
    from .machinery.basic.multi_fluid_container import MultiFluidContainer
    api = candidate
    for machine in list(cached_machines.values()):
        prepare(machine)
    blocks = CF.CreateBlockInfo(LEVEL_ID)
    for name, cls in registered_machines.items():
        tags = blocks.GetBlockTags(name) or ()
        if not cls.is_non_energy_machine and ("redstoneflux_accepter" in tags or "redstoneflux_provider" in tags):
            register_port(api.ENERGY, name, energy_port)
        if issubclass(cls, MultiFluidContainer) and "skybluetech_fluid_container" in tags:
            register_port(api.FLUID, name, fluid_port)
    # Other packs may register their providers later in this same tick.
    _refresh_pending = True


def register_port(capability, name, provider):
    try:
        api.register_provider(capability, name, provider)
    except ValueError as exc:
        # Another integration already owns this capability. Continue with other blocks.
        print("[skybluetech] Radium registration skipped for %s (%s): %s" % (name, capability, exc))


def refresh_networks():
    from .transmitters.wire.logic import logic_module as wires
    from .transmitters.fluid_pipe.logic import logic_module as pipes
    for logic, capability in ((wires, api.ENERGY), (pipes, api.FLUID)):
        logic.refresh_transfer_ports(capability)
    if supports_items():
        from .transmitters.item_pipe.logic import logic_module as items
        items.refresh_transfer_ports(api.ITEM)
