# coding=utf-8
"""不接触机器状态的配方数量分配；固定槽需求使用单元素 slots tuple。"""


def _eligible_slots(requirements, capacities, accepts):
    result = []
    for index, (slots, _amount) in enumerate(requirements):
        eligible = []
        seen = set()
        for slot in slots:
            if slot not in seen and slot in capacities and accepts(index, slot):
                eligible.append(slot)
                seen.add(slot)
        result.append(eligible)
    return result


def _quantity_tolerance(amount):
    # 只忽略浮点拆分的微小残差；不吞掉整数短缺或本身很小的真实需求。
    return min(1e-9, amount * 1e-9)


def allocate(requirements, capacities, accepts):
    # type: (list, dict, object) -> list | None
    """
    返回与 requirements 同序的 slot -> amount 分配，无法满足时返回 None。

    零数量输入只检查允许槽中存在可接受且容量大于零的库存，不占用数量；
    调用方仍需让 accepts 检查物品/流体身份。此检查不要求加工后保留库存。
    """
    eligible = _eligible_slots(requirements, capacities, accepts)
    for index, (_slots, amount) in enumerate(requirements):
        if amount == 0 and not any(
            capacities[slot] > 0 for slot in eligible[index]
        ):
            return None
    return _max_flow(requirements, capacities, eligible)


def _add_edge(graph, start, end, capacity):
    forward = [end, len(graph[end]), capacity]
    reverse = [start, len(graph[start]), 0]
    graph[start].append(forward)
    graph[end].append(reverse)
    return forward


def _max_flow(requirements, capacities, eligible):
    """源 -> 每条需求 -> 可用槽 -> 汇；反向边允许撤回先前的分配。"""
    result = [{} for _requirement in requirements]
    usable = [
        [slot for slot in slots if capacities[slot] > 0]
        for slots in eligible
    ]
    positive = [
        index for index, (_slots, amount) in enumerate(requirements) if amount > 0
    ]
    if any(not usable[index] for index in positive):
        return None

    # 普通固定槽配方无需建图；重叠的单槽需求仍共用一份剩余容量。
    if all(len(usable[index]) == 1 for index in positive):
        remaining = dict(capacities)
        for index in positive:
            slot = usable[index][0]
            amount = requirements[index][1]
            if remaining[slot] < amount:
                if amount - remaining[slot] > _quantity_tolerance(amount):
                    return None
                # 返回槽内实际数量，容差不能变成额外库存或输出容量。
                amount = remaining[slot]
            remaining[slot] -= amount
            result[index][slot] = amount
        return result

    slot_nodes = {}
    for slots in usable:
        for slot in slots:
            if slot not in slot_nodes:
                slot_nodes[slot] = 1 + len(requirements) + len(slot_nodes)
    sink = 1 + len(requirements) + len(slot_nodes)
    graph = [[] for _node in range(sink + 1)]
    requirement_edges = [[] for _requirement in requirements]
    for index in positive:
        amount = requirements[index][1]
        _add_edge(graph, 0, index + 1, amount)
        for slot in usable[index]:
            edge = _add_edge(graph, index + 1, slot_nodes[slot], amount)
            requirement_edges[index].append((slot, edge))
    for slot, node in slot_nodes.items():
        _add_edge(graph, node, sink, capacities[slot])

    # 小图使用 BFS 增广。保留原数值类型，不把流体数量转成整数。
    while True:
        parents = [None] * len(graph)
        parents[0] = (0, 0)
        queue = [0]
        head = 0
        while head < len(queue) and parents[sink] is None:
            node = queue[head]
            head += 1
            for edge_index, edge in enumerate(graph[node]):
                target, _reverse_index, capacity = edge
                if capacity > 0 and parents[target] is None:
                    parents[target] = (node, edge_index)
                    queue.append(target)
                    if target == sink:
                        break
        if parents[sink] is None:
            break

        amount = None
        node = sink
        while node:
            previous, edge_index = parents[node]
            capacity = graph[previous][edge_index][2]
            amount = capacity if amount is None else min(amount, capacity)
            node = previous
        node = sink
        while node:
            previous, edge_index = parents[node]
            edge = graph[previous][edge_index]
            edge[2] -= amount
            graph[node][edge[1]][2] += amount
            node = previous

    if any(
        edge[2] > _quantity_tolerance(requirements[edge[0] - 1][1])
        for edge in graph[0]
    ):
        return None
    for index, edges in enumerate(requirement_edges):
        for slot, edge in edges:
            # 反向边就是实际流量，避免用原容量减残量丢失小数精度。
            amount = graph[edge[0]][edge[1]][2]
            if amount > 0:
                result[index][slot] = amount
    return result


