# coding=utf-8
if 0 > 1:
    import typing

    from skybluetech_scripts.tooldelta.events import (
        PlayerTryPutCustomContainerItemServerEvent,
    )
    from skybluetech_scripts.tooldelta.events.server import ServerBlockUseEvent
    from skybluetech_scripts.tooldelta.events.server.block import (
        BlockNeighborChangedServerEvent,
        BlockRandomTickServerEvent,
        BlockStrengthChangedServerEvent,
        ServerEntityTryPlaceBlockEvent,
        ServerPlaceBlockEntityEvent,
    )


class MachineEventDispatcher(object):
    "单台机器的事件订阅与分发器。"

    def __init__(self):
        self.handlers = {}  # type: dict[str, list[typing.Callable]]

    # GENERAL

    def Subscribe(self, topic_name, handler):
        # type: (str, typing.Callable) -> None
        self.handlers.setdefault(topic_name, []).append(handler)

    def Unsubscribe(self, topic_name, handler):
        # type: (str, typing.Callable) -> None
        handlers = self.handlers.get(topic_name, [])
        if handler in handlers:
            handlers.remove(handler)

    def CallHandlers(self, topic_name, *args, **kwargs):
        for hdl in self.handlers.get(topic_name, []):
            hdl(*args, **kwargs)

    # SPECIAL
    def SubscribeOnPlaced(self, handler):
        # type: (typing.Callable[[ServerPlaceBlockEntityEvent], None]) -> None
        self.Subscribe(HandlerEnum.ON_PLACED, handler)

    def CallOnPlacedHandlers(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        self.CallHandlers(HandlerEnum.ON_PLACED, event)

    def SubscribeOnTicking(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_TICKING, handler)

    def CallOnTickingHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_TICKING)

    def SubscribeOnBlockRedstoneStrengthChanged(self, handler):
        # type: (typing.Callable[[BlockStrengthChangedServerEvent], None]) -> None
        self.Subscribe(HandlerEnum.ON_BLOCK_REDSTONE_STRENGTH_CHANGED, handler)

    def CallOnBlockRedstoneStrengthChangedHandlers(self, event):
        # type: (BlockStrengthChangedServerEvent) -> None
        self.CallHandlers(HandlerEnum.ON_BLOCK_REDSTONE_STRENGTH_CHANGED, event)

    def SubscribeOnUnload(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_UNLOAD, handler)

    def CallOnUnloadHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_UNLOAD)

    def SubscribeOnDestroy(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_DESTROY, handler)

    def CallOnDestroyHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_DESTROY)

    def SubscribeOnNeighborChanged(self, handler):
        # type: (typing.Callable[[BlockNeighborChangedServerEvent], None]) -> None
        self.Subscribe(HandlerEnum.ON_NEIGHBOR_CHANGED, handler)

    def CallOnNeighborChangedHandlers(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        self.CallHandlers(HandlerEnum.ON_NEIGHBOR_CHANGED, event)

    def SubscribeOnBlockRandomTick(self, handler):
        # type: (typing.Callable[[BlockRandomTickServerEvent], None]) -> None
        self.Subscribe(HandlerEnum.ON_BLOCK_RANDOM_TICK, handler)

    def CallOnBlockRandomTickHandlers(self, event):
        # type: (BlockRandomTickServerEvent) -> None
        self.CallHandlers(HandlerEnum.ON_BLOCK_RANDOM_TICK, event)

    def SubscribeOnDeactiveFlagsChanged(self, handler):
        # type: (typing.Callable[[bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_DEACTIVE_FLAGS_CHANGED, handler)

    def CallOnDeactiveFlagsChangedHandlers(self, flush=True):
        # type: (bool) -> None
        self.CallHandlers(HandlerEnum.ON_DEACTIVE_FLAGS_CHANGED, flush)

    def SubscribeOnInvalidateCaches(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_INVALIDATE_CACHES, handler)

    def CallOnInvalidateCachesHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_INVALIDATE_CACHES)

    def SubscribeOnClick(self, handler):
        # type: (typing.Callable[[ServerBlockUseEvent, typing.Optional[dict]], None]) -> None
        self.Subscribe(HandlerEnum.ON_CLICK, handler)

    def CallOnClickHandlers(self, event, extra_datas=None):
        # type: (ServerBlockUseEvent, typing.Optional[dict]) -> None
        self.CallHandlers(HandlerEnum.ON_CLICK, event, extra_datas)

    def SubscribeOnSync(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_SYNC, handler)

    def CallOnSyncHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_SYNC)

    def SubscribeOnSlotUpdate(self, handler):
        # type: (typing.Callable[[int], None]) -> None
        self.Subscribe(HandlerEnum.ON_SLOT_UPDATE, handler)

    def CallOnSlotUpdateHandlers(self, slot_pos):
        # type: (int) -> None
        self.CallHandlers(HandlerEnum.ON_SLOT_UPDATE, slot_pos)

    def SubscribeOnCustomCotainerPutItem(self, handler):
        # type: (typing.Callable[[PlayerTryPutCustomContainerItemServerEvent], None]) -> None
        self.Subscribe(HandlerEnum.ON_CUSTOM_COTAINER_PUT_ITEM, handler)

    def CallOnCustomCotainerPutItemHandlers(self, event):
        # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
        self.CallHandlers(HandlerEnum.ON_CUSTOM_COTAINER_PUT_ITEM, event)

    def SubscribeOnFluidSlotUpdate(self, handler):
        # type: (typing.Callable[[int, bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_FLUID_SLOT_UPDATE, handler)

    def CallOnFluidSlotUpdateHandlers(self, slot_pos, is_final):
        # type: (int, bool) -> None
        self.CallHandlers(HandlerEnum.ON_FLUID_SLOT_UPDATE, slot_pos, is_final)

    def SubscribeOnAddedFluid(self, handler):
        # type: (typing.Callable[[int, str, float, bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_ADDED_FLUID, handler)

    def CallOnAddedFluidHandlers(self, slot, fluid_id, added_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.CallHandlers(
            HandlerEnum.ON_ADDED_FLUID, slot, fluid_id, added_fluid_volume, is_final
        )

    def SubscribeOnReducedFluid(self, handler):
        # type: (typing.Callable[[int, str, float, bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_REDUCED_FLUID, handler)

    def CallOnReducedFluidHandlers(self, slot, fluid_id, reduced_fluid_volume, is_final):
        # type: (int, str, float, bool) -> None
        self.CallHandlers(
            HandlerEnum.ON_REDUCED_FLUID, slot, fluid_id, reduced_fluid_volume, is_final
        )

    def SubscribeOnStructureChanged(self, handler):
        # type: (typing.Callable[[bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_STRUCTURE_CHANGED, handler)

    def CallOnStructureChangedHandlers(self, structure_finished):
        # type: (bool) -> None
        self.CallHandlers(HandlerEnum.ON_STRUCTURE_CHANGED, structure_finished)

    def SubscribeOnWorkStatusUpdated(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_WORK_STATUS_UPDATED, handler)

    def CallOnWorkStatusUpdatedHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_WORK_STATUS_UPDATED)

    def SubscribeOnHeatWork(self, handler):
        # type: (typing.Callable[[], None]) -> None
        self.Subscribe(HandlerEnum.ON_HEAT_WORK, handler)

    def CallOnHeatWorkHandlers(self):
        # type: () -> None
        self.CallHandlers(HandlerEnum.ON_HEAT_WORK)


    def SubscribeOnSetDeactiveFlag(self, handler):
        # type: (typing.Callable[[int, bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_SET_DEACTIVE_FLAG, handler)

    def CallOnSetDeactiveFlagHandlers(self, flag, flush):
        # type: (int, bool) -> None
        self.CallHandlers(HandlerEnum.ON_SET_DEACTIVE_FLAG, flag, flush)

    def SubscribeOnUnsetDeactiveFlag(self, handler):
        # type: (typing.Callable[[int, bool], None]) -> None
        self.Subscribe(HandlerEnum.ON_UNSET_DEACTIVE_FLAG, handler)

    def CallOnUnsetDeactiveFlagHandlers(self, flag, flush):
        # type: (int, bool) -> None
        self.CallHandlers(HandlerEnum.ON_UNSET_DEACTIVE_FLAG, flag, flush)

    def UnsubscribeOnTicking(self, handler):
        # type: (typing.Callable) -> None
        self.Unsubscribe(HandlerEnum.ON_TICKING, handler)

    def UnsubscribeOnSlotUpdate(self, handler):
        # type: (typing.Callable) -> None
        self.Unsubscribe(HandlerEnum.ON_SLOT_UPDATE, handler)

    def UnsubscribeOnClick(self, handler):
        # type: (typing.Callable) -> None
        self.Unsubscribe(HandlerEnum.ON_CLICK, handler)


