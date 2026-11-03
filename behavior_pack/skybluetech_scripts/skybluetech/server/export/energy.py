# coding=utf-8
"""服务端通用 RF 端点。外部提供者不需要注册为本包机器。"""
from skybluetech_scripts.tooldelta.utils.py_comp import py2_long, py2_unicode

API_VERSION = 1
CAPABILITIES = frozenset(("energy_endpoints", "extraction_settlement", "storage_identity"))
_providers = {}
_busy = set()
_disabled = set()


def _quantity(value):
    if isinstance(value, bool) or not isinstance(value, (int, py2_long)) or not 0 <= value <= 9223372036854775807:
        raise ValueError("energy amount must be a nonnegative integer")
    return value


def _native_quantity(value):
    # 存量原生 NBT 可能把整数保存为 float；不接受带小数的电量。
    if isinstance(value, float) and 0 <= value <= 9223372036854775807 and value == int(value):
        value = int(value)
    return _quantity(value)


def IsReady():
    from ...common.export.events import IsServerLoaded
    return IsServerLoaded()


def RegisterEnergyProvider(owner, block_ids, resolver):
    """resolver(position, dimension, face) 返回 RF 处理器或 None；owner 唯一。"""
    if not isinstance(owner, (str, py2_unicode)) or ":" not in owner or not callable(resolver):
        raise ValueError("invalid energy provider")
    blocks = frozenset(block_ids)
    if not blocks or any(not isinstance(name, (str, py2_unicode)) or ":" not in name for name in blocks):
        raise ValueError("invalid energy block identifiers")
    if owner in _providers:
        raise ValueError("energy provider already registered")
    if any(blocks.intersection(entry[0]) for entry in _providers.values()):
        raise ValueError("energy blocks already registered")
    token = object()
    _providers[owner] = (blocks, resolver, token)
    return token


def UnregisterEnergyProvider(token):
    for owner, entry in tuple(_providers.items()):
        if entry[2] is token:
            _disabled.discard(token)
            del _providers[owner]
            return True
    return False


def IsExternalEnergyBlock(block_name):
    return any(block_name in entry[0] for entry in _providers.values())


def GetEnergyHandler(position, dimension, face, native_only=False, period_ticks=5):
    """查询已加载端点；face 是目标被接触的面，不加载机器或区块。"""
    if (isinstance(face, bool) or not isinstance(face, (int, py2_long)) or face not in range(6)
            or isinstance(dimension, bool) or not isinstance(dimension, (int, py2_long))
            or not isinstance(position, (tuple, list)) or len(position) != 3
            or any(isinstance(n, bool) or not isinstance(n, (int, py2_long)) for n in position)):
        raise ValueError("invalid energy endpoint location")
    if (not isinstance(period_ticks, (int, py2_long)) or isinstance(period_ticks, bool)
            or period_ticks not in (1, 5)):
        raise ValueError("period_ticks must be 1 or 5")
    from ..machinery.core.pool import GetLoadedMachine
    machine = GetLoadedMachine(dimension, *position)
    if machine is not None and not machine.is_non_energy_machine:
        return _MachineHandler(machine, face, period_ticks)
    if native_only or not _providers:
        return None
    from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
    if not CF.CreateChunkSource(LEVEL_ID).CheckChunkState(dimension, tuple(position)):
        return None
    name = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(tuple(position), dimension) or {}).get("name")
    for blocks, resolver, token in tuple(_providers.values()):
        if name in blocks and token not in _disabled:
            try:
                handler = resolver(tuple(position), dimension, face)
                return _ExternalHandler(handler, token) if handler is not None else None
            except Exception as error:
                _disabled.add(token)
                print("[skybluetech] energy provider resolver disabled: %s" % error)
                return None
    return None


class _ExternalHandler(object):
    def __init__(self, handler, token):
        self.handler, self.token = handler, token

    def _call(self, method, *args):
        try:
            return getattr(self.handler, method)(*args)
        except Exception as error:
            _disabled.add(self.token)
            print("[skybluetech] energy provider disabled: %s" % error)
            raise

    def _available(self):
        return self.token not in _disabled and any(entry[2] is self.token for entry in _providers.values())

    def canReceive(self):
        return self._available() and self._call("canReceive")

    def canExtract(self):
        return self._available() and self._call("canExtract")

    def storageIdentity(self):
        return self._call("storageIdentity") if hasattr(self.handler, "storageIdentity") else None

    def acceptsActivePush(self):
        return (self._call("acceptsActivePush") if hasattr(self.handler, "acceptsActivePush") else True)

    def insert(self, amount):
        _quantity(amount)
        if not self.canReceive():
            return 0
        try:
            accepted = _quantity(self._call("insert", amount))
            if accepted > amount:
                raise RuntimeError("energy receiver exceeded offer")
            return accepted
        except Exception:
            _disabled.add(self.token)
            raise

    def prepareExtract(self, amount):
        _quantity(amount)
        if not self.canExtract():
            return None
        return self._call("prepareExtract", amount)


