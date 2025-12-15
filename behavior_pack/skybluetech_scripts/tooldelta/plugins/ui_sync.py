# coding=utf-8

from weakref import WeakValueDictionary as WVD
from mod_log import logger
from ..events.notify import NotifyToClient, NotifyToServer
from ..events.server.world import DelServerPlayerEvent
from ..events.client.sync import ClientNewSync, ClientPopSync, S2CSyncDatas, ServerDelSync
from ..general import ServerInitCallback
from ..api.timer import AsTimerFunc

# 主要用于 UI 信息的同步。
# 比如:
#   1. 服务端 - 服务端开启 ui 同步(例如玩家点击方块) -> 挂起预请求, 将准备好的同步器放入同步池, 同时要求客户端打开界面
#              并携带同步器 id
#   2. 客户端 - 收到打开界面请求 -> 创建界面新增同步, 初始化时又向服务端申请开始同步
#   3. 服务端 - 接受同步申请, 去除预请求, 且在活跃池添加玩家端同步名
#   4. 服务端 - 开始将同步信息发送至客户端
#   5. 客户端 - 玩家退出界面 -> 向服务器申请停止同步
#   6. 服务端 - 同步源消失(例如方块被破坏了) -> 服务器使玩家强行关闭 UI, 并将同步项从同步池中移除
#   7. 服务端 - 如果在处理同步信息的时候遇到了无效同步名, 则删除同步项 (之后做什么?)

SYNC_DELAY = 0.2

EVENT_KEY = "_evtName" # 同步事件里表示同步类型的 key
S2C_SERVER = 0
S2C_CLIENT = 1

DEFAULT_UPDATE_FUNC = lambda :None

DEBUG = False

class S2CSync(object):
    """
    服务端-客户端 UI 内容同步器。
    必须先在服务端创建, 然后才能在客户端创建, 建立内容同步。
    服务端创建并激活后, 被放入同步池, 需要此同步项的客户端此时可以请求同步。

    在创建后, 使用 Activate() 方法激活同步。 (客户端/服务端)
    需要销毁同步, 则使用 Deactivate() 方法。 (客户端/服务端)
    
    服务端: 被实例化时放入服务器同步池, 被销毁时从同步池移出。

    客户端: 被实例化时放入客户端活跃池, 被销毁时从活跃池移出。
    """
    def __init__(self, mode, sync_id=None):
        # type: (int, str | None) -> None
        if self.__class__ is S2CSync:
            # 本类实例化时什么也不做
            return
        self.sync_id = sync_id or self.GenerateSpecName()
        self._mode = mode
        self.activated = False
        if mode == S2C_CLIENT:
            self.WhenUpdated = DEFAULT_UPDATE_FUNC
        self._changed = True

    def GenerateSpecName(self):
        # type: () -> str
        "覆写该方法时返回此同步项的独一名。"
        return "tds2c_%d" % id(self)

    def Marshal(self):
        # type: () -> dict
        "覆写该方法时返回该同步对象的序列化。"
        return {}

    def Unmarshal(self, data):
        # type: (dict) -> None
        "覆写该方法时返回该同步对象的反序列化。"
        pass

    def MarkedAsChanged(self):
        self._changed = True

    def GetPlayersInSync(self):
        return [i for i in server_active_syncs if self.sync_id in server_active_syncs[i]]

    def PlayerInSync(self, player_id):
        # type: (str) -> bool
        return self.sync_id in server_active_syncs.get(player_id, set())

    def AnyoneInSync(self):
        # type: () -> bool
        return any(self.sync_id in v for v in server_active_syncs.values())

    def toBroadcastData(self):
        "服务端更新数据到客户端。"
        data = self.Marshal()
        data[EVENT_KEY] = self.sync_id
        return data

    def updateFromServer(self, event_data):
        self.Unmarshal(event_data)
        self.WhenUpdated()

    @classmethod
    def NewClient(cls, sync_id):
        return cls(S2C_CLIENT, sync_id)

    @classmethod
    def NewServer(cls, spec_key=None):
        return cls(S2C_SERVER, spec_key)

    def Activate(self):
        "激活同步器。"
        if self.activated:
            return self
        if self._mode == S2C_CLIENT:
            clientAddActiveSync(self)
        elif self._mode == S2C_SERVER:
            serverAddSync(self)
        self.activated = True
        return self

    def Deactivate(self):
        if clientRemoveActiveSync is None or serverRemoveSync is None:
            # python closed
            return
        elif not self.activated:
            return
        if self._mode == S2C_CLIENT:
            clientRemoveActiveSync(self)
        elif self._mode == S2C_SERVER:
            serverRemoveSync(self)
        self.activated = False

    def __del__(self):
        self.Deactivate()


server_sync_pool     = WVD() # type: WVD[str, S2CSync]      # [nkey: sync]          # server only
client_pending_syncs = {} #  type: dict[str, set[str]]      # [cliId: set[nkey]]    # server only
server_active_syncs  = {} #  type: dict[str, set[str]]      # [cliId: set[nkey]]    # server only
client_active_syncs  = WVD() # type: WVD[str, S2CSync]      # [nkey: sync]          # client only

def AddSyncPending(cliId, sync):
    # type: (str, S2CSync) -> None
    """
    挂起一个即将完成的同步请求。
    只有在对应挂起请求的情况下, 客户端的同步请求才被接受。

    Args:
        cliId (str): 客户端 ID
        sync (S2CSync): 同步对象
    """
    if DEBUG:
        logger.info("[SyncServer] Add sync pending {}".format(sync.sync_id))
    client_pending_syncs.setdefault(cliId, set()).add(sync.sync_id)

