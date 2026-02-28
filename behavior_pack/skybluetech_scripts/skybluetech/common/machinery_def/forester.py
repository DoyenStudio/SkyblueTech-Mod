# coding=utf-8
#
def isLog(block_id):
    # type: (str) -> bool
    # TODO: 使用此方法判定方块是否为原木是不安全的, 考虑到一些模组的原木的命名
    #       方式比较奇特, 不一定符合此命名规则。因为原版的 log 标签没有覆盖所
    #       有原木如樱花木, 所以暂不使用。
    return block_id.endswith("log")

def isLeave(block_id):
    # type: (str) -> bool
    # TODO: 使用此方法判定方块是否为树叶是不安全的, 考虑到一些模组的树叶的命名
    #       方式比较奇特, 不一定符合此命名规则。如果 leave 标签被加入, 建议使
    #       用 leave 标签。
    return block_id.strip("s").endswith("leave")

def getSaplingId(log_block_id):
    # type: (str) -> str
    # TODO: 很简陋的获取树木对应树苗的方法。
    return log_block_id.replace("log", "sapling")

