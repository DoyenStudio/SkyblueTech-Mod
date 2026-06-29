# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import InventoryItemChangedServerEvent
from skybluetech_scripts.tooldelta.api.server import GetArmorSlotItems, SetPlayerAllItems
from .base import PlayerService

if 0:
    import typing
    from skybluetech_scripts.tooldelta.define import Item

    Callback = typing.Callable[[str], None]
    PowerCost = typing.Union[int, typing.Callable[[Item], int]]

# 10s @ 20tps。夜视等必须周期续期/持续耗电的效果借此驱动。
PERIODIC_INTERVAL = 200

# 惰性缓存 ItemPosType.ARMOR
_armor_pos = None  # type: int | None


def _get_armor_pos():
    # type: () -> int
    global _armor_pos
    if _armor_pos is None:
        from mod.server.extraServerApi import GetMinecraftEnum

        _armor_pos = GetMinecraftEnum().ItemPosType.ARMOR
    return _armor_pos


class _UpgradeHandler(object):
    __slots__ = ("on_activate", "on_deactivate", "on_periodic", "power_cost", "priority")

    def __init__(self, on_activate, on_deactivate, on_periodic, power_cost, priority):
        # type: (Callback | None, Callback | None, Callback | None, PowerCost, int) -> None
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.on_periodic = on_periodic
        self.power_cost = power_cost
        self.priority = priority

    def resolve_cost(self, item):
        # type: (Item) -> int
        if callable(self.power_cost):
            return self.power_cost(item)
        return self.power_cost

    def needs_tick(self):
        # type: () -> bool
        return self.on_periodic is not None or bool(self.power_cost)


