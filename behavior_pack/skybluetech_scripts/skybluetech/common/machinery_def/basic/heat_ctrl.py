# coding=utf-8
K_HEAT_VALUE = "heat_value"
"""`HeatCtrl`机器的热值; 0K 对应 0, 环境温度对应 Thermal.ENV_HEAT。

存的是参考热容(默认 Thermal.HEAT_CAPACITY = 1.0 RF/K)下的热值: 对默认热容的机器
来说, 它既是绝对热值(单位 RF), 数值上也等于温度(K)。覆写过 `heat_capacity` 的机器
这里存的仍然是温度, 乘上热容才是参与热力计算的绝对热值, 这样客户端 UI 读数、旧存档
都不会因为热容改动而错位。
"""
