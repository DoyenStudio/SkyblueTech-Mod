# HeatCtrl 热机控制基类

热机机器类, 表示产热或吸热的机器。

派生自 `BaseMachine` 基类。

- 你需要额外创建以下空方法并加上 `@SuperExecutorMeta.execute_super` 装饰器：
    - `OnTicking`

## 单位约定

本类的热值一律为**绝对热值** `H`(RF), 直接对应内能, `0K` 即 `H = 0`：

```
H = C * T        # C 为本机热容 heat_capacity, 默认 Thermal.HEAT_CAPACITY
T = H / C
```

环境温度 300K 对应 `H = Thermal.ENV_HEAT = 300 RF`。新放置的机器热值缺省即取该值。
温度的换算一律走 `Thermal.GetKelvin` / `Thermal.GetHeat`, 不要自行加减 300; 换算与
换热时都要把本机的 `heat_capacity` 传进去(见下)。

### 热容

`heat_capacity` 是**按机器覆写**的类属性, 默认 `Thermal.HEAT_CAPACITY`(1.0 RF/K)。
取默认值时 `H` 与 `T` 数值相同, 行为与过去一致; 覆写成更大的值, 相当于给这台机器加了
一大团需要加热/冷却的物质 —— 同样的温区要搬走更多热量, 所以更慢、也更费电。全局常量
`Thermal.HEAT_CAPACITY` 不动, 因此**只影响覆写过的那一台机器**(典型用法见
`VacuumFreezer` 与 `DistillationChamber`, 以及 `common/machinery_def/` 下各自对应的
`CHAMBER_HEAT_CAPACITY`)。

覆写热容时注意两点:

- 各子类里以 RF/t 计的**速率类常量**(产热功率、移热速率上限等)也是热量, 会随热容一起
  被放大, 要一起检查; 否则温度变化速度会跟着变慢。
- 落盘的 `K_HEAT_VALUE` 存的是**参考热容下的热值**: 默认热容时它既是绝对热值、也是
  温度(K); 覆写过热容的机器存的仍是温度, 乘 `heat_capacity` 才是参与计算的绝对热值。
  这样客户端 UI 读数与旧存档都不会因为改热容而错位。

## 类属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| heat_power | float | 产热功率, 正值代表加热, 负值代表吸热 |
| spread_heat | bool | 是否扩散热量, 默认为 False |
| max_heat_value | float | 本机相对环境温度的温升上限, 默认为 600.0(即上限 900K) |
| heat_capacity | float | 本机热容, 单位 RF/K, 默认 `Thermal.HEAT_CAPACITY`(1.0); 覆写它可只把这一台机器改"重" |
| WORK_INTERVAL | int | 热力结算间隔, 默认为 5 tick; 同时作为传热的 dt |
| env_conductance | float | 环境散热系数, 默认为 0.002, 单位 RF/(tick·K) |
| electric_per_heat | float | 电→热单价, 默认为全局标准 `Thermal.ELECTRIC_PER_HEAT`(10 RF电/RF热); 覆写它可只改这一台机器的电费 |

## 实例属性
| 属性名 | 类型 | 说明 |
| --- | --- | --- |
| heat_value | (property) float | 本机当前绝对热值, 单位 RF |
| kelvin | (property, 只读) float | 本机当前温度, 单位 K, 由热值换算 |
| max_kelvin | (property, 只读) float | 本机温度上限, 单位 K, 等于 `Thermal.STD_ENV_KELVIN + max_heat_value` |
| heat_target_kelvin | (property, 只读) float | 产热的目标温度, 单位 K, 默认为 `max_kelvin`; 子类可覆写 |

## 基类方法
```python
def SetOutputHeatPower(self, power: float) -> None
```
设置热机输出功率。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| power | float | 新的热功率值 |

```python
def HeatFromElectric(self, rf: float) -> float
```
按本机单价把 RF 电换算成买得到的热量(RF)。

```python
def ElectricCostOf(self, heat: float) -> float
```
按本机单价把热量(RF)换算成电费(RF)。

