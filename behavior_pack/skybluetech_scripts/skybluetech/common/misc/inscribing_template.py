# coding=utf-8
import random
import hashlib


RAND_MASK = 33550336
# 模版图案需要同时满足：
# 1. 同一个物品在同一个世界里稳定；
# 2. 不同 world_seed 之间隔离；
# 3. 注册过的目标物品之间图案不重复，避免成型机反查错物品。
cached_graphs = {}  # type: dict[tuple[str, int], list[int]]
cached_graphs_by_seed = {}  # type: dict[int, dict[str, list[int]]]
cached_used_graphs_by_seed = {}  # type: dict[int, set[tuple[int, ...]]]


def GetTemplateRandNum(template_item_id, world_seed, salt=0):
    # type: (str, int, int) -> int
    if not isinstance(template_item_id, bytes):
        bts = template_item_id.encode("utf-8")
    else:
        bts = template_item_id
    # 保留旧逻辑的 md5 后 32 bit，salt=0 时不会无端重洗已有图案。
    h = int(hashlib.new("md5", bts).hexdigest()[-8:], base=16)
    if salt:
        # 只有发生图案碰撞时才混入 salt，重新确定性生成一个候选图案。
        salt_bts = bytes(bts) + (":%s" % salt).encode("utf-8")
        h ^= int(hashlib.new("md5", salt_bts).hexdigest()[-8:], base=16)
    return h ^ world_seed ^ RAND_MASK


def _GenerateTemplateGraph(template_item_id, world_seed, salt=0):
    # type: (str, int, int) -> list[int]
    r = random.Random()
    r.seed(GetTemplateRandNum(template_item_id, world_seed, salt))
    graph = []  # type: list[int]
    for _ in range(25):
        graph.append(r.randint(0, 7))
    return graph


def _GetRegisteredTemplateItemIds():
    # type: () -> list[str]
    # 模版图案由研究刻印、战利品掉落、成型机反查共同使用。
    # 这里收集所有“应该避让碰撞”的目标 ID，按字符串排序保证初始化顺序稳定。
    from ..machinery_def import template_assembler
    from .industrial_researching import all_researchings

    item_ids = {}
    for item_id in template_assembler.recipes.recipes_mapping:
        item_ids[item_id] = None
    for recipe in all_researchings:
        item_ids[recipe.result_item_id] = None
    return sorted(item_ids)


def _GetUniqueTemplateGraph(template_item_id, world_seed, used_graphs):
    # type: (str, int, set[tuple[int, ...]]) -> list[int]
    salt = 0
    while True:
        graph = _GenerateTemplateGraph(template_item_id, world_seed, salt)
        graph_key = tuple(graph)
        if graph_key not in used_graphs:
            used_graphs.add(graph_key)
            return graph
        # 初始种子或最终 25 格图案撞了，就加 salt 重试；图案空间很大，正常很快结束。
        salt += 1


def _InitWorldTemplateGraphs(world_seed):
    # type: (int) -> None
    if world_seed in cached_graphs_by_seed:
        return

    graphs = {}  # type: dict[str, list[int]]
    used_graphs = set()
    # 先把当前世界的注册图案整体分配完，后续单个查询才能共享同一份避让结果。
    for template_item_id in _GetRegisteredTemplateItemIds():
        graph = _GetUniqueTemplateGraph(template_item_id, world_seed, used_graphs)
        graphs[template_item_id] = graph
        cached_graphs[(template_item_id, world_seed)] = graph
    cached_graphs_by_seed[world_seed] = graphs
    cached_used_graphs_by_seed[world_seed] = used_graphs


def GetTemplateGraph(template_item_id, world_seed):
    # type: (str, int) -> list[int]
    key = (template_item_id, world_seed)
    if key in cached_graphs:
        return cached_graphs[key]

    _InitWorldTemplateGraphs(world_seed)
    if key in cached_graphs:
        return cached_graphs[key]

    used_graphs = cached_used_graphs_by_seed[world_seed]
    # 未注册 ID 仍允许生成图案（例如调试命令），但也避开当前世界已注册的图案。
    graph = _GetUniqueTemplateGraph(template_item_id, world_seed, used_graphs)
    cached_graphs[key] = graph
    return graph


K_UD_MODIFIED = "st:modified"
K_UD_TEMPLATE_GRAPH = "st:graph"
K_UI_TEMPLATE_GRAPH = "st:graph"
