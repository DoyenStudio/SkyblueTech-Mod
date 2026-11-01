# coding=utf-8
"""按可放置位置、背包库存和接口最低数量分配多方块建材。"""


def create_build_plan(candidates, available_counts, required_counts):
    # type: (list, dict[str, int], dict[str, int]) -> list[tuple]
    """返回 ``[(世界坐标, 方块 ID)]``，不修改传入的坐标、库存或缺额。

    candidates 为 ``[(坐标三元组, 按模板优先级排列的方块 ID 元组)]``；
    每个世界坐标只能出现一次。库存和最低缺额均为非负整数计数。
    先尽可能满足最低缺额，再在不降低已分配材料数量的前提下填满其余位置。
    """
    options = {}
    capacity = {}
    for pos, block_ids in candidates:
        if pos in options:
            raise ValueError("Duplicate build position: %r" % (pos,))
        allowed = []
        for block_id in block_ids:
            count = available_counts.get(block_id, 0)
            if count > 0 and block_id not in allowed:
                allowed.append(block_id)
                capacity[block_id] = count
        options[pos] = allowed

    # 先处理只能用少数建材的格子，同等条件下由低向高搭建。
    positions = sorted(
        options,
        key=lambda pos: (len(options[pos]), pos[1], pos[0], pos[2]),
    )
    allowed_positions = {}
    for pos in positions:
        for block_id in options[pos]:
            allowed_positions.setdefault(block_id, []).append(pos)

    assigned = {}
    used_counts = {}

    def add_required_block(block_id):
        """给一种材料增加一格；遇到已分配格时沿增广路径搬移材料。"""
        queue = [block_id]
        previous = {}
        seen = {block_id}
        for current_id in queue:
            for pos in allowed_positions[current_id]:
                owner = assigned.get(pos)
                if owner is None:
                    # 每一步只搬移一个原有方块，只有起点材料的用量加一。
                    assigned[pos] = current_id
                    while current_id in previous:
                        parent_id, parent_pos = previous[current_id]
                        assigned[parent_pos] = parent_id
                        current_id = parent_id
                    used_counts[block_id] = used_counts.get(block_id, 0) + 1
                    return True
                if owner not in seen:
                    seen.add(owner)
                    previous[owner] = (current_id, pos)
                    queue.append(owner)
        return False

    # 比如钻机的流体口只有一个允许位置，先于有多个位置的能量口分配。
    required_ids = sorted(
        (block_id for block_id in allowed_positions
         if required_counts.get(block_id, 0) > 0),
        key=lambda block_id: (len(allowed_positions[block_id]), block_id),
    )
    for block_id in required_ids:
        target = min(required_counts[block_id], capacity[block_id], len(positions))
        for _i in range(target):
            if not add_required_block(block_id):
                break

    def fill_position(start_pos):
        """从空格反向找尚有库存的材料，保留之前所有材料的已用数量。"""
        queue = [start_pos]
        previous = {}
        seen_positions = {start_pos}
        seen_blocks = set()
        for pos in queue:
            # 保持模板可选项顺序，优先使用普通外壳等排在前面的材料。
            for block_id in options[pos]:
                if block_id in seen_blocks:
                    continue
                seen_blocks.add(block_id)
                previous[block_id] = pos
                if used_counts.get(block_id, 0) < capacity[block_id]:
                    used_counts[block_id] = used_counts.get(block_id, 0) + 1
                    while True:
                        target_pos = previous[block_id]
                        old_id = assigned.get(target_pos)
                        assigned[target_pos] = block_id
                        if old_id is None:
                            return
                        block_id = old_id
                for occupied_pos in allowed_positions[block_id]:
                    if (assigned.get(occupied_pos) == block_id
                            and occupied_pos not in seen_positions):
                        seen_positions.add(occupied_pos)
                        queue.append(occupied_pos)

    for pos in positions:
        if pos not in assigned:
            fill_position(pos)

    return [(pos, assigned[pos]) for pos in positions if pos in assigned]
