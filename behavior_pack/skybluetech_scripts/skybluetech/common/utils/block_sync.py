# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetPlayerDimensionId
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent
from skybluetech_scripts.tooldelta.events.server import DelServerPlayerEvent
from skybluetech_scripts.tooldelta.events.client import (
    ModBlockEntityLoadedClientEvent,
    ModBlockEntityRemoveClientEvent,
)
from skybluetech_scripts.tooldelta.general import ClientInitCallback, ServerInitCallback


class BlockSyncC2S(CustomC2SEvent):
    name = "st:BSC2S"

    MODE_BLOCK_LOADED = 0
    MODE_BLOCK_REMOVED = 1

    def __init__(self, x, y, z, block_id, mode=MODE_BLOCK_LOADED, player_id=""):
        # type: (int, int, int, str, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.block_id = block_id
        self.mode = mode
        self.player_id = player_id

    def marshal(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "block_id": self.block_id,
            "mode": self.mode,
            "player_id": self.player_id,
        }

    @classmethod
    def unmarshal(cls, data):
        return BlockSyncC2S(
            data["x"],
            data["y"],
            data["z"],
            data["block_id"],
            data["mode"],
            data["__id__"],
        )


class BlockSync:
    SIDE_CLIENT = 1
    SIDE_SERVER = 2

    def __init__(self, block_id, side):
        # type: (str, int) -> None
        self.block_id = block_id
        if side == self.SIDE_CLIENT:
            client_syncs[block_id] = self
        elif side == self.SIDE_SERVER:
            server_syncs[block_id] = self
            self.sync_pool = {}  # type: dict[str, set[tuple[int, int, int, int]]]

    def get_players(
        self,
        block_pos,  # type: tuple[int, int, int, int]
    ):
        return [player_id for player_id, v in self.sync_pool.items() if block_pos in v]

    def discard_block(self, block_pos):
        # type: (tuple[int, int, int, int]) -> None
        for player_id, block_poses in self.sync_pool.items():
            if block_pos in block_poses:
                block_poses.remove(block_pos)
                if not block_poses:
                    self.sync_pool.pop(player_id, None)

    def onServerSideRecvSyncEvent(self, event):
        # type: (BlockSyncC2S) -> None
        dim = GetPlayerDimensionId(event.player_id)
        player_loaded_block_counts = player2syncs.setdefault(event.player_id, {})
        loaded_blocks = self.sync_pool.setdefault(event.player_id, set())
        if event.mode == BlockSyncC2S.MODE_BLOCK_LOADED:
            count = player_loaded_block_counts[self.block_id] = (
                player_loaded_block_counts.get(self.block_id, 0) + 1
            )
            loaded_blocks.add((dim, event.x, event.y, event.z))
            if count > 1024:
                loaded_blocks.remove(next(iter(loaded_blocks)))
        elif event.mode == BlockSyncC2S.MODE_BLOCK_REMOVED:
            count = player_loaded_block_counts.get(self.block_id, 1) - 1
            if count <= 0:
                player_loaded_block_counts.pop(self.block_id, None)
            else:
                player_loaded_block_counts[self.block_id] = count
            loaded_blocks.discard((dim, event.x, event.y, event.z))
            if not loaded_blocks:
                self.sync_pool.pop(event.player_id, None)

    def onPlayerLeave(self, event):
        # type: (DelServerPlayerEvent) -> None
        self.sync_pool.pop(event.id, None)

    def onClientSideRecvBlockLoadedEvent(self, event):
        # type: (ModBlockEntityLoadedClientEvent) -> None
        BlockSyncC2S(
            event.posX,
            event.posY,
            event.posZ,
            self.block_id,
            mode=BlockSyncC2S.MODE_BLOCK_LOADED,
        ).send()

    def onClientSideRecvBlockRemovedEvent(self, event):
        # type: (ModBlockEntityRemoveClientEvent) -> None
        BlockSyncC2S(
            event.posX,
            event.posY,
            event.posZ,
            self.block_id,
            mode=BlockSyncC2S.MODE_BLOCK_REMOVED,
        ).send()


server_syncs = {}  # type: dict[str, BlockSync]
client_syncs = {}  # type: dict[str, BlockSync]
player2syncs = {}  # type: dict[str, dict[str, int]]


@ServerInitCallback()
def onServerInit():
    @BlockSyncC2S.Listen()
    def onServerSideRecvSyncEvent(event):
        # type: (BlockSyncC2S) -> None
        sync = server_syncs.get(event.block_id)
        if sync is None:
            return
        sync.onServerSideRecvSyncEvent(event)

    @DelServerPlayerEvent.Listen()
    def onPlayerLeave(event):
        # type: (DelServerPlayerEvent) -> None
        for block_id in player2syncs.pop(event.id, []):
            sync = server_syncs.get(block_id)
            if sync is None:
                return
            sync.onPlayerLeave(event)


@ClientInitCallback()
def onClientInit():
    @ModBlockEntityLoadedClientEvent.Listen()
    def onModBlockLoaded(event):
        # type: (ModBlockEntityLoadedClientEvent) -> None
        sync = client_syncs.get(event.blockName)
        if sync is None:
            return
        sync.onClientSideRecvBlockLoadedEvent(event)

    @ModBlockEntityRemoveClientEvent.Listen()
    def onModBlockRemoved(event):
        # type: (ModBlockEntityRemoveClientEvent) -> None
        sync = client_syncs.get(event.blockName)
        if sync is None:
            return
        sync.onClientSideRecvBlockRemovedEvent(event)
