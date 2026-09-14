# coding=utf-8

import math


class Thermal:
    STD_ENV_KELVIN = 300.0  # type: float
    # 标准环境温度，单位 K。

    HEAT_CAPACITY = 1.0  # type: float
    # 热容，单位 RF/K。用于在热值 H 与开尔文温度 T 之间换算：
    # H = HEAT_CAPACITY * T
    # T = H / HEAT_CAPACITY

    ENV_HEAT = HEAT_CAPACITY * STD_ENV_KELVIN  # type: float
    # 环境温度对应的绝对热值，单位 RF。
    # 默认 HEAT_CAPACITY=1.0 时，ENV_HEAT = 300.0 RF。

    MIN_HEAT = 1e-3  # type: float
    # 允许的最小热值，避免出现 0K 导致除零。

    EPS = 1e-9  # type: float
    # 通用极小值，用于避免除零。

    MAX_HEAT_POWER = 2147483647.0  # type: float
    # 加热或移热的最大功率，单位 RF/t。

    MAX_COOL_POWER = 2147483647.0  # type: float
    # 主动冷却时每 tick 最大移热速率，单位 RF/t。

    THERMAL_CONDUCTANCE = 0.1  # type: float
    # 热交换系数，单位 RF/(tick*K)。
    # 数值越大，热物体与机器之间换热越快。

    ELECTRIC_PER_HEAT = 10.0  # type: float
    # 电→热单价：每 1 RF 热量需要的 RF 电，即电热转换效率 10%。
    #
    # 这是本包电与热互换的唯一标准量，所有耗电产热的机器都按它计费（见
    # `HeatCtrl.electric_per_heat` 与 `Thermal.ElectricCostOfHeat`）。想调整个包的热力
    # 电费只改这里；单台机器想更省电或更费电，覆写它自己的单价即可。
    #
    # 制冷侧也以它为参照（见下面三个常量），即本包约定电与热在 80K 上同价。这是游戏内
    # 的换算约定，不是物理恒等式：现实里制冷永远比制热贵（`COP热 = COP冷 + 1`）。

    COOL_REFERENCE_KELVIN = 80.0  # type: float
    # 制冷参照温度，单位 K。
    #
    # 电与热两个方向的单价在这一点闭合：制冷机在这里的局部 COP 应当等于
    # `COOL_REFERENCE_COP`，也就是搬走 1 RF 热量与加热 1 RF 热量同价。各制冷机用自己
    # 的冷头效率与蒸发温差去命中它（见 `VacuumFreezer`）；偏离这个温度之后单价按卡诺
    # 曲线浮动：更冷更贵，更热更便宜。见 `CoolCOP` 与 `CoolElectricPerHeat`。

    COOL_REFERENCE_COP = 1.0 / ELECTRIC_PER_HEAT  # type: float
    # 制冷参照 COP，即 `1 / ELECTRIC_PER_HEAT`（0.1）：每 1 RF 电搬走 0.1 RF 热。

    class HeatToTargetResult:
        # type: (...) -> None
        """
        HeatToTarget 的返回结果。

        Attributes:
            required_power (float): 理论上需要的功率，单位 RF/t。
                正数表示需要加热，负数表示需要移热。
            actual_power (float): 本 tick 实际执行的功率，单位 RF/t。
            delta_heat (float): 本 tick 热值变化量，单位 RF。
                正数表示内能增加，负数表示内能减少。
            H_next (float): 下一 tick 的绝对热值，单位 RF。
        """

        def __init__(self, required_power, actual_power, delta_heat, H_next):
            # type: (float, float, float, float) -> None
            self.required_power = required_power
            self.actual_power = actual_power
            self.delta_heat = delta_heat
            self.H_next = H_next

    class ExchangeCarnotResult:
        # type: (...) -> None
        """
        ExchangeCarnot 的返回结果。

        Attributes:
            H_hot_next (float): 热物体下一 tick 的绝对热值，单位 RF。
            H_cold_next (float): 机器下一 tick 的绝对热值，单位 RF。
            rf_out (float): 本 tick 产出的 RF 值。
        """

        def __init__(self, H_hot_next, H_cold_next, rf_out):
            # type: (float, float, float) -> None
            self.H_hot_next = H_hot_next
            self.H_cold_next = H_cold_next
            self.rf_out = rf_out

    class ActiveCoolResult:
        # type: (...) -> None
        """
        ActiveCool 的返回结果。

        Attributes:
            H_next (float): 下一 tick 的绝对热值，单位 RF。
            Q_removed (float): 本 tick 减少的热量值，单位 RF。
            energy_used (float): 本 tick 消耗的 RF 能量。
                低于环境温度的部分按卡诺制冷机计费，温度越低越贵。
        """

        def __init__(self, H_next, Q_removed, energy_used):
            # type: (float, float, float) -> None
            self.H_next = H_next
            self.Q_removed = Q_removed
            self.energy_used = energy_used

    class TickMachineResult:
        # type: (...) -> None
        """
        TickMachine 的返回结果。

        Attributes:
            H_next (float): 机器下一 tick 的绝对热值，单位 RF。
            hot_object_H_next (float | None): 热物体下一 tick 的绝对热值。
                如果未提供热物体，则为 None。
            rf_out (float): 本 tick 热交换产出的 RF。
            energy_used (float): 本 tick 主动温度控制消耗的 RF。
        """

        def __init__(self, H_next, hot_object_H_next, rf_out, energy_used):
            # type: (float, float | None, float , float) -> None
            self.H_next = H_next
            self.hot_object_H_next = hot_object_H_next
            self.rf_out = rf_out
            self.energy_used = energy_used

    class ConductHeatResult:
        # type: (...) -> None
        """
        纯热传导的返回结果。

        Attributes:
            H_hot_next (float): 热物体下一 tick 的绝对热值，单位 RF。
            H_cold_next (float): 冷物体下一 tick 的绝对热值，单位 RF。
            Q_transferred (float): 本 tick 从热物体传到冷物体的热量，单位 RF。
        """

        def __init__(self, H_hot_next, H_cold_next, Q_transferred):
            # type: (float, float, float) -> None
            self.H_hot_next = H_hot_next
            self.H_cold_next = H_cold_next
            self.Q_transferred = Q_transferred

    # =========================
    # 换算
    # =========================
    @staticmethod
    def NormalizeCapacity(capacity):
        # type: (float | None) -> float
        """
        归一化热容参数: 不传(None)时使用全局默认热容 `Thermal.HEAT_CAPACITY`。

        热容与默认值不同的机器(例如真空冷却仓)可以把自己的热容传进来, 让
        "温度 <-> 热值"的换算、以及和其他物体换热时的热量分配都按它自己的热容算。
        这样只需要给这一台机器传参, 不必动全局常量, 其他机器完全不受影响。

        Args:
            capacity (float, optional): 热容，单位 RF/K。

        Returns:
            float: 归一化后的热容，单位 RF/K。
        """
        return float(Thermal.HEAT_CAPACITY if capacity is None else capacity)

    @staticmethod
    def GetKelvin(heat_value, capacity=None):
        # type: (float, float | None) -> float
        """
        将绝对热值转换为开尔文温度。

        Args:
            heat_value (float): 绝对热值，单位 RF。
            capacity (float, optional): 热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。

        Returns:
            float: 开尔文温度，单位 K。
        """
        return float(heat_value) / Thermal.NormalizeCapacity(capacity)

    @staticmethod
    def GetHeat(kelvin, capacity=None):
        # type: (float, float | None) -> float
        """
        将开尔文温度转换为绝对热值。

        Args:
            kelvin (float): 开尔文温度，单位 K。
            capacity (float, optional): 热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。

        Returns:
            float: 绝对热值，单位 RF。
        """
        return Thermal.NormalizeCapacity(capacity) * float(kelvin)

    @staticmethod
    def HeatFromElectric(rf, electric_per_heat=None):
        # type: (float, float | None) -> float
        """
        把电费换算成按标准单价买得到的热量。

        Args:
            rf (float): 电费，单位 RF。
            electric_per_heat (float, optional): 电→热单价，单位 RF电/RF热。
                默认为全局标准 `Thermal.ELECTRIC_PER_HEAT`。

        Returns:
            float: 热量，单位 RF。
        """
        if electric_per_heat is None:
            electric_per_heat = Thermal.ELECTRIC_PER_HEAT
        return float(rf) / float(electric_per_heat)

    @staticmethod
    def ElectricCostOfHeat(heat, electric_per_heat=None):
        # type: (float, float | None) -> float
        """
        把热量换算成电费，即 `HeatFromElectric` 的逆运算。

        Args:
            heat (float): 热量，单位 RF。
            electric_per_heat (float, optional): 电→热单价，单位 RF电/RF热。
                默认为全局标准 `Thermal.ELECTRIC_PER_HEAT`。

        Returns:
            float: 电费，单位 RF。
        """
        if electric_per_heat is None:
            electric_per_heat = Thermal.ELECTRIC_PER_HEAT
        return float(heat) * float(electric_per_heat)

    @staticmethod
    def CoolCOP(T_body, T_hot=None, eta=1.0, approach=0.0):
        # type: (float, float | None, float, float) -> float
        """
        制冷机在仓温 `T_body` 处的局部卡诺 COP：每 1 RF 电搬走多少 RF 热。

        单价（每搬走 1 RF 热量的电费）就是它的倒数，与加热侧的 `ELECTRIC_PER_HEAT`
        同量纲，见 `CoolElectricPerHeat`。制冷机的总电费沿温区积分，见 `ActiveCool`：

            - 冷头必须比被冷却物更冷才能吸热，蒸发温度取 `T_body - approach`；
            - `eta` 是冷头相对理想卡诺的效率折扣，取值 (0, 1]；
            - 高于环境温度的一段不耗功，返回 inf；
            - 蒸发温度趋近绝对零度时 COP 趋近 0，电费趋于无穷。

        Args:
            T_body (float): 被冷却物的温度，单位 K。
            T_hot (float, optional): 排热侧温度，单位 K。默认为环境温度。
            eta (float, optional): 冷头效率，相对理想卡诺，取值 (0, 1]。
            approach (float, optional): 蒸发器温差，单位 K。

        Returns:
            float: 局部 COP，单位 RF热/RF电；不需要做功时为 inf。
        """
        if T_hot is None:
            T_hot = Thermal.STD_ENV_KELVIN
        T_hot = float(T_hot)
        T_evap = float(T_body) - float(approach)
        if T_evap >= T_hot:
            return float("inf")
        if T_evap <= 0.0:
            return 0.0
        return max(float(eta), Thermal.EPS) * T_evap / (T_hot - T_evap)

    @staticmethod
    def CoolElectricPerHeat(T_body, T_hot=None, eta=1.0, approach=0.0):
        # type: (float, float | None, float, float) -> float
        """
        制冷的单价：在仓温 `T_body` 处搬走 1 RF 热量要花多少 RF 电。

        即 `1 / CoolCOP(...)`，与加热侧的 `ELECTRIC_PER_HEAT` 是同一种量，两者在
        `COOL_REFERENCE_KELVIN` 上相等。不需要做功时为 0，够不到绝对零度时为 inf。

        Args:
            T_body (float): 被冷却物的温度，单位 K。
            T_hot (float, optional): 排热侧温度，单位 K。默认为环境温度。
            eta (float, optional): 冷头效率，相对理想卡诺，取值 (0, 1]。
            approach (float, optional): 蒸发器温差，单位 K。

        Returns:
            float: 单价，单位 RF电/RF热。
        """
        cop = Thermal.CoolCOP(T_body, T_hot=T_hot, eta=eta, approach=approach)
        if cop == float("inf"):
            return 0.0
        if cop <= 0.0:
            return float("inf")
        return 1.0 / cop

    @staticmethod
    def Clamp(x, lo, hi):
        # type: (float, float, float) -> float
        """
        将数值限制在 [lo, hi] 区间内。

        Args:
            x (float): 输入值。
            lo (float): 下限。
            hi (float): 上限。

        Returns:
            float: 限制后的值。
        """
        return max(lo, min(hi, x))

    # =========================
    # 功能 1：给定期望温度，计算功率和热值变化
    # =========================
    @staticmethod
    def HeatToTarget(H, target_T, max_power=None, dt=1.0, capacity=None):
        # type: (float, float, float | None, float, float | None) -> Thermal.HeatToTargetResult
        """
        给定期望温度和当前热值，计算所需功率以及单 tick 内热值变化。

        Args:
            H (float): 机器当前绝对热值，单位 RF。
            target_T (float): 期望达到的开尔文温度，单位 K。
            max_power (float, optional): 最大加热/移热功率，单位 RF/t。
                默认为 Thermal.MAX_HEAT_POWER。
            dt (float, optional): 时间步长，单位 tick，默认 1.0。
            capacity (float, optional): 热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。

        Returns:
            Thermal.HeatToTargetResult: 包含 required_power、actual_power、
                delta_heat 和 H_next 的结果对象。
        """
        if max_power is None:
            max_power = Thermal.MAX_HEAT_POWER

        H = float(H)
        target_T = float(target_T)
        max_power = float(max_power)
        dt = float(dt)

        H_target = Thermal.GetHeat(target_T, capacity)
        delta_needed = H_target - H

        delta_heat = Thermal.Clamp(delta_needed, -max_power * dt, max_power * dt)
        actual_power = delta_heat / dt

        return Thermal.HeatToTargetResult(
            required_power=delta_needed / dt,
            actual_power=actual_power,
            delta_heat=delta_heat,
            H_next=H + delta_heat,
        )

    # =========================
    # 功能 2：热交换做功
    # =========================
    @staticmethod
    def ExchangeCarnot(H_hot, H_cold, conductance=None, dt=1.0,
                       capacity_hot=None, capacity_cold=None):
        # type: (float, float, float | None, float, float | None, float | None) -> Thermal.ExchangeCarnotResult
        """
        热物体与机器进行理想卡诺热交换，机器对外做功。

        要求热物体热值 H_hot 大于机器热值 H_cold。
        热量从热物体流向机器，同时一部分热量转化为 RF 输出。

        Args:
            H_hot (float): 热物体的绝对热值，单位 RF。
            H_cold (float): 机器的绝对热值，单位 RF。
            capacity_hot (float, optional): 热物体的热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。
            capacity_cold (float, optional): 机器的热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。
            conductance (float, optional): 热交换系数，单位 RF/(tick*K)。
                默认为 Thermal.THERMAL_CONDUCTANCE。
            dt (float, optional): 时间步长，单位 tick，默认 1.0。

        Returns:
            Thermal.ExchangeCarnotResult: 包含 H_hot_next、H_cold_next
                和 rf_out 的结果对象。
        """
        if conductance is None:
            conductance = Thermal.THERMAL_CONDUCTANCE

        H_hot = float(H_hot)
        H_cold = float(H_cold)
        conductance = float(conductance)
        dt = float(dt)

        if H_hot <= H_cold or H_hot <= Thermal.MIN_HEAT or H_cold <= Thermal.MIN_HEAT:
            return Thermal.ExchangeCarnotResult(H_hot, H_cold, 0.0)

        capacity_hot = Thermal.NormalizeCapacity(capacity_hot)
        capacity_cold = Thermal.NormalizeCapacity(capacity_cold)
        T_hot = H_hot / capacity_hot
        T_cold = H_cold / capacity_cold

        if T_hot <= T_cold or T_hot <= Thermal.MIN_HEAT or T_cold <= Thermal.MIN_HEAT:
            return Thermal.ExchangeCarnotResult(H_hot, H_cold, 0.0)

        dT = T_hot - T_cold
        Q_hot_want = conductance * dT * dt

        # 防止交换后热端低于冷端: 取两端刚好等温的那个交换量。
        # 两侧热容相同时退化成原式 (H_hot - H_cold) * H_hot / (H_hot + H_cold)。
        Q_hot_limit = (
            dT * capacity_hot * capacity_cold * T_hot
            / (capacity_cold * T_hot + capacity_hot * T_cold)
        )
        Q_hot = max(0.0, min(Q_hot_want, Q_hot_limit))

        # 理想卡诺关系：Q_cold / Q_hot = T_cold / T_hot
        Q_cold = Q_hot * (T_cold / T_hot)
        W = Q_hot - Q_cold

        H_hot_next = H_hot - Q_hot
        H_cold_next = H_cold + Q_cold

        return Thermal.ExchangeCarnotResult(H_hot_next, H_cold_next, W)

    # =========================
    # 功能 3：主动耗能降温
    # =========================
    @staticmethod
    def ActiveCool(H, target_T, max_cool=None, dt=1.0,
                   eta=1.0, approach=0.0, T_cold_floor=None, capacity=None):
        # type: (float, float, float | None, float, float, float, float | None, float | None) -> Thermal.ActiveCoolResult
        """
        用卡诺制冷机主动降温，把热值降向目标温度对应的热值。

        算的是一台"接近现实"的制冷机，而不是可逆的理想机：

            - 冷头必须比被冷却物更冷才能吸热，蒸发温度 `T_c = T_body - approach`；
            - 冷头效率 `eta` 是相对理想卡诺的折扣(0~1)，真实斯特林机约 0.2~0.3；
            - 高于环境温度的一段直接向环境排热，不耗功；
            - 蒸发温度逼近绝对零度时耗电趋于无穷，所以绝对零度永远够不到。

        耗电沿本 tick 跨过的温区积分(等价于用两端温度的对数平均)：

            W = C / eta * [T_h * ln(T_c1 / T_c2) - (T_c1 - T_c2)]

        必须沿轨迹积分：只拿起点温度算 COP 的话，"一个周期直接冻到目标温度"反而会
        便宜到不耗电(起点正好是环境温度时 COP 为无穷)，步长越大越省电，与物理相反。

        Args:
            H (float): 被冷却物当前的绝对热值，单位 RF。
            target_T (float): 期望达到的开尔文温度，单位 K。
            max_cool (float, optional): 每 tick 最大移热速率，单位 RF/t。
                默认为 Thermal.MAX_COOL_POWER。
            dt (float, optional): 时间步长，单位 tick，默认 1.0。
            eta (float, optional): 冷头效率，相对理想卡诺，取值 (0, 1]，默认 1.0。
            approach (float, optional): 蒸发器温差，单位 K，默认 0.0。
                换热器不可能零温差，取 0 相当于直接拿被冷却物的温度当蒸发温度。
            T_cold_floor (float, optional): 蒸发温度下限，单位 K。
                默认为 Thermal.MIN_HEAT，避免绝对零度附近出现除零。
            capacity (float, optional): 被冷却物的热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。热容越大, 同样的降温幅度要搬走更多
                热量, 因此也更费电。

        Returns:
            Thermal.ActiveCoolResult: 包含 H_next、Q_removed 和 energy_used 的结果对象。
                energy_used 为本 tick 消耗的 RF 能量，温度越低每份热量越贵。
        """
        if max_cool is None:
            max_cool = Thermal.MAX_COOL_POWER
        if T_cold_floor is None:
            T_cold_floor = Thermal.MIN_HEAT

        H = float(H)
        target_T = float(target_T)
        max_cool = float(max_cool)
        dt = float(dt)
        eta = float(eta)
        approach = float(approach)
        T_cold_floor = float(T_cold_floor)

        capacity = Thermal.NormalizeCapacity(capacity)
        T_env = Thermal.STD_ENV_KELVIN
        H_target = Thermal.GetHeat(target_T)

        Q_remove = max(0.0, H - H_target)
        Q_remove_tick = min(Q_remove, max_cool * dt)

        # 绝对零度够不到：本 tick 最多把蒸发温度压到下限
        T_evap_start = Thermal.GetKelvin(H, capacity) - approach
        Q_remove_tick = min(
            Q_remove_tick, max(0.0, T_evap_start - T_cold_floor) * capacity
        )
        if Q_remove_tick <= 0.0:
            return Thermal.ActiveCoolResult(H, 0.0, 0.0)

        T_evap_end = T_evap_start - Q_remove_tick / capacity

        if T_evap_end >= T_env:
            # 整段都还比环境热，理想情况下向环境排热不耗功
            energy_used = 0.0
        else:
            # 只有低于环境的那一段需要制冷机做功，积分从环境温度开始
            T_evap_top = min(T_evap_start, T_env)
            # 卡诺制冷机 COP = T_c / (T_h - T_c)
            # dW = dQ / (eta * COP) = (T_h - T_c) / (eta * T_c) * dQ
            energy_used = (capacity / max(eta, Thermal.EPS)) * (
                T_env * math.log(T_evap_top / T_evap_end)
                - (T_evap_top - T_evap_end)
            )

        return Thermal.ActiveCoolResult(
            H - Q_remove_tick, Q_remove_tick, energy_used
        )

    # =========================
    # 可选：单 tick 统一调度
    # =========================
    @staticmethod
    def TickMachine(H, target_T=None, hot_object_H=None, capacity=None):
        # type: (float, float | None, float | None, float | None) -> Thermal.TickMachineResult
        """
        在单个 tick 内统一处理热交换做功、主动降温和加热到目标温度。

        执行顺序：
            1. 如果提供了热物体，先进行卡诺热交换并产出 RF。
            2. 如果提供了目标温度：
                - 当前温度高于目标温度时，执行主动冷却。
                - 当前温度低于目标温度时，执行加热。

        Args:
            H (float): 机器当前绝对热值，单位 RF。
            target_T (float, optional): 期望达到的开尔文温度，单位 K。
                为 None 时不进行温度控制。
            hot_object_H (float, optional): 热物体的绝对热值，单位 RF。
                为 None 时不进行热交换做功。
            capacity (float, optional): 本机热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。

        Returns:
            Thermal.TickMachineResult: 包含 H_next、hot_object_H_next、
                rf_out 和 energy_used 的结果对象。
        """
        H = float(H)
        if hot_object_H is not None:
            hot_object_H = float(hot_object_H)

        rf_out = 0.0
        energy_used = 0.0

        if hot_object_H is not None:
            exchange_res = Thermal.ExchangeCarnot(
                hot_object_H, H, capacity_cold=capacity
            )
            hot_object_H = exchange_res.H_hot_next
            H = exchange_res.H_cold_next
            rf_out = exchange_res.rf_out

        if target_T is not None:
            target_T = float(target_T)

            if Thermal.GetKelvin(H, capacity) > target_T:
                cool_res = Thermal.ActiveCool(H, target_T, capacity=capacity)
                H = cool_res.H_next
                energy_used = cool_res.energy_used
            else:
                heat_res = Thermal.HeatToTarget(H, target_T, capacity=capacity)
                H = heat_res.H_next
                energy_used = max(0.0, heat_res.delta_heat)

        return Thermal.TickMachineResult(H, hot_object_H, rf_out, energy_used)

    @staticmethod
    def ConductHeat(H_hot, H_cold, conductance=None, dt=1.0,
                    capacity_hot=None, capacity_cold=None):
        # type: (float, float, float | None, float, float | None, float | None) -> Thermal.ConductHeatResult
        """
        两个物体之间进行纯热传导，不做功，只交换热量直到温度平衡。

        方向按温度判断: 要求 `H_hot / capacity_hot` 大于 `H_cold / capacity_cold`, 即
        `H_hot` 那一侧确实更热。两侧热容可以不同, 所以不能比热值 —— 热容大的机器在
        300K 就有几百 RF 热值, 一比热值就会被误判成更热的那一方。
        与 ExchangeCarnot 不同，本函数不产出 RF，仅让两侧温度趋近。

        Args:
            H_hot (float): 热物体的绝对热值，单位 RF。
            H_cold (float): 冷物体的绝对热值，单位 RF。
            capacity_hot (float, optional): 热物体的热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。
            capacity_cold (float, optional): 冷物体的热容，单位 RF/K。
                默认为 Thermal.HEAT_CAPACITY。
            conductance (float, optional): 热交换系数，单位 RF/(tick*K)。
                默认为 Thermal.THERMAL_CONDUCTANCE。
            dt (float, optional): 时间步长，单位 tick，默认 1.0。

        Returns:
            Thermal.ConductHeatResult: 包含 H_hot_next、H_cold_next
                和 Q_transferred 的结果对象。
        """
        if conductance is None:
            conductance = Thermal.THERMAL_CONDUCTANCE

        H_hot = float(H_hot)
        H_cold = float(H_cold)
        conductance = float(conductance)
        dt = float(dt)

        capacity_hot = Thermal.NormalizeCapacity(capacity_hot)
        capacity_cold = Thermal.NormalizeCapacity(capacity_cold)
        T_hot = H_hot / capacity_hot
        T_cold = H_cold / capacity_cold

        # 谁更热一律比温度, 不能比热值: 热容不同的两台机器, 热值大小与温度高低并不一致
        # (热容 50 的机器在 300K 就有 15000 RF 热值, 比 800K 的加热仓还"热"), 比热值会把
        # 传热方向判反 —— 结果是重机器永远收不到热。
        if T_hot <= T_cold or T_hot <= Thermal.MIN_HEAT or T_cold <= Thermal.MIN_HEAT:
            return Thermal.ConductHeatResult(H_hot, H_cold, 0.0)

        dT = T_hot - T_cold
        Q_want = conductance * dT * dt

        # 平衡点是两者等温处: 热容相等时退化成 Q_max = (H_hot - H_cold) / 2
        Q_max = (capacity_cold * H_hot - capacity_hot * H_cold) / (
            capacity_hot + capacity_cold
        )
        Q = max(0.0, min(Q_want, Q_max))

        H_hot_next = H_hot - Q
        H_cold_next = H_cold + Q

        return Thermal.ConductHeatResult(H_hot_next, H_cold_next, Q)
