# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF
"游戏事件入口: 查找机器、处理交互并派发实例事件。"
from skybluetech_scripts.tooldelta.utils.timer import Delay
from skybluetech_scripts.skybluetech.common.define.id_enum.items import (
    MULTIBLOCK_STRUCTURE_SCEPTER,
)

from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    BlockRandomTickServerEvent,
    BlockRemoveServerEvent,
    BlockStrengthChangedServerEvent,
    ContainerItemChangedServerEvent,
    EntityPlaceBlockAfterServerEvent,
    ItemPullOutCustomContainerServerEvent,
    ItemPushInCustomContainerServerEvent,
    PlayerTryPutCustomContainerItemServerEvent,
    ServerBlockEntityTickEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
    ServerItemUseOnEvent,
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.events.server.world import (
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
)

from ..basic.base_clicker import BaseClicker
from ..basic.gui_ctrl import GUIControl
from ..basic.item_container import ItemContainer
from ..basic.multi_fluid_container import MultiFluidContainer
from ..core import pool
from ..core.registry import TryGetMachineCls


@BlockNeighborChangedServerEvent.Listen()
def on_neighbor_changed(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    m = pool.GetLoadedMachine(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.handler.CallOnNeighborChangedHandlers(event)
        m.handler.CallOnInvalidateCachesHandlers()


@BlockStrengthChangedServerEvent.Listen()
def on_block_strength_changed(event):
    # type: (BlockStrengthChangedServerEvent) -> None
    m = pool.GetLoadedMachine(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.handler.CallOnBlockRedstoneStrengthChangedHandlers(event)


@ServerBlockEntityTickEvent.Listen()
def on_ticking(event):
    # type: (ServerBlockEntityTickEvent) -> None
    m = pool.GetLoadedMachine(event.dimension, event.posX, event.posY, event.posZ)
    if m:
        m.handler.CallOnTickingHandlers()


@BlockRandomTickServerEvent.Listen()
def on_block_random_tick(event):
    # type: (BlockRandomTickServerEvent) -> None
    m = pool.GetLoadedMachine(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.handler.CallOnBlockRandomTickHandlers(event)


@ServerBlockUseEvent.Listen()
def on_click(event):
    # type: (ServerBlockUseEvent) -> None
    from ..utils.bans import reject_banned_machine

    if reject_banned_machine(event.playerId, event.blockName):
        event.cancel()
        return
    if event.item.id == MULTIBLOCK_STRUCTURE_SCEPTER:
        from ...tools.multiblock_structure_scepter import try_build

        if try_build(event.playerId, event.blockName, event.dimensionId, (event.x, event.y, event.z)):
            event.cancel()
            return
    m = pool.GetLoadedMachine(event.dimensionId, event.x, event.y, event.z)
    if (
        isinstance(m, MultiFluidContainer)
        and not CF.CreatePlayer(event.playerId).isSneaking()
        and m.on_player_interact_with_bucket(event.playerId)
    ):
        event.cancel()
        return
    if isinstance(m, BaseClicker):
        if not CF.CreatePlayer(event.playerId).isSneaking():
            if m._can_click(event):
                m.handler.CallOnClickHandlers(event)
            event.cancel()
    elif isinstance(m, GUIControl):
        m.handler.CallOnClickHandlers(event)


@ServerItemUseOnEvent.Listen()
def on_use_item(event):
    # type: (ServerItemUseOnEvent) -> None
    from ..utils.bans import reject_banned_machine

    if reject_banned_machine(event.entityId, event.blockName):
        event.cancel()
        return
    if event.item.id == MULTIBLOCK_STRUCTURE_SCEPTER:
        from ...tools.multiblock_structure_scepter import try_build

        if try_build(event.entityId, event.blockName, event.dimensionId, (event.x, event.y, event.z)):
            event.cancel()
            return
    m = pool.GetLoadedMachine(event.dimensionId, event.x, event.y, event.z)
    if (
        isinstance(m, MultiFluidContainer)
        and not CF.CreatePlayer(event.entityId).isSneaking()
        and m.on_player_interact_with_bucket(event.entityId, test=True)
    ):
        event.cancel()
    if isinstance(m, BaseClicker) and not CF.CreatePlayer(event.entityId).isSneaking():
        event.cancel()


@ServerEntityTryPlaceBlockEvent.Listen()
def on_try_place(event):
    # type: (ServerEntityTryPlaceBlockEvent) -> None
    from ..utils.bans import reject_banned_machine

    if reject_banned_machine(event.entityId, event.fullName):
        event.cancel()
        return
    m = TryGetMachineCls(event.fullName)
    if m:
        m.OnPrePlaced(event)


@EntityPlaceBlockAfterServerEvent.Listen()
def on_entity_placed(event):
    # type: (EntityPlaceBlockAfterServerEvent) -> None
    m = pool.GetMachineWithoutCls(
        event.dimensionId, event.x, event.y, event.z, event.fullName
    )
    if m is not None:
        m.bdata["owner"] = event.entityId


@ServerPlaceBlockEntityEvent.Listen()
def on_placed(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    m = pool.GetMachineWithoutCls(
        event.dimension, event.posX, event.posY, event.posZ, event.blockName
    )
    if m:
        m.handler.CallOnPlacedHandlers(event)
    pool.InvalidateNearbyCaches(event.dimension, event.posX, event.posY, event.posZ)


@BlockRemoveServerEvent.Listen()
def on_unload(event):
    # type: (BlockRemoveServerEvent) -> None
    m = pool.PopMachineStrict(event.dimension, event.x, event.y, event.z)
    if m is not None:
        m.handler.CallOnDestroyHandlers()
        m.handler.CallOnUnloadHandlers()
    pool.InvalidateNearbyCaches(event.dimension, event.x, event.y, event.z)


@PlayerTryPutCustomContainerItemServerEvent.ListenWithUserData()
def on_custom_container_put_item(event):
    # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
    from ..interfaces import FluidInputInterface, FluidOutputInterface

    dimensionId = CF.CreateDimension(event.playerId).GetEntityDimensionId()
    m = pool.GetLoadedMachine(dimensionId, event.x, event.y, event.z)
    if isinstance(m, (FluidInputInterface, FluidOutputInterface)):
        event.cancel()
        return
    if isinstance(m, ItemContainer):
        m.handler.CallOnCustomCotainerPutItemHandlers(event)


@ItemPushInCustomContainerServerEvent.Listen()
def on_item_push_in(event):
    # type: (ItemPushInCustomContainerServerEvent) -> None
    from ..interfaces import FluidInputInterface, FluidOutputInterface

    m = pool.GetLoadedMachine(event.dimension, event.x, event.y, event.z)
    if isinstance(m, (FluidInputInterface, FluidOutputInterface)):
        event.cancel()
        return
    if not isinstance(m, ItemContainer):
        return
    if (
        not m.IsValidInput(event.collectionIndex, event.item)
        or event.collectionIndex not in m.item_input_slots
    ):
        event.cancel()


@ItemPullOutCustomContainerServerEvent.Listen()
def on_item_pull_out(event):
    # type: (ItemPullOutCustomContainerServerEvent) -> None
    m = pool.GetLoadedMachine(event.dimension, event.x, event.y, event.z)
    if not isinstance(m, ItemContainer):
        return
    if event.collectionIndex not in m.item_output_slots:
        event.cancel()


@ContainerItemChangedServerEvent.ListenWithUserData()
@Delay(0)
def on_slot_update(event):
    # type: (ContainerItemChangedServerEvent) -> None
    pos = event.pos
    if pos is None:
        return
    x, y, z = pos
    m = pool.GetLoadedMachine(event.dimensionId, x, y, z)
    if isinstance(m, ItemContainer):
        m.handler.CallOnSlotUpdateHandlers(event.slot)


@ChunkLoadedServerEvent.Listen()
def on_chunk_loaded(event):
    # type: (ChunkLoadedServerEvent) -> None
    if not event.blockEntities:
        return
    for block_entity_posdata in event.blockEntities[:]:
        x = block_entity_posdata["posX"]
        y = block_entity_posdata["posY"]
        z = block_entity_posdata["posZ"]
        machine_cls = TryGetMachineCls(block_entity_posdata["blockName"])
        if machine_cls is not None:
            pool.LoadMachine(event.dimension, x, y, z, machine_cls)


@ChunkAcquireDiscardedServerEvent.Listen()
def on_chunk_discarded(event):
    # type: (ChunkAcquireDiscardedServerEvent) -> None
    for block_entity_posdata in event.blockEntities:
        x = block_entity_posdata["posX"]
        y = block_entity_posdata["posY"]
        z = block_entity_posdata["posZ"]
        m = pool.PopMachineStrict(event.dimension, x, y, z)
        if m is not None:
            m.handler.CallOnUnloadHandlers()
        pool.InvalidateNearbyCaches(event.dimension, x, y, z)