```python
def OnHeatWork(self) -> None
```
热力结算前的钩子, 每 `WORK_INTERVAL` tick 调用一次, 基类实现为空。

子类覆写它来按本周期的实际耗能调整 `heat_power`。因为它在产热/热扩散**之前**执行,
本周期设置的热功率本周期即生效, 不存在"先产热后结算"的空窗。

`heat_power` 默认为 0(类属性), 所以不覆写本钩子的子类(如 `DistillationChamber`)始终不产热,
而是自己直接改 `heat_value`。典型实现见 `ElectricHeater`: 停机、到温、电量不足时置 0,
否则按 `electric_per_heat` 把设定功率换算成本周期的产热功率, 并在**钳位之前**按设定
功率全额扣电 —— 温差不够时进不来的那部分热量就是白烧, 这是有意的设计。

> 覆写 `OnHeatWork` 时注意: 机器停机(`IsActive()` 为 False)期间本方法**仍然会被调用**。
> 若子类只在活跃时检查电量, "能量不足"停机旗就没有机会解除(解旗的唯一时机会只剩充电那一瞬间),
> 机器会永远醒不过来。

## 热力计算

每个 `WORK_INTERVAL` tick 结算一次, 顺序为: **`OnHeatWork`(子类调整 `heat_power`)
→ 产热/吸热 → 环境散热 → 热扩散**。

本类不自带热力学公式, 全部委托给 `phys_math.Thermal`:

- 产热/吸热: `Thermal.HeatToTarget(heat_value, target_T, max_power=abs(heat_power), capacity=heat_capacity)`
    - `target_T`: 产热时取 `heat_target_kelvin`(默认 `max_kelvin`), 吸热时取绝对零度
    - 到达目标温度后热值不再变化; 机器未活跃或 `heat_power == 0` 时不结算
    - `HeatToTarget` 会把单周期产热钳位在"距目标还差多少"以内, 因此天然不会过冲;
      但若产热里含有抵消散热的补偿项, 目标温度需要相应上抬, 否则补偿会被钳位吃掉
- 环境散热: `Thermal.ConductHeat(heat_value, Thermal.ENV_HEAT, conductance=env_conductance, dt=WORK_INTERVAL, capacity_hot=heat_capacity)`
    - 环境视为无穷大热库, 即牛顿冷却律 `Q = env_conductance * (T - T_env) * dt`
    - 环境那一侧按默认热容算(`ENV_HEAT` 本身就等于环境温度), 本机这一侧用
      `heat_capacity`; 判断"谁更热"要比温度, 不能直接比热值, 热容大的机器热值天然更大
    - 双向生效: 高于环境向环境排热, 低于环境从环境吸热
    - `env_conductance = 0.002` 时, 1 RF/t(`heat_power = 0.5`) 的稳态温升约 50K
    - 置 0 可关闭环境散热
- 热扩散: `Thermal.ConductHeat(H_self, H_neighbor, dt=WORK_INTERVAL, capacity_hot=heat_capacity, capacity_cold=邻居.heat_capacity)`
    - 逐个邻居结算, 每个邻居传热后的热值立即作为下一个邻居的起点
    - 只从高温侧流向低温侧, 不产出 RF
    - 方向由**温度**判断, 不是比热值: 热容不同的两台机器, 热值大小与温度高低并不一致,
      比热值会让热容大的机器永远收不到热
- 电费: 加热侧按全局标准单价 `Thermal.ELECTRIC_PER_HEAT`(经 `electric_per_heat`)换算,
  制冷侧按温度相关的 `Thermal.CoolElectricPerHeat`; 两者在 `Thermal.COOL_REFERENCE_KELVIN`
  上相等, 也就是同一个"电与热互换"的标准量

> 注意: 环境散热是机器唯一的自降温通道。若把 `env_conductance` 置 0 且没有子类的主动
> 降温逻辑(如 `VacuumFreezer.freeze`), 机器只会被加热, 永远不会回落到环境温度。
