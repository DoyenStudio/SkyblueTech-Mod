# coding=utf-8
from .core.pool import GetLoadedMachine
from .interfaces import (
    FluidInputInterface, FluidOutputInterface,
    ItemInputInterface, ItemOutputInterface,
)

class MultiblockProcessingPorts(object):
    """接口库存独立保存；仅在库存事件或重新绑定时搬运。"""

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
        for port_id, machines in self._ios.items():
            for machine in machines:
                if machine.getMachineRef() is not self:
                    continue
                if isinstance(machine, (ItemInputInterface, ItemOutputInterface)):
                    machine.SetOnSlotUpdateCallback(None)
                elif isinstance(machine, (FluidInputInterface, FluidOutputInterface)):
                    machine.SetOnFluidSlotUpdateCallback(None)
                machine.UnsetMachineRef()
        self._ios = {}

    def _refresh_io_bindings(self):
        if not self.StructureFinished():
            if self._ios:
                self._disconnect_ios()
            return
        wanted = {}
        for port_id, cls in self.ports:
            wanted[port_id] = []
            for machine in self.GetAllMachines(cls, port_id):
                owner = machine.getMachineRef()
                if owner is not None and owner is not self:
                    if GetLoadedMachine(owner.dim, *owner.xyz) is owner:
                        continue
                wanted[port_id].append(machine)
        if wanted == self._ios:
            return
        self._disconnect_ios()
        self._ios = wanted
        for machines in wanted.values():
            for machine in machines:
                machine.SetMachineRef(self)
                if isinstance(machine, (ItemInputInterface, ItemOutputInterface)):
                    machine.SetOnSlotUpdateCallback(self._on_material_item_update)
                elif isinstance(machine, (FluidInputInterface, FluidOutputInterface)):
                    machine.SetOnFluidSlotUpdateCallback(self._on_port_fluid_update)
        self.transmit_materials()

    def _live_ports(self, port_id):
        return [machine for machine in self._ios.get(port_id, ())
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
            for port_id, slot in self.fluid_inputs_by_port:
                for machine in self._live_ports(port_id):
                    source = machine.fluids[0]
                    if self.IsValidFluidInput(slot, source.fluid_id):
                        self._move_fluid(machine, 0, self, slot)
            for port_id, slot in self.fluid_outputs_by_port:
                for machine in self._live_ports(port_id):
                    self._move_fluid(self, slot, machine, 0)
        finally:
            self._io_busy = False

    def _take_items(self):
        for machine in self._live_ports(self.item_input_port):
            for slot in machine.item_input_slots:
                item = machine.GetSlotItem(slot)
                if item is None or not self.IsValidInput(0, item):
                    continue
                before = item.count
                rest = self.PushItem(item)
                if rest is None or rest.count < before:
                    machine.SetSlotItem(slot, rest)

    def _send_items(self):
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

    @staticmethod
    def _move_fluid(source_machine, source_slot, target_machine, target_slot):
        source = source_machine.fluids[source_slot]
        target = target_machine.fluids[target_slot]
        fluid_id = source.fluid_id
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
