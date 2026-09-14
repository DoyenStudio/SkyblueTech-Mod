# Thermal 热力学模块设计文档

> 用于 Minecraft Java 版科技模组的热力学计算模块。运行环境 Python 2.7，类型注释使用 Python 3 风格仅供 IDE 提示。核心目标：模拟机器内能（热值）变化、热交换做功、主动冷却，遵循理想热力学规律。

---

## 1. 前置概念

| 名称 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 绝对热值 | `H` | RF | 机器内能，绝对值，0K 对应 `H = 0` |
| 开尔文温度 | `T` | K | 绝对温度，只读，由 `H` 换算 |
| 环境温度 | `T_env` | K | 常量 300K |
| 环境热值 | `H_env` | RF | 由 `T_env` 换算 |
| 热容 | `C` | RF/K | 常量，默认 1.0 |

### 换算关系

```
H = C * T
T = H / C
```

默认 `C = 1.0` 时，数值上 `H == T`，单位不同。环境 300K 对应 `H_env = 300 RF`。

### 物理假设

- 所有物体均为理想热源，无热容随温度变化。
- 无热量流失、挥发、辐射。
- 热交换遵循理想卡诺循环效率。
- 主动冷却为理想制冷机。
- 机器温度高于环境时，向环境排热不耗功；低于环境时，需要制冷机耗功。

---

## 2. 常量表

| 常量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `STD_ENV_KELVIN` | float | 300.0 | 标准环境温度，单位 K |
| `HEAT_CAPACITY` | float | 1.0 | 默认热容，单位 RF/K；各函数可用 `capacity=` 覆写，单台机器可以更"重" |
| `ENV_HEAT` | float | 300.0 | 环境温度对应热值，单位 RF |
| `MIN_HEAT` | float | 1e-3 | 最小热值，防止 0K 除零 |
| `EPS` | float | 1e-9 | 通用极小值，防止除零 |
| `MAX_HEAT_POWER` | float | 100.0 | 加热/移热最大功率，RF/t |
| `MAX_COOL_POWER` | float | 100.0 | 主动冷却最大移热速率，RF/t |
| `THERMAL_CONDUCTANCE` | float | 0.1 | 热交换系数，RF/(tick·K) |
| `ELECTRIC_PER_HEAT` | float | 10.0 | 电→热单价，RF电/RF热；全包电热转换的标准量 |
| `COOL_REFERENCE_KELVIN` | float | 80.0 | 制冷参照温度，K；电与热两个方向的单价在此闭合 |
| `COOL_REFERENCE_COP` | float | 0.1 | 制冷参照 COP，等于 `1 / ELECTRIC_PER_HEAT` |

---

## 3. 结果数据类

所有多返回值函数使用嵌套数据类，不使用 dict 或裸 tuple。

### `Thermal.HeatToTargetResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `required_power` | float | 理论所需功率，RF/t，正=加热，负=移热 |
| `actual_power` | float | 本 tick 实际执行功率，RF/t |
| `delta_heat` | float | 本 tick 热值变化量，RF，正=增，负=减 |
| `H_next` | float | 下一 tick 绝对热值，RF |

### `Thermal.ExchangeCarnotResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `H_hot_next` | float | 热物体下一 tick 绝对热值，RF |
| `H_cold_next` | float | 机器下一 tick 绝对热值，RF |
| `rf_out` | float | 本 tick 产出 RF |

### `Thermal.ActiveCoolResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `H_next` | float | 下一 tick 绝对热值，RF |
| `Q_removed` | float | 本 tick 减少热量，RF |
| `energy_used` | float | 本 tick 消耗 RF，可能为 `inf` |

### `Thermal.TickMachineResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `H_next` | float | 机器下一 tick 绝对热值，RF |
| `hot_object_H_next` | float\|None | 热物体下一 tick 热值，无则 None |
| `rf_out` | float | 本 tick 热交换产出 RF |
| `energy_used` | float | 本 tick 温度控制消耗 RF |

---

## 4. 函数清单

### 4.1 换算函数

#### `NormalizeCapacity(capacity) -> float`

归一化热容: 传 `None` 取全局默认 `HEAT_CAPACITY`, 否则取传入值。下面所有 `capacity`
/ `capacity_hot` / `capacity_cold` 参数都按这个规则解析。

