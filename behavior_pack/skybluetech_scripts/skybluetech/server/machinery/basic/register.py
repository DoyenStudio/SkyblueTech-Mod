# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.server import (
    ServerPlaceBlockEntityEvent,
    ServerBlockEntityTickEvent,
    BlockNeighborChangedServerEvent,
    BlockStrengthChangedServerEvent,
    BlockRandomTickServerEvent,
    BlockRemoveServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
    PlayerTryPutCustomContainerItemServerEvent,
    ContainerItemChangedServerEvent,
    ItemPushInCustomContainerServerEvent,
    ItemPullOutCustomContainerServerEvent,
    ServerItemUseOnEvent,
)
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId, IsSneaking
from skybluetech_scripts.tooldelta.api.common import Delay
from .. import pool
from .base_clicker import BaseClicker
from .base_machine import BaseMachine
from .fluid_container import FluidContainer
from .multi_fluid_container import MultiFluidContainer
from .item_container import ItemContainer
from .gui_ctrl import GUIControl

# TYPE_CHECKING
if 0:
    import typing

    MT = typing.TypeVar("MT", bound=BaseMachine)
# TYPE_CHECKING END


def RegisterMachine(machine_cls):
    # type: (type[MT]) -> type[MT]
    """
    注册机器。所有机器类都必须使用此 `@RegisterMachine` 标注器标注。
    """
    if machine_cls.block_name:
        pool.machine_classes[machine_cls.block_name] = machine_cls
    for interface_cls, extra_block_names in machine_cls._extra_block_names.items():
        for extra_block_name in extra_block_names:
            pool.machine_classes[extra_block_name] = interface_cls
    return machine_cls


@BlockNeighborChangedServerEvent.Listen()
def onNeighborChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.OnNeighborChanged(event)
        m.OnInvalidateCaches()


@BlockStrengthChangedServerEvent.Listen()
def onBlockStrengthChanged(event):
    # type: (BlockStrengthChangedServerEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.OnBlockRedstoneStrengthChanged(event)


@ServerBlockEntityTickEvent.Listen()
def onTicking(event):
    # type: (ServerBlockEntityTickEvent) -> None
    m = pool.GetMachineStrict(event.dimension, event.posX, event.posY, event.posZ)
    if m:
        m.OnTicking()


@BlockRandomTickServerEvent.Listen()
def onBlockRandomTick(event):
    # type: (BlockRandomTickServerEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.OnBlockRandomTick(event)


@ServerBlockUseEvent.Listen()
def onClick(event):
    # type: (ServerBlockUseEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.x, event.y, event.z)
    if (
        isinstance(m, (FluidContainer, MultiFluidContainer))
        and not IsSneaking(event.playerId)
        and m.on_player_interact_with_bucket(event.playerId)
    ):
        event.cancel()
        return
    if isinstance(m, BaseClicker):
        if not IsSneaking(event.playerId):
            m._revOnClick(event)
            event.cancel()
    elif isinstance(m, GUIControl):
        m.OnClick(event)


@ServerItemUseOnEvent.Listen()
def onUseItem(event):
    # type: (ServerItemUseOnEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.x, event.y, event.z)
    if (
        isinstance(m, (FluidContainer, MultiFluidContainer))
        and not IsSneaking(event.entityId)
        and m.on_player_interact_with_bucket(event.entityId, test=True)
    ):
        event.cancel()
    if isinstance(m, BaseClicker) and not IsSneaking(event.entityId):
        event.cancel()


@ServerEntityTryPlaceBlockEvent.Listen()
def onTryPlace(event):
    # type: (ServerEntityTryPlaceBlockEvent) -> None
    m = pool.TryGetMachineCls(event.fullName)
    if m:
        m.OnPrePlaced(event)


@ServerPlaceBlockEntityEvent.Listen()
def onPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    m = pool.GetMachineWithoutCls(
        event.dimension, event.posX, event.posY, event.posZ, event.blockName
    )
    if m:
        m.OnPlaced(event)
    pool.InvalidateNearbyCaches(event.dimension, event.posX, event.posY, event.posZ)


@BlockRemoveServerEvent.Listen()
def OnUnload(event):
    # type: (BlockRemoveServerEvent) -> None
    m = pool.PopMachineStrict(event.dimension, event.x, event.y, event.z)
    if m is not None:
        m.OnDestroy()
        m.OnUnload()
    pool.InvalidateNearbyCaches(event.dimension, event.x, event.y, event.z)


@PlayerTryPutCustomContainerItemServerEvent.ListenWithUserData()
def onCustomContainerPutItem(event):
    # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
    from ..interfaces import FluidInputInterface, FluidOutputInterface

    dimensionId = GetPlayerDimensionId(event.playerId)
    m = pool.GetMachineStrict(dimensionId, event.x, event.y, event.z)
    if isinstance(m, (FluidInputInterface, FluidOutputInterface)):
        event.cancel()
        return
    if isinstance(m, ItemContainer):
        m.OnCustomCotainerPutItem(event)


@ItemPushInCustomContainerServerEvent.Listen()
def onItemPushIn(event):
    # type: (ItemPushInCustomContainerServerEvent) -> None
    from ..interfaces import FluidInputInterface, FluidOutputInterface

    m = pool.GetMachineStrict(event.dimension, event.x, event.y, event.z)
    if isinstance(m, (FluidInputInterface, FluidOutputInterface)):
        event.cancel()
        return
    if not isinstance(m, ItemContainer):
        return
    if (
        not m.IsValidInput(event.collectionIndex, event.item)
        or event.collectionIndex not in m.input_slots
    ):
        event.cancel()


@ItemPullOutCustomContainerServerEvent.Listen()
def onItemPullOut(event):
    # type: (ItemPullOutCustomContainerServerEvent) -> None
    m = pool.GetMachineStrict(event.dimension, event.x, event.y, event.z)
    if not isinstance(m, ItemContainer):
        return
    if event.collectionIndex not in m.output_slots:
        event.cancel()


@ContainerItemChangedServerEvent.ListenWithUserData()
@Delay(0)
def onSlotUpdate(event):
    # type: (ContainerItemChangedServerEvent) -> None
    pos = event.pos
    if pos is None:
        return
    x, y, z = pos
    m = pool.GetMachineStrict(event.dimensionId, x, y, z)
    if isinstance(m, ItemContainer):
        m.OnSlotUpdate(event.slot)
