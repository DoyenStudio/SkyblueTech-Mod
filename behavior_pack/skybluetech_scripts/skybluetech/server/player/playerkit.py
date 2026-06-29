# coding=utf-8
from .charge_service import ChargeService
from .armor_service import ArmorService


class PlayerKit(object):
    """每玩家服务容器:聚合各 PlayerService,统一调度 tick 与销毁。

    新增子系统时,在 __init__ 里实例化并加入 self._services 即可,
    无需改动 pool 的 tick/销毁逻辑。
    """

    def __init__(self, player_id):
        # type: (str) -> None
        self.player_id = player_id
        self.charge = ChargeService(player_id)
        self.armor = ArmorService(player_id)
        self._services = [self.charge, self.armor]

    def on_tick(self, ticks):
        # type: (int) -> None
        for service in self._services:
            if service.tick_interval and ticks % service.tick_interval == 0:
                service.on_tick()

    def destroy(self):
        for service in self._services:
            service.destroy()