def GetAllPlayersInSync(sync_id):
    # type: (str) -> list[str]
    """
    根据同步器 ID 获取所有正在进行此同步的 playerId

    Args:
        sync_id (str): 同步器 ID

    Returns:
        list[str]: playerIds
    """
    ret = [] # type: list[str]
    for cliId, sync_names in server_active_syncs.items():
        if sync_id in sync_names:
            ret.append(cliId)
    return ret

def notifySyncToSingleClient(cliId, sync_ids):
    # type: (str, set[str]) -> None
    event_body = []
    for sid in sync_ids:
        sync = server_sync_pool.get(sid)
        if sync is not None:
            event_body.append(sync.toBroadcastData())
        else:
            logger.warning("[SyncServer] S2C sync {} terminated".format(sid))
            server_active_syncs[cliId].remove(sid)
    NotifyToClient(cliId, S2CSyncDatas(event_body))

@AsTimerFunc(SYNC_DELAY)
def serverBroadcastSyncEvents():
    posted_sync_ids = set() # type: set[str]
    for cliId, sync_ids in server_active_syncs.copy().items():
        sync_ids = {i for i in sync_ids if server_sync_pool[i]._changed}
        notifySyncToSingleClient(cliId, sync_ids)
        posted_sync_ids |= sync_ids
    for sync_id in posted_sync_ids:
        server_sync_pool[sync_id]._changed = False

@S2CSyncDatas.Listen()
def clientProcessSyncEvent(eventData):
    # type: (S2CSyncDatas) -> None
    for sync_data in eventData.sync_datas:
        sync = client_active_syncs.get(sync_data[EVENT_KEY])
        if sync is not None:
            sync.updateFromServer(sync_data)
        else:
            logger.warning("[SyncClient] Client sync {} not exists".format(sync_data[EVENT_KEY]))

def serverAddSync(sync):
    # type: (S2CSync) -> None
    if DEBUG:
        logger.info("[SyncServer] Add s2c sync {}".format(sync.__class__.__name__))
    server_sync_pool[sync.sync_id] = sync

def serverRemoveSync(sync):
    # type: (S2CSync) -> None
    if DEBUG:
        logger.info("[SyncServer] Remove s2c sync {}".format(sync.sync_id))
    for cliId, sync_names in server_active_syncs.copy().items():
        if sync.sync_id in sync_names:
            sync_names.remove(sync.sync_id)
            NotifyToClient(cliId, ServerDelSync(sync.sync_id))
            if not sync_names:
                del server_active_syncs[cliId]

# TODO: 玩家有可能同时请求多个同步器

def clientAddActiveSync(sync):
    # type: (S2CSync) -> None
    if DEBUG:
        logger.info("[SyncClient] Add s2c sync {}".format(sync.__class__.__name__))
    client_active_syncs[sync.sync_id] = sync
    NotifyToServer(ClientNewSync(sync.sync_id))

def clientRemoveActiveSync(sync):
    # type: (S2CSync) -> None
    NotifyToServer(ClientPopSync(sync.sync_id))
    client_active_syncs.pop(sync.sync_id, None)

@ClientNewSync.Listen()
def onClientNewSync(event):
    # type: (ClientNewSync) -> None
    if DEBUG:
        logger.info("[SYNC] Client request new sync {}".format(event.sync_name))
    pendingsync_ids = client_pending_syncs.get(event.pid)
    if pendingsync_ids is not None and event.sync_name in pendingsync_ids:
        pendingsync_ids.remove(event.sync_name)
        if not pendingsync_ids:
            del client_pending_syncs[event.pid]
        server_active_syncs.setdefault(event.pid, set()).add(event.sync_name)
        notifySyncToSingleClient(event.pid, server_active_syncs[event.pid])
    else:
        logger.warning("[SYNC] Client request new sync {} but not pending".format(event.sync_name))

@ClientPopSync.Listen()
def onClientPopSync(event):
    # type: (ClientPopSync) -> None
    # 考虑到可能执行在 serverRemoveSync 之后
    if DEBUG:
        logger.info("[SYNC] Client request pop sync {}".format(event.sync_name))
    if event.sync_name in server_active_syncs.get(event.pid, set()):
        server_active_syncs[event.pid].remove(event.sync_name)
        if not server_active_syncs[event.pid]:
            del server_active_syncs[event.pid]

@DelServerPlayerEvent.Listen()
def onDelServerPlayerEvent(event):
    # type: (DelServerPlayerEvent) -> None
    """ Player GC """
    playerId = event.id
    client_pending_syncs.pop(playerId, None)
    server_active_syncs.pop(playerId, None)

@ServerDelSync.Listen()
def onServerDelSync(event):
    # type: (ServerDelSync) -> None
    """ Sync GC 目前什么也不做, 因为同步被掐断的时候服务端理应通知客户端退出 UI """
    if DEBUG:
        logger.info("[SYNC] Server request pop cli sync {}".format(event.sync_name))
    # server_sync_pool.pop(event.sync_name, None)
    pass

@ServerInitCallback()
def onServerInit():
    serverBroadcastSyncEvents()


__all__ = [
    "S2CSync",
    "AddSyncPending",
    "GetAllPlayersInSync",
]
