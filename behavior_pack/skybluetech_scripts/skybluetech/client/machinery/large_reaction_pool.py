# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.mod_block_event import (
    asModBlockLoadedListener, asModBlockRemovedListener,
)
from skybluetech_scripts.tooldelta.utils.nbt import ValueOf
from ...common.define.id_enum import LargeReactionPool
from ...common.machinery_def.large_reaction_pool import K_SURFACE
from .brine_evaporation_pond import PondFluidDisplay, _read_vector, remove_pond, track_pond


class ReactionPoolDisplay(PondFluidDisplay):
    def read_volume(self, data):
        snapshot = ValueOf(data.get(K_SURFACE))
        if not isinstance(snapshot, dict):
            return None, None, None
        fluid_id = ValueOf(snapshot.get("id"))
        ratio = ValueOf(snapshot.get("ratio"))
        if not fluid_id or ratio is None or not 0 < ratio <= 1:
            return None, None, None
        return _read_vector(snapshot, "origin"), (1, 2, 1), (fluid_id, ratio)


@asModBlockLoadedListener(LargeReactionPool.CONTROLLER)
def on_pool_loaded(event):
    track_pond(event, ReactionPoolDisplay())


@asModBlockRemovedListener(LargeReactionPool.CONTROLLER)
def on_pool_removed(event):
    remove_pond((event.dimensionId, event.posX, event.posY, event.posZ))