class HandlerEnum:
    ON_PLACED = "on_placed"
    ON_TICKING = "on_ticking"
    ON_BLOCK_REDSTONE_STRENGTH_CHANGED = "on_block_redstone_strength_changed"
    ON_UNLOAD = "on_unload"
    ON_DESTROY = "on_destroy"
    ON_NEIGHBOR_CHANGED = "on_neighbor_changed"
    ON_BLOCK_RANDOM_TICK = "on_block_random_tick"
    ON_DEACTIVE_FLAGS_CHANGED = "on_deactive_flags_changed"
    ON_INVALIDATE_CACHES = "on_invalidate_caches"
    ON_CLICK = "on_click"
    ON_SYNC = "on_sync"
    ON_SLOT_UPDATE = "on_slot_update"
    ON_CUSTOM_COTAINER_PUT_ITEM = "on_custom_cotainer_put_item"
    ON_FLUID_SLOT_UPDATE = "on_fluid_slot_update"
    ON_ADDED_FLUID = "on_added_fluid"
    ON_REDUCED_FLUID = "on_reduced_fluid"
    ON_STRUCTURE_CHANGED = "on_structure_changed"
    ON_WORK_STATUS_UPDATED = "on_work_status_updated"
    ON_HEAT_WORK = "on_heat_work"
    ON_SET_DEACTIVE_FLAG = "on_set_deactive_flag"
    ON_UNSET_DEACTIVE_FLAG = "on_unset_deactive_flag"
