# coding=utf-8


def init_server():
    from .skybluetech import server
    from .tooldelta import extensions


def init_client():
    from .skybluetech import client
    # 与 MoreEnoughItems 的联动。import 即挂上 UiInitFinished 监听，
    # 玩家没装 MEI 的话它什么都不做（软依赖）
    from .skybluetech.external import mei
