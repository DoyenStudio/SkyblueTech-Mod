# 通用 RF 能源端点

本接口只处理整数 RF 电量，不处理热量，也不包含任何特定附属包的识别逻辑。
服务端导入 `server.export.energy`；`API_VERSION == 1`，`IsReady()` 表示业务完成加载。
支持能力 `energy_endpoints`、`extraction_settlement`、`storage_identity`。

## 接入与查询

- `RegisterEnergyProvider(owner, block_ids, resolver)`：唯一命名空间 owner、静态方块 ID 集合、处理器查询回调；返回撤销 token。重复 owner 或重复方块拒绝注册。
- `UnregisterEnergyProvider(token)`：撤销本方登记，返回是否找到。世界退出时撤销；重新进入后重新登记。
- `GetEnergyHandler(position, dimension, face, native_only=False, period_ticks=5)`：查询已加载端点，不加载区块。face 为目标被接触的面，Facing 0～5；native_only 排除外部提供者。
- `RefreshEnergyConnections(position, dimension)`：端点上线、下线或面配置变化后刷新管网缓存，保留玩家手动断开的连接。调用方负责对已加载端点通知，不应每 tick 无条件调用。
- resolver 的参数为 `(position, dimension, face)`，返回 RF 处理器或 None。外部提供者自行检查实例、朝向、世界生命周期；其存档仍由自己维护。

原生电缆识别和邻接输出均使用通用处理器；不需要把外部方块注册为蔚蓝机器。
提供者异常会被停用，本局重新登记前不再调用；尚未确定接收结果的电量不会退款后重新发放。

## 处理器与结算

处理器实现 `canReceive()`、`canExtract()`、`insert(amount)` 和 `prepareExtract(amount)`。
前两项为无写入的方向能力查询，不要求储能非空或未满。
insert 返回实际接收量；prepareExtract 从来源扣出最多 amount，返回票据或 None。
外部处理器可实现 `acceptsActivePush()`（默认 True），返回 False 时原生邻接输出不主动推送，电缆运输不受此策略影响。
用于接收方已经主动拉取该连接的情况，避免两个调度器重复交换。
原生处理器另有 `isActiveOutput()`，说明此面是否由原生邻接输出驱动，外部调度器据此避免重复抽取。

可选的 `storageIdentity()` 返回本局有效的共享储能标识；未实现视为未知，不应持久化或解析。
原生多方块端口使用控制器标识；外部提供者应为同一储能的不同端口返回相同值。
`SameEnergyStorage(source, target)` 比较这些标识。电缆与 TransferEnergy 跳过同一储能，避免自我回送耗尽运输额度。

票据公开 `amount` 和 `finish(accepted)`：退回 amount - accepted；相同结算幂等，不同结算拒绝。
票据只能在同一服务端调用链里使用，不跨 tick、异步或 RPC。
原生处理器调用原机器的 AddPower／TakeoutPower／GivebackPower，保留储能开关、转发和统计副作用。
多方块转发源在未结束抽取期间不能重入。

`TransferEnergy(source, target, amount)` 完成抽取、插入与实际量结算，返回实际传输 RF。
接收方抛异常时按已经交出整笔处理，不盲目退款；来源失效时不把余量退到新实例。
这不是跨进程事务，也不保证两侧存档原子性。外部实现不得在未持有电量时承诺抽取成功。

数量必须为非负整数，不接受 bool 或浮点参数（包括 100.0），最大 9223372036854775807；仍需符合具体机器的存档范围。
接口不承诺通用储能快照或模拟写入：转发口、能量物品矩阵和创造接收器未必具有独立标量库存，不能用 store_rf 推断其实际接受量。

## 周期与兼容

原生线缆继续每 5 tick 驱动，共用原网络的 transfer_speed × 5 预算。
period_ticks 只接受 1 或 5；外部逐 tick 调度传 1，线缆传 5。
机器可覆写 `GetEnergyTransferLimits(period_ticks)` 返回本次输入／输出上限，None 表示不增加限制。
普通机器只开放整数可用空间与存量，不足一 RF 的部分留在原端；原生存档中的整数浮点值仅在内部归一化。
能量立方与电池矩阵额外按功率及周期限制，结构端口转发控制器限制，创造接收器和中继植物显式开放其特殊接收能力。
这些是单次限制，不新建所有调用方共享的全局 tick 配额。外部提供者保留自己的单次限制，不自动乘 5。

不同电网仍独立，不通过本接口合并拓扑。不安装任何外部提供者时，原生机器保持原存取路径及存档格式。

## 验证

只在游戏服务端执行：

```python
from skybluetech_scripts.skybluetech.server.export.energy_selftest import run
_result = run()
```

用独立替身端点检查部分接收、拒收、空源、周期限制、重入保护及登记撤销，不依赖任何外部模组，不修改世界方块。
游戏内通用自检现覆盖 10 组场景，并检查实际电缆运输回调不会将能量送回同一储能的其他端口。
实体锡电缆原生线路已验证每周期运输 1920 RF；外部端点的六面运输、满容、开关和功率统计已验证。
八段电缆环路运行 100 个周期，总电量保持 140000；正常 tick 自动运输验证 3200 单位源电量全部进入目标。
共享储能去重是通用机制，接口与自检不识别任何特定外部模组。

保存后的引擎重载恢复已验证。真正的区块卸载未能触发：玩家远离后测试区仍被引擎保持加载，不能记为通过。
远端多人缺少第二客户端；外部模组缺席及不同加载顺序的真实安装组合仍待验证。
本轮临时测试方块与导线已清理。
