# coding=utf-8
import random
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.skybluetech.common.define import id_enum
from .register import LootHandler, DoRand


@LootHandler("loot_tables/chests/monster_room.json")
def handle_monster_room(
    playerId,  # type: str
):
    # 额外产出: 随机一个
    # - id_enum.FamicomCartidges.YELLOW
    # - id_enum.FamicomCartidges.PURPLE
    # - id_enum.FamicomCartidges.BLUE
    # - id_enum.FamicomCartidges.RED
    if DoRand(0.5):
        return [
            Item(
                random.choice([
                    id_enum.FamicomCartidges.YELLOW,
                    id_enum.FamicomCartidges.PURPLE,
                    id_enum.FamicomCartidges.BLUE,
                    id_enum.FamicomCartidges.RED,
                ])
            )
        ]
    return []