class ArmorService(PlayerService):
    """缓存玩家护甲上的升级模块状态,驱动模块的激活/失活、周期效果与耗电。

    升级模块通过 ArmorService.register_upgrade_handler 注册回调(全局,模块导入
    时注册一次)。每个玩家实例维护「当前激活的 (槽位, 模块) 集合」:
      - 激活条件 = 穿戴 ∧ (不耗电 ∨ 所在护甲电量 ≥ 本周期 cost)
      - 护甲变化(InventoryItemChangedServerEvent)-> refresh 重算激活集合(不扣电)
      - 每 10s -> on_tick 重算激活集合 + 对持续模块续期 + 按 priority 顺序从所在护甲扣电
    所有回调签名均为 callback(player_id)。

    # NOTE: 性能优化原则 —— 不要再写「主动/周期性扫描所有玩家」的服务。
    #   穿脱检测一律事件驱动;on_tick 仅在该玩家穿戴了「需周期处理」(有 on_periodic
    #   或 power_cost)的模块时才扫描其 4 个护甲槽(self._tick_needed 门控),
    #   身上没有此类模块的玩家 on_tick 直接返回、零开销。
    #   耗电本身是天然的周期逻辑,是 on_periodic 存在的正当理由;但凡能用
    #   on_activate/on_deactivate(纯事件驱动)表达的效果,就不要用 on_periodic。
    """

    tick_interval = PERIODIC_INTERVAL

    # 全局注册表(类级共享): upgrader_id -> _UpgradeHandler
    _handlers = {}  # type: dict[str, _UpgradeHandler]

    @classmethod
    def register_upgrade_handler(
        cls,
        upgrader_id,  # type: str
        on_activate=None,  # type: Callback | None
        on_deactivate=None,  # type: Callback | None
        on_periodic=None,  # type: Callback | None
        power_cost=0,  # type: PowerCost
        priority=0,  # type: int
    ):
        # type: (...) -> None
        """供升级模块注册护甲激活/失活/周期回调与耗电。

        Args:
            upgrader_id: 升级模块 id(ObjectUpgraders.*)。
            on_activate: 模块由未激活变为激活(穿戴且通电)时 on_activate(player_id)。
            on_deactivate: 模块由激活变为未激活(脱下或断电)时 on_deactivate(player_id)。
            on_periodic: 持续激活期间每 10s on_periodic(player_id)(如续期 buff)。
            power_cost: 每 10s 从所在护甲扣的电;int 或 callable(item)->int;0=不耗电。
            priority: 同一护甲电量不足时,数值大的模块优先供电/扣费。
        """
        cls._handlers[upgrader_id] = _UpgradeHandler(
            on_activate, on_deactivate, on_periodic, power_cost, priority
        )

    def __init__(self, player_id):
        # type: (str) -> None
        PlayerService.__init__(self, player_id)
        # 当前激活的 (slot, upgrader_id)
        self._active = set()  # type: set[tuple[int, str]]
        self._tick_needed = False
        self.refresh()

    def _worn(self, items):
        # type: (dict[int, Item]) -> list[tuple[int, str, _UpgradeHandler]]
        """列出当前穿戴且已注册的模块: [(slot, upgrader_id, handler), ...]。"""
        # 惰性导入: 避免 player 包与 tools.upgraders 包在加载期相互导入成环。
        from ..tools.upgraders.utils import GetUpgraders

        out = []  # type: list[tuple[int, str, _UpgradeHandler]]
        for slot, item in items.items():
            if item is None:
                continue
            for upgrader_id in GetUpgraders(item):
                handler = self._handlers.get(upgrader_id)
                if handler is not None:
                    out.append((slot, upgrader_id, handler))
        return out

    def _plan(self, items, worn):
        # type: (dict[int, Item], list[tuple[int, str, _UpgradeHandler]]) -> tuple[set[tuple[int, str]], dict[int, int]]
        """按激活条件与 priority 计算本周期的激活集合与每槽扣电量。"""
        from ..machinery.utils.charge import GetCharge

        by_slot = {}  # type: dict[int, list[tuple[str, _UpgradeHandler]]]
        for slot, upgrader_id, handler in worn:
            by_slot.setdefault(slot, []).append((upgrader_id, handler))
        desired = set()  # type: set[tuple[int, str]]
        drain = {}  # type: dict[int, int]
        for slot, mods in by_slot.items():
            mods.sort(key=lambda m: -m[1].priority)
            store = GetCharge(items[slot].userData or {})[0]
            for upgrader_id, handler in mods:
                cost = handler.resolve_cost(items[slot])
                if cost > 0:
                    if store < cost:
                        continue  # 电量不足 -> 不激活
                    store -= cost
                    drain[slot] = drain.get(slot, 0) + cost
                desired.add((slot, upgrader_id))
        return desired, drain

    def _apply(self, desired, fire_periodic):
        # type: (set[tuple[int, str]], bool) -> None
        """对激活/失活的模块触发回调;fire_periodic 时对持续激活模块续期。"""
        for slot, upgrader_id in desired - self._active:
            cb = self._handlers[upgrader_id].on_activate
            if cb is not None:
                cb(self.player_id)
        for slot, upgrader_id in self._active - desired:
            cb = self._handlers[upgrader_id].on_deactivate
            if cb is not None:
                cb(self.player_id)
        if fire_periodic:
            for slot, upgrader_id in desired & self._active:
                cb = self._handlers[upgrader_id].on_periodic
                if cb is not None:
                    cb(self.player_id)
        self._active = desired

    def _drain(self, items, drain):
        # type: (dict[int, Item], dict[int, int]) -> None
        """每件护甲合并扣电、统一回写一次。"""
        from ..machinery.utils.charge import GetCharge, UpdateCharge

        armor_pos = _get_armor_pos()
        changed = {}  # type: dict[tuple[int, int], Item]
        for slot, cost in drain.items():
            if cost <= 0:
                continue
            item = items[slot]
            store = GetCharge(item.userData or {})[0]
            UpdateCharge(item, store - cost)
            changed[(armor_pos, slot)] = item
        if changed:
            SetPlayerAllItems(self.player_id, changed)

    def refresh(self):
        # type: () -> None
        """护甲变化时重算激活集合(处理穿/脱),不扣电。"""
        items = GetArmorSlotItems(self.player_id, get_userdata=True)
        worn = self._worn(items)
        self._tick_needed = any(handler.needs_tick() for _, _, handler in worn)
        desired, _ = self._plan(items, worn)
        self._apply(desired, fire_periodic=False)

    def on_tick(self):
        # type: () -> None
        if not self._tick_needed:
            return
        items = GetArmorSlotItems(self.player_id, get_userdata=True)
        worn = self._worn(items)
        desired, drain = self._plan(items, worn)
        self._apply(desired, fire_periodic=True)
        self._drain(items, drain)

    @PlayerService.Listen(InventoryItemChangedServerEvent.WithUserData())
    def on_armor_changed(self, event):
        # type: (InventoryItemChangedServerEvent) -> None
        if event.playerId != self.player_id:
            return
        self.refresh()
