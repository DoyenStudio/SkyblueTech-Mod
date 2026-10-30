# coding=utf-8
"""
取蔚蓝自己的界面（ToolDelta 的界面实例）、控件矩形、物品 id 的几个小工具 —— 合成样板、机件加工台、几个选物品的界面共用。
"""


def Path(value):  # type: (any) -> str
    """ ToolDelta 的 UIPath（或字符串）→ str（递给引擎的不能是 unicode）"""
    text = getattr(value, "base", value)
    return text.encode("utf-8") if isinstance(text, unicode) else str(text)  # noqa: F821  py2 的 unicode


def Active(cls):  # type: (type) -> any
    """ 开着的这一类 ToolDelta 界面（实例）；没开着给 None """
    from skybluetech_scripts.tooldelta.ui import GetActiveToolDeltaScreens
    for screen in GetActiveToolDeltaScreens():
        if isinstance(screen, cls):
            return screen
    return None


def Rect(ctrl):  # type: (any) -> tuple or None
    """ ToolDelta 控件（或 SDK 控件）的全局矩形 (x0, y0, x1, y1)；量不出来给 None """
    control = getattr(ctrl, "base", ctrl)
    try:
        x, y = control.GetGlobalPosition()
        w, h = control.GetSize()
    except Exception:  # noqa
        return None
    if w <= 0 or h <= 0:
        return None
    return x, y, x + w, y + h


def Inside(rect, pos):  # type: (tuple, tuple) -> bool
    return rect is not None and pos is not None and rect[0] <= pos[0] < rect[2] and rect[1] <= pos[1] < rect[3]


def Shown(screen, path):  # type: (any, any) -> bool
    """
    控件连同上面每一层都显示着。引擎的 GetVisible 只管控件自己：蔚蓝切页、MEI 开配方页时藏的都是外面那一层，
    而 MEI 找放置目标只看目标自己，配方页开着时点下去会落到底下被藏起来的目标上 —— 放置回调里从外往里再问一遍
    """
    parts = Path(path).strip("/").split("/")
    for depth in range(1, len(parts) + 1):
        try:
            control = screen.GetBaseUIControl("/" + "/".join(parts[:depth]))
            hidden = control is not None and control.GetVisible() is False
        except Exception:  # noqa  问不出来的那一层当看得见
            hidden = False
        if hidden:
            return False
    return True


def ItemId(stack):  # type: (any) -> str or None
    """ ItemStack 的物品 id（str：蔚蓝服务端的校验只认 str）；拿的不是物品给 None """
    item = getattr(stack, "Item", None)
    return Path(item.ItemId) if item is not None else None


def ItemName(stack):  # type: (any) -> str
    """ 给玩家看的名字（MEI 物品表里缓存的），取不到用 id """
    item = getattr(stack, "Item", None)
    if item is None:
        return "?"
    try:
        name = item.Info.ItemName
    except Exception:  # noqa
        name = None
    return Path(name or item.ItemId)


def Cell(stack):  # type: (any) -> tuple or None
    """ 样板一格存的样子：(物品 id 的 str, aux 的 int)；蔚蓝服务端的校验只认这两种类型 """
    item = getattr(stack, "Item", None)
    if item is None:
        return None
    return Path(item.ItemId), int(item.AuxValue or 0)


def GridCellAt(grid, columns, count, pos):  # type: (any, int, int, tuple) -> int or None
    """
    点下去的那一点落在 ToolDelta grid 的第几格（行优先）：按每一格控件自己的矩形认 ——
    格子之间有缝、grid 带边框也认得对；点在缝上给 None
    """
    for index in range(count):
        try:
            cell = grid.GetGridItem(index % columns, index // columns)
        except Exception:  # noqa
            continue
        if cell is not None and Inside(Rect(cell), pos):
            return index
    return None
