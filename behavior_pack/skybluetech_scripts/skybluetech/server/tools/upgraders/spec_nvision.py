# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import (
    AddEffectToEntity,
    RemoveEffectFromEntity,
)
from skybluetech_scripts.skybluetech.common.define.id_enum import ObjectUpgraders
from skybluetech_scripts.skybluetech.server.player.armor_service import ArmorService

EFFECT_NAME = "night_vision"
# 持续时间长于刷新周期(10s), 使剩余时间始终高于夜视临界闪烁阈值, 避免画面闪烁。
EFFECT_DURATION = 20
EFFECT_AMPLIFIER = 0


def _grant(player_id):
    # type: (str) -> None
    AddEffectToEntity(player_id, EFFECT_NAME, EFFECT_DURATION, EFFECT_AMPLIFIER, False)


def _revoke(player_id):
    # type: (str) -> None
    RemoveEffectFromEntity(player_id, EFFECT_NAME)


ArmorService.register_upgrade_handler(
    ObjectUpgraders.SPEC_NVISION,
    on_activate=_grant,
    on_deactivate=_revoke,
    on_periodic=_grant,
    power_cost=200,  # 200 RF / 10s
)