class _MachineHandler(object):
    def __init__(self, machine, face, period_ticks=5):
        self.machine, self.face, self.period_ticks = machine, face, period_ticks

    def valid(self):
        from ..machinery.core.pool import GetLoadedMachine
        machine = self.machine
        return GetLoadedMachine(machine.dim, *machine.xyz) is machine

    def canReceive(self):
        return self.valid() and self.machine.energy_io_mode[self.face] == 0

    def canExtract(self):
        return self.valid() and self.machine.energy_io_mode[self.face] == 1

    def storageIdentity(self):
        machine = self.machine
        backing = machine.getMachineRef() if hasattr(machine, "getMachineRef") else machine
        return ("skybluetech:energy", id(backing)) if self.valid() and backing is not None else None

    def acceptsActivePush(self):
        return True

    def isActiveOutput(self):
        return self.canExtract() and self.face in getattr(self.machine, "_power_output_faces", ())

    def insert(self, amount):
        _quantity(amount)
        if not amount or not self.canReceive():
            return 0
        limit = self.machine.GetEnergyTransferLimits(self.period_ticks)[0]
        offered = min(amount, limit) if limit is not None else amount
        remaining = _native_quantity(self.machine.AddPower(int(offered))[1])
        if remaining > offered:
            raise RuntimeError("energy receiver returned excessive remainder")
        return offered - remaining

    def prepareExtract(self, amount):
        _quantity(amount)
        if not amount or not self.canExtract():
            return None
        machine = self.machine
        limit = machine.GetEnergyTransferLimits(self.period_ticks)[1]
        amount = min(amount, limit) if limit is not None else amount
        # 多方块端口可能转发到同一个控制器；禁止重入其 Takeout/Giveback 调用对。
        backing = machine.getMachineRef() if hasattr(machine, "getMachineRef") else machine
        if backing is None or id(backing) in _busy:
            return None
        _busy.add(id(backing))
        try:
            taken = _native_quantity(machine.TakeoutPower(int(amount)))
            if taken > amount:
                raise RuntimeError("energy source exceeded request")
            if not taken:
                machine.GivebackPower(0)
                _busy.discard(id(backing))
                return None
            return _Extraction(self, backing, taken)
        except Exception:
            _busy.discard(id(backing))
            raise


class _Extraction(object):
    def __init__(self, handler, backing, amount):
        self.handler, self.backing, self.amount = handler, backing, amount
        self.accepted = None

    def finish(self, accepted):
        _quantity(accepted)
        if accepted > self.amount:
            raise ValueError("settlement exceeds extraction")
        if self.accepted is not None:
            if self.accepted != accepted:
                raise RuntimeError("extraction already settled")
            return True
        self.accepted = accepted
        try:
            machine = self.handler.machine
            backing = machine.getMachineRef() if hasattr(machine, "getMachineRef") else machine
            if not self.handler.valid() or backing is not self.backing:
                raise RuntimeError("energy source changed during transfer")
            machine.GivebackPower(int(self.amount - accepted))
        finally:
            _busy.discard(id(self.backing))
        return True


def SameEnergyStorage(source, target):
    """同局共享储能去重；未知标识不推断为相同。"""
    if source is target:
        return True
    left = source.storageIdentity() if hasattr(source, "storageIdentity") else None
    right = target.storageIdentity() if hasattr(target, "storageIdentity") else None
    return left is not None and right is not None and left == right


def TransferEnergy(source, target, amount):
    """同一调用链内抽取、接收、按实际量退回；结果不明时不退款。"""
    _quantity(amount)
    if source is None or target is None or not amount or not source.canExtract() or not target.canReceive():
        return 0
    if SameEnergyStorage(source, target):
        return 0
    ticket = source.prepareExtract(amount)
    if ticket is None:
        return 0
    try:
        accepted = _quantity(target.insert(ticket.amount))
        if accepted > ticket.amount:
            raise RuntimeError("energy receiver exceeded offer")
    except Exception:
        ticket.finish(ticket.amount)
        raise
    ticket.finish(accepted)
    return accepted


def RefreshEnergyConnections(position, dimension):
    """仅用于端点生命周期或面配置变化；保留玩家手动断开的连接。"""
    from .transmitters import RefreshPowerConnections
    RefreshPowerConnections(dimension, *position)


__all__ = [
    "API_VERSION", "CAPABILITIES", "IsReady", "RegisterEnergyProvider",
    "UnregisterEnergyProvider", "GetEnergyHandler", "IsExternalEnergyBlock",
    "TransferEnergy", "RefreshEnergyConnections", "SameEnergyStorage",
]
