# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.server import (
    ServerPlaceBlockEntityEvent,
    ServerBlockEntityTickEvent,
    BlockNeighborChangedServerEvent,
    BlockRemoveServerEvent,
    ServerBlockUseEvent,
    ServerEntityTryPlaceBlockEvent,
    PlayerTryPutCustomContainerItemServerEvent,
    ContainerItemChangedServerEvent,
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
    from typing import TypeVar

    MT = TypeVar("MT", bound=BaseMachine)
# TYPE_CHECKING END


def RegisterMachine(machine_cls):
    # type: (type[MT]) -> type[MT]
    """
    注册机器。所有机器类都必须使用此 `@RegisterMachine` 标注器标注。
    """
    if machine_cls.block_name:
        pool.machine_classes[machine_cls.block_name] = machine_cls
    for extra_block_name in machine_cls.extra_block_names:
        pool.machine_classes[extra_block_name] = machine_cls
    return machine_cls


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


@PlayerTryPutCustomContainerItemServerEvent.ListenWithUserData()
def onCustomCotainerPutItem(event):
    # type: (PlayerTryPutCustomContainerItemServerEvent) -> None
    dimensionId = GetPlayerDimensionId(event.playerId)
    m = pool.GetMachineStrict(dimensionId, event.x, event.y, event.z)
    if isinstance(m, ItemContainer):
        m.OnCustomCotainerPutItem(event)


@BlockNeighborChangedServerEvent.Listen()
def onNeighborChanged(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.posX, event.posY, event.posZ)
    if m:
        m.OnNeighborChanged(event)


@ServerBlockEntityTickEvent.Listen()
def onTicking(event):
    # type: (ServerBlockEntityTickEvent) -> None
    m = pool.GetMachineStrict(event.dimension, event.posX, event.posY, event.posZ)
    if m:
        m.OnTicking()


@ServerBlockUseEvent.Listen()
def onClick(event):
    # type: (ServerBlockUseEvent) -> None
    m = pool.GetMachineStrict(event.dimensionId, event.x, event.y, event.z)
    if (
        isinstance(m, (FluidContainer, MultiFluidContainer))
        and not IsSneaking(event.playerId)
        and m.ifPlayerInteractWithBucket(event.playerId)
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
        and m.ifPlayerInteractWithBucket(event.entityId, test=True)
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


@BlockRemoveServerEvent.Listen()
def OnUnload(event):
    # type: (BlockRemoveServerEvent) -> None
    m = pool.PopMachineStrict(event.dimension, event.x, event.y, event.z)
    if m is not None:
        m.OnDestroy()
        m.OnUnload()
