# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery, DistillationColumn
from skybluetech_scripts.skybluetech.common.machinery_def.distillation_column import STRUCTURE_PALETTE
from ...define import PageGroup, TextPage, MachineryWorkstationRecipePage, MultiBlockStructureModelPage


chain = PageGroup("polyethylene_chain", [
    TextPage("聚乙烯板生产线", "生树脂 → 熔化仓 → 液态生树脂 → 蒸馏塔 → 树油 → 热裂解机 → 乙烯 → 小型化学反应釜 → 熔融聚乙烯 → 流体凝结机 → 聚乙烯粒 → 压缩机 → 聚乙烯板。\n\n充分预热、供料供能充足、无升级时，稳定每 10 秒 1 板（每分钟 6 板）。这是连续吞吐量，不是第一块板的总等待时间。"),
    TextPage("熔化与分馏", "每份生树脂用 200 tick 熔成 244 mB 液态生树脂；343 K 满速，超过 373 K 会损失产物。\n蒸馏塔在 500 K 满速，每 200 tick 处理 244 mB；每份得到树油 100 mB、熔融松香 144 mB。\n\n配置两个有效输出口：最高处取树油，下一口取熔融松香。松香送独立流体凝结机（100 tick、40 RF/t）凝固为 1 份松香并储存。储存满后正常停机。"),
    MultiBlockStructureModelPage(DistillationColumn.CONTROLLER, STRUCTURE_PALETTE),
    TextPage("蒸馏塔制造", "工作台：四角钢板、四边铁锭、中心留空，一次得到 8 个塔外壳。\n\n控制器与三种接口在机件加工台制造，需要殷钢扳手和钳。输入口接液态生树脂，受热口接独立热源。输出口按高度排序；同高度按坐标排序，建议错层放置。"),
    MachineryWorkstationRecipePage(DistillationColumn.CONTROLLER),
    MachineryWorkstationRecipePage(DistillationColumn.IO_FLUID1),
    MachineryWorkstationRecipePage(DistillationColumn.IO_FLUID2),
    MachineryWorkstationRecipePage(DistillationColumn.IO_HEAT),
    TextPage("热裂解与供汽", "小型蒸馏仓将蒸馏水变为蒸汽：最适 393 K，每 200 tick 消耗 20 mB、产出 200 mB。每份需要蒸馏水 20 mB。温度高于最适会增加耗水。\n\n热裂解机输入树油与蒸汽各用固定槽，每槽 2000 mB。满速每 200 tick 消耗树油 100 mB、蒸汽 200 mB、2000 RF热，产乙烯 400 mB、纯甲烷 100 mB。缺料或缺热按比例降速；任一产物堵塞整机暂停。"),
    MachineryWorkstationRecipePage(Machinery.THERMAL_CRACKER),
    TextPage("热源设置", "各阶段独立供热，观察机器实际温度后微调热源功率与设定。\n熔化仓：电力加热仓先设 355 K，机器保持 343～373 K。\n蒸馏塔：热源先设 550 K，塔保持 500～600 K。\n供汽仓：热源先设 405 K，尽量维持机器 393 K。水蒸馏沿用已有配方。\n裂解机：红外高热发生器先设 1200 K，机器保持 1100～1300 K。≤1000 K 或 >1300 K 暂停。"),
    MachineryWorkstationRecipePage(Machinery.HEAT_MELTING_CHAMBER),
    MachineryWorkstationRecipePage(Machinery.INFRARED_HEAT_GENERATOR),
    TextPage("聚合与成板", "反应釜：乙烯 400 mB + 氧气 40 mB → 熔融聚乙烯 144 mB；200 tick、128 RF/t。这是游戏化聚合配方。\n凝结机：144 mB → 聚乙烯粒 ×9；100 tick、40 RF/t。\n压缩机：9 粒 → 聚乙烯板 ×1；160 tick、80 RF/t。\n\n计量统一为 16 mB = 1 粒，144 mB = 1 板。本阶段不提供聚乙烯重熔。两台新机器通过并联扩产，不支持升级加速。"),
    TextPage("副产物与运输", "熔融松香、熔融聚乙烯等热流体使用白铜管。全线制造及白铜运输均不依赖聚乙烯板。\n\n面向裂解机正面，左侧抽乙烯，右侧抽纯甲烷；分别设置管道，不混接。电解 40 mB 氧气副产 80 mB 氢气。氢气与纯甲烷分别经缓冲罐接燃气发电机。纯甲烷 4 mB → 320 RF，旧沼气燃料保持独立。"),
    TextPage("供电与投产检查", "每板理论净耗电约 8.8 万 RF，含松香凝结及氢气、甲烷回收；预热、散热、实际传热与蒸馏偏离最适温度另计，整线仍需外部供电。\n发电负载不足时燃气会积压，上游允许正常停机，不自动排放。\n\n投产先检查所有副产出口，再预热供汽；用 10 份树脂核对 10 板、10 松香、1000 mB 纯甲烷及 800 mB 氢气（若已燃烧则计回收电量）。"),
])

reactor = PageGroup("small_chemical_reactor_description", [
    TextPage("小型化学反应釜", "两路固定流体输入：乙烯、氧气；一路输出：熔融聚乙烯。每槽 2000 mB，储电 32000 RF。\n\n每份乙烯 400 mB + 氧气 40 mB，经过 200 tick、128 RF/t 产出聚乙烯 144 mB。缺电或输出空间不足时暂停；不需要催化剂，不模拟压力，不支持升级。"),
    MachineryWorkstationRecipePage(Machinery.SMALL_CHEMICAL_REACTOR),
])
