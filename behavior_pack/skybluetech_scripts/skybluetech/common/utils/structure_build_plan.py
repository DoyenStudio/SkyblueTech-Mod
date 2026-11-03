# coding=utf-8
"""按可放置位置、背包库存和接口最低数量分配多方块建材。"""


def create_build_plan(candidates, available_counts, required_counts):
    # type: (list, dict[str, int], dict[str, int]) -> list[tuple]
    """返回 ``[(世界坐标, 方块 ID)]``，不修改传入的坐标、库存或缺额。

    candidates 为 ``[(坐标三元组, 按模板优先级排列的方块 ID 元组)]``；
    每个世界坐标只能出现一次。库存和最低缺额均为非负整数计数。
    先尽可能满足最低缺额并填满其余位置，再按位置顺序优先选择列表靠前的材料；
    调整时保留已满足的最低数量和已填位置，避免挤占必需材料或其允许位置。
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

    minimum_counts = {
        block_id: min(required_counts.get(block_id, 0), used_counts.get(block_id, 0))
        for block_id in capacity
    }
    fixed_positions = set()

    def prefer_block(start_pos, preferred_id):
        """试换成更靠前的材料，通过换位或剩余库存补回原材料的缺额。"""
        old_id = assigned[start_pos]
        queue = [preferred_id]
        seen = {preferred_id}
        previous = {}
        for current_id in queue:
            if current_id == old_id:
                # 找到完整调整路径后才改计划；找不到时原计划保持不变。
                assigned[start_pos] = preferred_id
                used_counts[old_id] -= 1
                used_counts[preferred_id] = used_counts.get(preferred_id, 0) + 1
                while current_id != preferred_id:
                    parent_id, move_pos = previous[current_id]
                    if move_pos is not None:
                        assigned[move_pos] = current_id
                        used_counts[parent_id] -= 1
                        used_counts[current_id] = used_counts.get(current_id, 0) + 1
                    current_id = parent_id
                return True

            if current_id is None:
                # None 连接库存余量与超出必需数量的材料，允许两者交换一份。
                moves = [
                    (block_id, None) for block_id in sorted(capacity)
                    if used_counts.get(block_id, 0) > minimum_counts[block_id]
                ]
            else:
                moves = []
                for move_pos in allowed_positions[current_id]:
                    if (move_pos in fixed_positions
                            or assigned.get(move_pos) != current_id):
                        continue
                    for block_id in options[move_pos]:
                        moves.append((block_id, move_pos))
                if used_counts.get(current_id, 0) < capacity[current_id]:
                    moves.append((None, None))
            for next_id, move_pos in moves:
                if next_id not in seen:
                    seen.add(next_id)
                    previous[next_id] = (current_id, move_pos)
                    queue.append(next_id)
        return False

    # 固定前面已选好的位置；后面的位置可换位，但不能减少必需方块或已填格数。
    # 例如两个位置均允许 [外壳, 接口] 且必须有一个接口时，优先把外壳放在前面。
    for pos in positions:
        if pos not in assigned:
            continue
        fixed_positions.add(pos)
        for block_id in options[pos]:
            if block_id == assigned[pos] or prefer_block(pos, block_id):
                break

    return [(pos, assigned[pos]) for pos in positions if pos in assigned]
