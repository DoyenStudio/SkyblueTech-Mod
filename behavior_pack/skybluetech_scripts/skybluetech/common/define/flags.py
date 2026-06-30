def b(num):
    # type: (int) -> int
    return 1 << (num - 1)


# general
DEACTIVE_FLAG_NO_RECIPE = b(1)
DEACTIVE_FLAG_OUTPUT_FULL = b(2)
DEACTIVE_FLAG_NO_INPUT = b(3)
DEACTIVE_FLAG_STRUCTURE_BROKEN = b(4)
DEACTIVE_FLAG_STRUCTURE_BLOCK_LACK = b(5)

# appliance
DEACTIVE_FLAG_POWER_LACK = b(6)
DEACTIVE_FLAG_FLUID_NOT_MATCH = b(7)
DEACTIVE_FLAG_FLUID_FULL = b(8)

# generator
# 注意: 与 DEACTIVE_FLAG_POWER_LACK 共用同一位 b(6)。
# 一台机器要么耗电 (可能 POWER_LACK), 要么发电 (可能 POWER_FULL),
# 二者不会同时出现, 故复用同一位; 修改其一时务必同步另一处。
DEACTIVE_FLAG_POWER_FULL = b(6)

# 处于以下停机原因时不重置工作进度: 这些都是"短暂阻塞", 阻塞解除后
# 应当从原进度继续, 而非丢弃已完成的工作。
#   - 能量缓冲相关 (耗电机器能量不足 / 发电机能量已满, 同为 b(6))
#   - 输出受阻 (输出槽/缓冲已满)
PROGRESS_PRESERVING_FLAGS = (
    DEACTIVE_FLAG_POWER_LACK | DEACTIVE_FLAG_POWER_FULL | DEACTIVE_FLAG_OUTPUT_FULL
)
