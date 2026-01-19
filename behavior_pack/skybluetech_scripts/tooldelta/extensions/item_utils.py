# coding=utf-8
from ..define import Item

if 0:
    from typing import Callable


def SortItems(items, key=lambda i: i.id):
    # type: (list[Item], Callable[[Item], str | int]) -> list[Item]
    res = [] # type: list[Item]
    for item in (i.copy() for i in items):
        for exists_item in res:
            if exists_item.StackFull():
                continue
            if exists_item.CanMerge(item):
                sum_count = exists_item.count + item.count
                max_stack = exists_item.GetBasicInfo().maxStackSize
                if sum_count <= max_stack:
                    exists_item.count = sum_count
                    item.count = 0
                    break
                else:
                    exists_item.count = max_stack
                    item.count = sum_count - max_stack
        if item.count > 0:
            res.append(item)
    return sorted(res, key=key)