def allocate_outputs(
    requirements, capacities, accepts, identities, empty_slots, empty_capacities=None
):
    # type: (list, dict, object, list, object, dict | None) -> list | None
    """
    分配产出；空槽最多接收一种 identity，已占用槽由 accepts 限制身份。

    empty_capacities 可按 (slot, identity) 指定空槽容量，缺键使用 capacities。
    未约束空槽先用可入身份的最大容量，遇到身份冲突或容量不足才回溯。
    零数量产物直接返回空分配；概率应由调用方每原条目只计算一次。
    """
    eligible = _eligible_slots(requirements, capacities, accepts)
    empty_slots = set(empty_slots)
    identity_values = []
    identity_indices = []
    for identity in identities:
        try:
            index = identity_values.index(identity)
        except ValueError:
            index = len(identity_values)
            identity_values.append(identity)
        identity_indices.append(index)

    def empty_capacity(slot, identity_index):
        if empty_capacities is None:
            return capacities[slot]
        return empty_capacities.get(
            (slot, identity_values[identity_index]), capacities[slot]
        )

    candidates = {}
    for index, (_slots, amount) in enumerate(requirements):
        if amount <= 0:
            continue
        identity_index = identity_indices[index]
        for slot in eligible[index]:
            if slot in empty_slots and empty_capacity(slot, identity_index) > 0:
                choices = candidates.setdefault(slot, [])
                if identity_index not in choices:
                    choices.append(identity_index)

    relaxed_capacities = dict(capacities)
    for slot in empty_slots:
        if slot in capacities:
            choices = candidates.get(slot, [])
            relaxed_capacities[slot] = max(
                empty_capacity(slot, identity_index) for identity_index in choices
            ) if choices else 0
    slot_indices = {slot: index for index, slot in enumerate(candidates)}
    failed = set()

    def search(bindings):
        state = tuple(sorted(
            (slot_indices[slot], identity_index)
            for slot, identity_index in bindings.items()
        ))
        if state in failed:
            return None
        current_capacities = dict(relaxed_capacities)
        for slot, identity_index in bindings.items():
            current_capacities[slot] = empty_capacity(slot, identity_index)
        current_eligible = [
            [slot for slot in slots if (
                slot not in bindings or bindings[slot] == identity_indices[index]
            )]
            for index, slots in enumerate(eligible)
        ]
        allocation = _max_flow(requirements, current_capacities, current_eligible)
        if allocation is None:
            failed.add(state)
            return None

        used = {}
        for index, assignments in enumerate(allocation):
            for slot, amount in assignments.items():
                if slot in empty_slots and slot not in bindings:
                    amounts = used.setdefault(slot, {})
                    identity_index = identity_indices[index]
                    amounts[identity_index] = amounts.get(identity_index, 0) + amount
        conflict = None
        for slot, amounts in used.items():
            if len(amounts) > 1:
                conflict = slot
                break
            identity_index = next(iter(amounts))
            if amounts[identity_index] > empty_capacity(slot, identity_index):
                conflict = slot
                break
        if conflict is None:
            return allocation

        # 必须尝试所有可入身份，不能只试当前流入的两种：其他身份也可能
        # 需要占用此槽，才能让余下需求绕到别处。每次分支重新最大流剪枝。
        for identity_index in candidates[conflict]:
            next_bindings = dict(bindings)
            next_bindings[conflict] = identity_index
            result = search(next_bindings)
            if result is not None:
                return result
        failed.add(state)
        return None

    return search({})
