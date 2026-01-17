# coding=utf-8
from ..define import Item

if 0:
    from typing import Callable


def SortItems(items, key=lambda i: i.id):
    # type: (list[Item], Callable[[Item], str | int]) -> list[Item]
    its = {} # type: dict[str, list[Item]]
    max_stacks = {} # type: dict[str, int]
    items = [i.copy() for i in items]
    for item in items:
        if item.id not in its:
            its[item.id] = []
            max_stacks[item.id] = item.GetBasicInfo().maxStackSize
        its[item.id].append(item)
    res = [] # type: list[Item]
    for items in sorted(its.values(), key=lambda x: key(x[0])):
        i_res = [] # type: list[Item]
        for item in items:
            for item_2 in i_res:
                if item_2.CanMerge(item):
                    sum_count = item_2.count + item.count
                    max_stack = max_stacks[item.id]
                    if sum_count <= max_stack:
                        item_2.count = sum_count
                        item = None
                        break
                    else:
                        item.count -= sum_count - max_stack
                        item_2.count = max_stack
            if item is not None:
                i_res.append(item)
        res.extend(i_res)
    return res

