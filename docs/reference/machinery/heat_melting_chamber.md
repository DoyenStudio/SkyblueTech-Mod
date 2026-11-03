# 熔化仓

方块 ID：`skybluetech:heat_melting_chamber`。使用 `heat_melting_chamber.geo.json`
和 `heat_melting_chamber_texture.png`，仅接收外部供热，不耗电。

物品输入槽 0、输出槽 1；流体输出槽 0，容量 1500 mB，不允许倒入流体。
温度条固定显示 300～900 K，热容沿用小型蒸馏仓的 50 RF热/K。

配方定义位于 `common/machinery_def/heat_melting_chamber.py`，使用
`HeatMeltingChamberRecipe(input_item_id, output_fluid, output_volume,
tick_duration, min_temperature, fit_temperature, max_temperature,
output_item_id=None, output_count=1, heat_per_produce=1.0)`。
每次消耗一个输入物。`heat_per_produce` 单位与小型蒸馏仓相同，为 RF热/mB。

- 温度不高于最低温度时暂停；最低至最适温度之间线性从 0 增至 1.0x。
- 达到最适温度后恒定 1.0x，不受升级加速。
- 每推进一个配方 tick，扣除 `output_volume * heat_per_produce / tick_duration` 热量。
  过热仍扣热；余热不足以支付该步时限制该步进度，避免负热量。
- 是否产出流体以完成该次配方的加工 tick 扣热前温度判定；恰好等于最高温度仍产液。
  超过最高温度照常消耗输入并产出可选固体，不产液，也不受流体槽堵塞影响。
- 输出不足或流体类型冲突时暂停，不消耗物品或配方热量；环境换热照常发生。
- 小数进度原生保存；切换输入配方清零，暂停、缺热和输出堵塞保留进度。

初始配方沿用旧草稿：松香 → 144 mB 熔融松香，200 tick，333/343/353 K，
无固体输出，默认 1 RF热/mB。物品输出是正常副产物，不是仅过热产生的废料。

游戏内验收：检查模型及材质、标题与状态灯、温度条两端、输入输出和管道抽取；
在最低温度、中间温度、最适温度、最高温度及超温条件检查速度和产出；
检查满槽暂停、过热满流体槽仍可加工、不同配方重置进度，以及保存重进后的进度/流体。
离线 JSON 解析和界面预览不代替这些游戏内验收。
