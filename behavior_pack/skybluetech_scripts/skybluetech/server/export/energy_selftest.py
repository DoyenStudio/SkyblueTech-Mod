# coding=utf-8
"""仅在游戏服务端显式调用 run()，不导入正式路径，不访问世界方块。"""


def run():
    from . import energy
    from ..machinery.basic.base_machine import BaseMachine

    class Machine(BaseMachine):
        dim, xyz = 0, (0, 0, 0)
        energy_io_mode = (0, 1, 2, 2, 2, 2)
        _power_output_faces = (1,)

        def __init__(self, value, capacity):
            self.value, self.capacity = value, capacity
            self.refunds = []

        @property
        def store_rf(self):
            return self.value

        @property
        def store_rf_max(self):
            return self.capacity

        def GetEnergyTransferLimits(self, period_ticks):
            incoming, outgoing = BaseMachine.GetEnergyTransferLimits(self, period_ticks)
            return min(incoming, 10 * period_ticks), min(outgoing, 10 * period_ticks)

        def AddPower(self, amount):
            accepted = min(amount, self.capacity - self.value)
            self.value += accepted
            return accepted > 0, amount - accepted

        def TakeoutPower(self, amount):
            taken = min(amount, self.value)
            self.value -= taken
            return taken

        def GivebackPower(self, amount):
            self.refunds.append(amount)
            self.value += amount

    class Handler(energy._MachineHandler):
        def valid(self):
            return True

    for invalid in (True, False, -1, 1.5, 100.0, "100"):
        try:
            energy.TransferEnergy(None, None, invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("noninteger energy request was accepted")
    results = []
    for initial, stored, cap, period, expected in (
            (100, 93, 100, 5, 7), (100, 100, 100, 5, 0),
            (0, 0, 100, 5, 0), (100, 0, 1000, 5, 50),
            (100, 0, 1000, 1, 10), (100.0, 93.0, 100, 5, 7),
            (100.75, 93.5, 100, 5, 6)):
        source, target = Machine(initial, 1000), Machine(stored, cap)
        moved = energy.TransferEnergy(Handler(source, 1, period), Handler(target, 0, period), 60)
        assert moved == expected
        assert source.value + target.value == initial + stored
        results.append(moved)
    machine = Machine(100, 1000)
    assert energy.SameEnergyStorage(Handler(machine, 1), Handler(machine, 0))
    assert energy.TransferEnergy(Handler(machine, 1), Handler(machine, 0), 40) == 0
    assert machine.value == 100
    source = Handler(machine, 1)
    ticket = source.prepareExtract(40)
    try:
        assert source.prepareExtract(10) is None
        ticket.finish(13)
        ticket.finish(13)
        assert machine.value == 87 and machine.refunds == [27]
        assert source.isActiveOutput()
        assert not Handler(machine, 2).canExtract()
        assert not Handler(machine, 2).canReceive()
    finally:
        energy._busy.discard(id(machine))
    token = energy.RegisterEnergyProvider("energy_test:provider", ("energy_test:block",), lambda pos, dim, face: None)
    try:
        assert energy.IsExternalEnergyBlock("energy_test:block")
        class PullReceiver(object):
            def acceptsActivePush(self):
                return False
        assert not energy._ExternalHandler(PullReceiver(), token).acceptsActivePush()
    finally:
        assert energy.UnregisterEnergyProvider(token)
    assert not energy.IsExternalEnergyBlock("energy_test:block")
    _check_network_transport(energy, Machine, Handler)
    return {"ok": True, "cases": len(results) + 3, "transferred": results}



def _check_network_transport(energy, machine_cls, handler_cls):
    """两个不同坐标的端口属于同一储能时，真实运输循环必须跳过自我回送。"""
    from ..transmitters.wire.logic import onNetworkTick

    class Access(object):
        access_facing = 1

        def __init__(self, pos):
            self.target_pos = pos

    class Network(object):
        dim, transfer_speed, power_through_sum, run_ticks = 0, 60, 0, 0
        power_through_avg = 0

        def get_input_access_points(self):
            return [Access((0, 0, 1)), Access((1, 0, 0))]

        def get_output_access_points(self):
            return [Access((0, 0, 0))]

        def trigger_shock(self, amount):
            self.transferred = amount

    source, target = machine_cls(100, 1000), machine_cls(0, 1000)
    handlers = {(0, 0, 0): handler_cls(source, 1),
                (0, 0, 1): handler_cls(source, 0),
                (1, 0, 0): handler_cls(target, 0)}
    original = energy.GetEnergyHandler
    try:
        energy.GetEnergyHandler = lambda position, dimension, face: handlers[position]
        network = Network()
        onNetworkTick(network)
        assert source.value == 50 and target.value == 50
        assert network.transferred == 50
    finally:
        energy.GetEnergyHandler = original