```
C = HEAT_CAPACITY if capacity is None else capacity
```

#### `GetKelvin(heat_value, capacity=None) -> float`

绝对热值转开尔文温度。

```
T = H / capacity
```

#### `GetHeat(kelvin, capacity=None) -> float`

开尔文温度转绝对热值。

```
H = capacity * kelvin
```

#### `Clamp(x, lo, hi) -> float`

将数值限制在 `[lo, hi]` 区间。

#### `HeatFromElectric(rf, electric_per_heat=None) -> float`

把电费换算成按标准单价买得到的热量。`electric_per_heat` 默认取 `ELECTRIC_PER_HEAT`。

```
Q = rf / electric_per_heat
```

#### `ElectricCostOfHeat(heat, electric_per_heat=None) -> float`

把热量换算成电费，即 `HeatFromElectric` 的逆运算。

```
W = heat * electric_per_heat
```

#### `CoolCOP(T_body, T_hot=None, eta=1.0, approach=0.0) -> float`

制冷机在仓温处的局部卡诺 COP：每 1 RF 电搬走多少 RF 热，单价即它的倒数。
`T_hot` 默认环境温度；高于环境温度的一段不耗功（返回 `inf`）；蒸发温度趋近绝对零度时
COP 趋近 0，电费趋于无穷。总电费沿温区积分见 `ActiveCool`。

```
COP = eta * T_evap / (T_hot - T_evap),  T_evap = T_body - approach
```

#### `CoolElectricPerHeat(T_body, T_hot=None, eta=1.0, approach=0.0) -> float`

制冷的单价：在仓温处搬走 1 RF 热量要花多少 RF 电，即 `1 / CoolCOP(...)`。与加热侧的
`ELECTRIC_PER_HEAT` 同量纲，两者在 `COOL_REFERENCE_KELVIN` 上相等。

---

### 4.2 功能 1：加热到目标温度

#### `HeatToTarget(H, target_T, max_power=None, dt=1.0, capacity=None) -> HeatToTargetResult`

**用途**：给定期望温度和当前热值，计算所需功率及单 tick 内热值变化。

**公式**：

```
H_target     = C * target_T
delta_needed = H_target - H
delta_heat   = clamp(delta_needed, -max_power*dt, max_power*dt)
actual_power = delta_heat / dt
H_next       = H + delta_heat
```

**参数**：

- `H`：当前绝对热值（RF）
- `target_T`：目标开尔文温度（K）
- `max_power`：最大功率限制（RF/t），默认 `MAX_HEAT_POWER`
- `dt`：时间步长（tick），默认 1.0
- `capacity`：热容（RF/K），默认 `HEAT_CAPACITY`

**返回**：`HeatToTargetResult`

**特点**：

- 允许负功率（主动移热），由 `max_power` 双向限制。
- 若只想加热，调用方可自行过滤 `delta_heat < 0`。

---

### 4.3 功能 2：热交换做功

#### `ExchangeCarnot(H_hot, H_cold, conductance=None, dt=1.0, capacity_hot=None, capacity_cold=None) -> ExchangeCarnotResult`

**用途**：热物体与机器进行理想卡诺热交换，机器对外做功。

**前置条件**：`T_hot > T_cold`（两侧热容可以不同，所以要比温度而不是比热值）。

**公式**：

```
T_hot  = H_hot / C_hot
T_cold = H_cold / C_cold
dT     = T_hot - T_cold

# 热导驱动
Q_hot_want  = conductance * dT * dt

# 防温度交叉（交换后热端不低于冷端，取两端刚好等温的交换量；
# 两侧热容相同时退化成 (H_hot - H_cold) * H_hot / (H_hot + H_cold)）
Q_hot_limit = dT * C_hot * C_cold * T_hot / (C_cold * T_hot + C_hot * T_cold)
Q_hot       = clamp(Q_hot_want, 0, Q_hot_limit)

# 理想卡诺关系
Q_cold = Q_hot * (T_cold / T_hot)
W      = Q_hot - Q_cold

H_hot_next  = H_hot  - Q_hot
H_cold_next = H_cold + Q_cold
```

**参数**：

