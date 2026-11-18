# coding=utf-8
from .multiblock_port_bindings import MultiblockPortBindings
from ..core.pool import GetLoadedMachine
from ..interfaces import (
    FluidInputInterface, FluidOutputInterface,
    ItemInputInterface, ItemOutputInterface,
)


class MultiblockProcessingPorts(MultiblockPortBindings):
    """接口库存独立保存；仅在库存事件或重新绑定时搬运。"""

    # 独占模式只操作仍属本机的已加载接口；冷却仓沿用成型时取得的接口列表。
    exclusive_ports = True

    def _init_ios(self, refresh_on_sync=True):
        self._ios = {}
        self._io_busy = False
        self._io_refresh_ticks = 0
        self.handler.SubscribeOnSlotUpdate(self._on_material_item_update)
        self.handler.SubscribeOnFluidSlotUpdate(self._on_material_fluid_update)
        self.handler.SubscribeOnStructureChanged(self._on_structure_changed)
        self.handler.SubscribeOnUnload(self._disconnect_ios)
        if refresh_on_sync:
            self.handler.SubscribeOnSync(self._refresh_io_bindings)
        self._refresh_io_bindings()

    def _on_structure_changed(self, ok):
        self._disconnect_ios()
        if ok:
            self._refresh_io_bindings()
        self.CallSync()

    def _disconnect_ios(self):
        self._unbind_ports(only_owned=self.exclusive_ports)
        self._ios = {}

    def _release_port(self, machine):
        if self.exclusive_ports:
            if isinstance(machine, (ItemInputInterface, ItemOutputInterface)):
                machine.SetOnSlotUpdateCallback(None)
            elif isinstance(machine, (FluidInputInterface, FluidOutputInterface)):
                machine.SetOnFluidSlotUpdateCallback(None)
        machine.UnsetMachineRef()

    def _refresh_io_bindings(self):
        if not self.StructureFinished():
            if self._ios:
                self._disconnect_ios()
            return
        wanted = {port_id: self._find_io_ports(cls, port_id) for port_id, cls in self.ports}
        if wanted == self._ios:
            return
        self._disconnect_ios()
        self._ios = wanted
        self._bind_ports(machine for port_id, _ in self.ports for machine in wanted[port_id])
        self.transmit_materials()

    def _find_io_ports(self, cls, port_id):
        candidates = self.GetAllMachines(cls, port_id)
        if not self.exclusive_ports:
            return candidates
        machines = []
        for machine in candidates:
            owner = machine.getMachineRef()
            if owner is not None and owner is not self and GetLoadedMachine(owner.dim, *owner.xyz) is owner:
                continue
            machines.append(machine)
        return machines

    def _bind_port(self, machine):
        machine.SetMachineRef(self)
        if isinstance(machine, (ItemInputInterface, ItemOutputInterface)):
            machine.SetOnSlotUpdateCallback(self._on_material_item_update)
        elif isinstance(machine, (FluidInputInterface, FluidOutputInterface)):
            machine.SetOnFluidSlotUpdateCallback(self._on_port_fluid_update)

    def _live_ports(self, port_id):
        ports = self._ios.get(port_id, ())
        if not self.exclusive_ports:
            return ports
        return [machine for machine in ports
                if machine.getMachineRef() is self
                and GetLoadedMachine(machine.dim, *machine.xyz) is machine]

    def _on_material_item_update(self, slot):
        self.transmit_materials()

    def _on_material_fluid_update(self, slot, is_final):
        if is_final:
            self.transmit_materials()

    def _on_port_fluid_update(self):
        self.transmit_materials()

    def transmit_materials(self):
        if self._io_busy or self._applying_recipe or not self.StructureFinished():
            return
        self._io_busy = True
        try:
            self._take_items()
            self._send_items()
            self._transfer_fluids()
        finally:
            self._io_busy = False

    def _transfer_fluids(self):
        for port_id, slot in self.fluid_inputs_by_port:
            for machine in self._live_ports(port_id):
                self._move_fluid(machine, 0, self, slot)
        for port_id, slot in self.fluid_outputs_by_port:
            for machine in self._live_ports(port_id):
                self._move_fluid(self, slot, machine, 0)

    def _take_items(self):
        for machine in self._live_ports(self.item_input_port):
            for slot in machine.item_input_slots:
                item = machine.GetSlotItem(slot)
                if item is None:
                    continue
                before = item.count
                rest = self._push_port_item(item)
                if rest is None or rest.count < before:
                    machine.SetSlotItem(slot, rest)

    def _push_port_item(self, item):
        return self.PushItem(item) if self.IsValidInput(0, item) else item

    def _send_items(self):
        if not self._ios.get(self.item_output_port):
            return
        item = self.GetSlotItem(1)
        if item is None:
            return
        before = item.count
        for machine in self._live_ports(self.item_output_port):
            item = machine.OutputItem(item)
            if item is None:
                break
        if item is None or item.count < before:
            self.SetSlotItem(1, item)

    def _move_fluid(self, source_machine, source_slot, target_machine, target_slot):
        source = source_machine.fluids[source_slot]
        target = target_machine.fluids[target_slot]
        fluid_id = source.fluid_id
        if target_machine is self and not self.IsValidFluidInput(target_slot, fluid_id):
            return
        if not target.canMerge(fluid_id):
            return
        amount = min(source.volume, target.max_volume - target.volume)
        if amount <= 0:
            return
        # 两端先写完再通知；同步流体回调不能观察到只有一端完成的转移。
        target.fluid_id = fluid_id
        target.volume += amount
        source.volume -= amount
        source_machine._on_reduced_fluid(source_slot, fluid_id, amount, True)
        target_machine._on_added_fluid(target_slot, fluid_id, amount, True)