- `H_hot`：热物体绝对热值（RF）
- `H_cold`：机器绝对热值（RF）
- `conductance`：热交换系数（RF/(tick·K)），默认 `THERMAL_CONDUCTANCE`
- `dt`：时间步长（tick）
- `capacity_hot` / `capacity_cold`：两侧热容（RF/K），默认 `HEAT_CAPACITY`

**返回**：`ExchangeCarnotResult`，`rf_out = W`

**边界情况**：若 `T_hot <= T_cold` 或任一低于 `MIN_HEAT`，返回原值，`rf_out = 0`。

---

### 4.4 功能 3：被动热传导

#### `ConductHeat(H_hot, H_cold, conductance=None, dt=1.0, capacity_hot=None, capacity_cold=None) -> ConductHeatResult`

**用途**：两个物体之间纯热传导，不做功、不产出 RF，只让两侧温度趋近。机器的环境散热
与相邻机器之间的热扩散都走它（见 `HeatCtrl._exchange_with_env` / `HeatCtrl.share_heat`）。

**前置条件**：`T_hot > T_cold`，其中 `T = H / 对应热容`。两侧热容可以不同，所以**一律比
温度、不比热值**：热容大的机器在 300K 就有几百 RF 热值，比热值会把方向判反，结果是重
机器永远收不到热。

```
dT  = T_hot - T_cold
Q   = min(conductance * dT * dt, (C_cold * H_hot - C_hot * H_cold) / (C_hot + C_cold))
H_hot_next  = H_hot  - Q
H_cold_next = H_cold + Q
```

第二个上限就是"传到两侧等温为止"的平衡点，所以单次调用不会过冲。

**参数**：
- `H_hot` / `H_cold`：两侧绝对热值（RF）
- `conductance`：热交换系数（RF/(tick·K)），默认 `THERMAL_CONDUCTANCE`
- `dt`：时间步长（tick）
- `capacity_hot` / `capacity_cold`：两侧热容（RF/K），默认 `HEAT_CAPACITY`

**返回**：`ConductHeatResult`，`Q_transferred = Q`

**边界情况**：若 `T_hot <= T_cold` 或任一温度低于 `MIN_HEAT`，返回原值，`Q_transferred = 0`。

---

### 4.5 功能 4：主动耗能降温

#### `ActiveCool(H, target_T, max_cool=None, dt=1.0, ..., capacity=None) -> ActiveCoolResult`

**用途**：机器消耗能量自降温到目标温度。

**公式**：

```
H_target      = C * target_T
Q_remove      = max(0, H - H_target)
Q_remove_tick = min(Q_remove, max_cool * dt)

if T > T_env:
    energy_used = 0            # 向环境排热，不耗功
else:
    COP = H / (H_env - H)      # 理想制冷机
    energy_used = Q_remove_tick / COP
```

**参数**：

- `H`：当前绝对热值（RF）
- `target_T`：目标开尔文温度（K）
- `max_cool`：最大移热速率（RF/t），默认 `MAX_COOL_POWER`
- `dt`：时间步长（tick）
- `capacity`：被冷却物的热容（RF/K），默认 `HEAT_CAPACITY`；热容越大，同样的降温幅度
  要搬走更多热量，也就更费电

**返回**：`ActiveCoolResult`

**边界情况**：

- `H` 已低于目标对应热值：不做任何事，`Q_removed = 0`，`energy_used = 0`。
- `H <= MIN_HEAT` 且需要制冷：`energy_used = float("inf")`。

**物理注释**：真实制冷机 COP 为 `T_cold / (T_hot - T_cold)`。此处 `T_cold = T`（机器），`T_hot = T_env = 300K`。用绝对热值表达即 `COP = H / (H_env - H)`。

---

### 4.6 单 tick 统一调度

#### `TickMachine(H, target_T=None, hot_object_H=None, capacity=None) -> TickMachineResult`

**用途**：在单个 tick 内统一处理热交换做功、主动降温和加热到目标温度。

**执行顺序**：

1. 若提供 `hot_object_H`，先执行 `ExchangeCarnot`，产出 RF。
2. 若提供 `target_T`：
   - 当前温度 > 目标温度 → `ActiveCool`
   - 当前温度 ≤ 目标温度 → `HeatToTarget`

**参数**：

- `H`：机器当前绝对热值（RF）
- `target_T`：目标温度（K），None 表示不控温
- `hot_object_H`：热物体热值（RF），None 表示无热源
- `capacity`：本机热容（RF/K），默认 `HEAT_CAPACITY`

**返回**：`TickMachineResult`

**注意**：`energy_used` 在加热分支只取正数部分（`max(0, delta_heat)`），因为加热是"消耗 RF 输入"，不是产热。

---

## 5. 调用示例

```python
H = 300.0  # 300K 环境热值

# 加热到 500K
res = Thermal.HeatToTarget(H, 500.0)
print res.H_next, res.required_power, res.delta_heat

# 热物体 600 RF 与机器 300 RF 热交换
ex = Thermal.ExchangeCarnot(600.0, 300.0)
print ex.H_hot_next, ex.H_cold_next, ex.rf_out

# 从 500 RF 主动降到 250K
cool = Thermal.ActiveCool(500.0, 250.0)
print cool.H_next, cool.Q_removed, cool.energy_used

# 单 tick 综合调度
tick = Thermal.TickMachine(300.0, target_T=500.0, hot_object_H=600.0)
print tick.H_next, tick.hot_object_H_next, tick.rf_out, tick.energy_used
```

---

## 6. 待细化 / 未来扩展点

以下方向可供 Codex 继续细化，按优先级排列：

### 6.1 物理模型扩展

- [x] 支持不同机器不同 `HEAT_CAPACITY`：各函数接受 `capacity` / `capacity_hot` /
  `capacity_cold`（`None` 取全局默认），`HeatCtrl.heat_capacity` 按机器覆写。
- [ ] 支持环境温度可变（如不同维度 280K / 300K / 350K）。
- [ ] 引入非理想卡诺效率因子 `EFFICIENCY_RATIO ∈ (0, 1]`，让 `W = η_carnot * EFFICIENCY_RATIO * Q_hot`。
- [ ] 引入辐射散热（`P_rad ∝ T^4`）作为被动降温通道。
- [ ] 支持相变储热（潜热），使 `C` 在特定温区非线性。

### 6.2 数值稳健性

- [ ] `H_hot + H_cold` 在小热值下是否会溢出/精度丢失。
- [ ] `Q_hot_limit` 在 `H_hot ≈ H_cold` 时的数值行为。
- [ ] `ActiveCool` 在 `H_env - H → 0` 附近时 `energy_used` 爆炸，需要上限截断策略。
- [ ] 大 `dt` 下是否需要子步（substep）积分以保证稳定。

### 6.3 多机器耦合

- [ ] 热网的批量结算顺序（避免依赖顺序导致能量不守恒）。
- [ ] 机器之间的被动热传导（无做功，仅热平衡）。
- [ ] 热缓存（thermal buffer）机制。

### 6.4 与 Minecraft 模组集成

- [ ] 与 RF API（如 Redstone Flux / Forge Energy）对接。
- [ ] NBT 序列化 `H` 到 ItemStack / TileEntity。
- [ ] 温度超限警告 / 爆炸机制接口。
- [ ] 用于 GUI 的温度与热值同步字段。

### 6.5 API 层面

- [x] `HEAT_CAPACITY` 已可作为参数逐次传入；尚未引入 `ThermalBody` 实例类（当前由
  `HeatCtrl.heat_capacity` 这个类属性承担"每台机器一个热容"的角色）。
- [ ] 结果类支持 `__slots__` 减少开销（Minecraft tick 内高频调用）。
- [ ] 提供 `__all__` 与模块级便捷别名。
- [ ] 增加单元测试覆盖边界：`H_hot == H_cold`、`H = 0`、`target_T < 0` 等。

### 6.6 单位与文档

- [ ] 明确 RF/t 与 RF/tick 的区别（1 tick = 0.05s）。
- [ ] 给出典型数值区间建议（如机器工作温度 300~2000K）。
- [ ] 附一张热交换方向示意图。
- [x] 电与热的换算标准（`ELECTRIC_PER_HEAT`、`COOL_REFERENCE_*`）已作为全包标准量写入
  常量表；加热与制冷两侧的单价在 `COOL_REFERENCE_KELVIN` 上闭合。
