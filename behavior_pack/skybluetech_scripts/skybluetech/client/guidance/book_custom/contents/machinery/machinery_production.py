# coding=utf-8
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
    CheckRecipes,
)
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.common.machinery_def.brine_evaporation_pond import (
    STRUCTURE_PALETTE as BRINE_EVAPORATION_POND_SP,
)
from skybluetech_scripts.skybluetech.common.machinery_def.distillation_column import (
    STRUCTURE_PALETTE as DISTILLATION_COLUMN_SP,
)
from skybluetech_scripts.skybluetech.common.machinery_def.gas_metallurgical_furnace import (
    STRUCTURE_PALETTE as GAS_METALLURGICAL_FURNACE_SP,
)
from skybluetech_scripts.skybluetech.common.machinery_def.large_reaction_pool import (
    STRUCTURE_PALETTE as LARGE_REACTION_POOL_SP,
)
from skybluetech_scripts.skybluetech.common.machinery_def.vacuum_freezer import (
    STRUCTURE_PALETTE as VACUUM_FREEZER_SP,
)

from ...define import (
    MachineryWorkstationRecipePage,
    MultiBlockStructureModelPage,
    PageGroup,
    TextPage,
    UnfinishedItemName,
)

alloy_furnace = PageGroup(
    "alloy_furnace_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ALLOY_FURNACE),
            '合金炉可以将多种金属<item id="%s">或非金属<item id="%s">混合烧制为<style color="§5" t="合金"><item id="%s">。\n钢锭、 青铜锭、 殷钢锭等都需要合金炉进行烧制。'
            % ("minecraft:iron_ingot", id_enum.Dusts.CARBON, id_enum.Ingots.STEEL),
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ALLOY_FURNACE),
    ],
)


brine_evaporation_pond = PageGroup(
    "brine_evaporation_pond_description",
    [
        TextPage(
            "卤水池",
            '<text color="§9" t="卤水池">多方块结构是海水化工中的核心设施之一， 可以使用热能浓缩盐水。\n使用<link id="scepter" text="多方块结构手杖">可快速建造。\n\n在受热口放置热源， 从液体输入口送入<text color="§3" t="淡盐水">， 即可从液体输出口收集饱和盐水。',
            hyperlink_cbs={
                "scepter": lambda _: CheckRecipe(id_enum.MULTIBLOCK_STRUCTURE_SCEPTER)
            },
        ),
        MultiBlockStructureModelPage(
            id_enum.BrineEvaporationPond.CONTROLLER, BRINE_EVAPORATION_POND_SP
        ),
        MachineryWorkstationRecipePage(id_enum.BrineEvaporationPond.CONTROLLER),
    ],
)


compressor = PageGroup(
    "compressor_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.COMPRESSOR),
            '压缩机可将金属锭<item id="%s">压制为板材<item id="%s">， 除此以外还能对一些材料进行进一步压缩。'
            % (id_enum.Ingots.TIN, id_enum.Plates.TIN),
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.COMPRESSOR),
    ],
)

distillation_chamber = PageGroup(
    "distillation_chamber_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.DISTILLATION_CHAMBER),
            '小型蒸馏仓可以使用<text color="§c" t="热能">对其中的流体进行<text color="§9" t="蒸馏">， 如生产饮用水和部分油类液体等。\n它的下方需要一个<text color="§4" t="热源">为其供热， 如<link text="电力加热仓" id="electric_heater">。',
            hyperlink_cbs={
                "electric_heater": lambda _: (
                    _get_machinery_thermal_module().electric_heater.FastJump()
                )
            },
        ),
        TextPage(
            "",
            "小型蒸馏仓按配方所需的温度进行蒸馏， 每个配方只产出一种流体。蒸馏塔也兼容这些配方， 在相同温度下的原料与产物比例相同。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.DISTILLATION_CHAMBER),
    ],
)

distillation_column = PageGroup(
    "distillation_column_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.DistillationColumn.CONTROLLER),
            '蒸馏塔可以使用<text color="§c" t="热能">对其中的流体进行<text color="§9" t="蒸馏">。处理兼容配方时， 蒸馏塔的最高蒸馏速率比小型蒸馏仓更高， 部分配方还能收集多种<text color="§d" t="馏分">。\n\n'
            '搭建时至少需要一个液体输入口、一个受热口和两个液体输出口。蒸馏塔的受热口需要<text color="§4" t="热源">为其供热， 如<link text="电力加热仓" id="electric_heater">。',
            hyperlink_cbs={
                "electric_heater": lambda _: (
                    _get_machinery_thermal_module().electric_heater.FastJump()
                )
            },
        ),
        TextPage(
            "",
            '馏分会按液体输出口高低进行输出， 蒸馏塔最多使用最高的四个输出口。<text color="§6" t="最高处">的输出口将产生最上层馏分， 越往下的输出口就输出<text color="§5" t="越下层">的馏分。'
            '同一层有多个输出口时， 按世界坐标 X、Z 由小到大排列， 各自独立输出。\n\n'
            '蒸馏液态空气至少需要三个液体输出口， 数量不足时会暂停。满足配方要求后， 如果还有馏分没有对应的输出口， 这些下层馏分会被<text color="§4" t="丢弃">。',
        ),
        MultiBlockStructureModelPage(
            id_enum.DistillationColumn.CONTROLLER, DISTILLATION_COLUMN_SP
        ),
        MachineryWorkstationRecipePage(id_enum.DistillationColumn.CONTROLLER),
    ],
)

electric_crafter = PageGroup(
    "electric_crafter_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ELECTRIC_CRAFTER),
            '电动合成台可按<text color="§2" t="给定模版">和输入物品消耗能量自动进行<text color="§9" t="物品合成">。\n需要先制作一个<item id="%s"><link id="crafting_template_recipe" text="合成样板">， 手持合成样板下蹲点击地面打开模版设置界面进行合成配方设置， 然后将其插入电动合成台中， 即可进行自动合成。'
            % id_enum.CRAFTING_TEMPLATE,
            hyperlink_cbs={
                "crafting_template_recipe": lambda _: CheckRecipe(
                    id_enum.CRAFTING_TEMPLATE
                )
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ELECTRIC_CRAFTER),
    ],
)

electrolyzer = PageGroup(
    "electrolyzer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ELECTROLYZER),
            '电解机消耗能量对液体进行电解， 也可以对不活泼金属进行精炼处理。\n\n电解机的流体输出模式<text color="§2" t="较为特殊">： 左输出槽的流体从机器<text color="§c" t="左侧">的管道输出； 右输出槽从机器<text color="§9" t="右侧">输出； 下输出槽从机器<text color="§5" t="底部">输出。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ELECTROLYZER),
    ],
)


high_temp_electrolyzer = PageGroup(
    "high_temp_electrolyzer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HIGH_TEMP_ELECTROLYZER),
            "在机器底面接红外高热发生器或导热块， 再接入电力。"
            "铝电解混合料从物品槽投入， 无水氯化镁熔盐从流体槽注入。\n\n"
            "金属进入物品出口， 副产气体默认从右侧抽取。点击面板上的进度箭头可查看配方温区。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HIGH_TEMP_ELECTROLYZER),
    ],
)


engraver = PageGroup(
    "engraver_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.ENGRAVER),
            "蚀刻机可以使用一种或两种蚀刻液， 使用不同波长的激光对原料进行较精密的蚀刻， 制造诸如高级电路板这类精密构件。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.ENGRAVER),
    ],
)

flotation_machine = PageGroup(
    "flotation_machine_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.FLOTATION_MACHINE),
            '浮选机可以对粗矿进行浮选， 产出<item id="{sorted_ore}">预选矿料和<item id="{cake}">滤饼， 使一份粗矿能产出更多产品。\n\n'
            "接通电源后， 输入粗矿、水和复配矿物捕收剂。工作时还会产生含捕收剂的浮选废水， 废水槽容量不足时需要排出废水才能继续。".format(
                sorted_ore=id_enum.SortedOres.IRON, cake=id_enum.FilterCakes.IRON
            ),
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.FLOTATION_MACHINE),
    ],
)


fluid_condenser = PageGroup(
    "fluid_condenser_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.FLUID_CONDENSER),
            '流体冷却机可将<text color="§c" t="高温流体">进行冷却获得物品产物。 如将熔融金属冷却为锭。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.FLUID_CONDENSER),
    ],
)

freezer = PageGroup(
    "freezer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.FREEZER),
            '可按照设置将水<text color="§9" t="冷冻">为冰雪。 可以选择生产冰块<item id="minecraft:ice">、 浮冰<item id="minecraft:packed_ice">、 蓝冰<item id="minecraft:blue_ice">、 雪块<item id="minecraft:snow">或雪球<item id="minecraft:snowball">， 所需水量、 加工时间和能耗各不相同。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.FREEZER),
    ],
)

gas_metallurgical_furnace = PageGroup(
    "gas_metallurgical_furnace_description",
    [
        TextPage(
            "气体冶金炉",
            '气体冶金炉主要用于在特定气体环境下<text color="§6" t="冶炼金属">。例如， 可用<item id="{hydrogen}">氢气还原氧化铁粉， 得到铁粉和水蒸气。\n\n'
            "炉体底面为 3×3， 高 5 格。控制器所在层和紧下方一层可安装输入口， 紧上方一层可安装输出口， 中间三层的中心留空。\n\n"
            "通过能量输入口供电， 再按配方选装对应的进出料接口。点击结构图中的方块可查看该位置允许使用的部件。".format(
                hydrogen=id_enum.CommonGas.HYDROGEN
            ),
        ),
        MultiBlockStructureModelPage(
            id_enum.GasMetallurgicalFurnace.CONTROLLER,
            GAS_METALLURGICAL_FURNACE_SP,
        ),
        MachineryWorkstationRecipePage(id_enum.GasMetallurgicalFurnace.CONTROLLER),
    ],
)


heat_melting_chamber = PageGroup(
    "heat_melting_chamber_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HEAT_MELTING_CHAMBER),
            '熔化仓消耗<text color="§4" t="热量">将低温易熔物品熔化为流体。热源应接在底部。\n\n'
            "超过配方的最高温度时， 仍会消耗原料， 但不会产出流体。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HEAT_MELTING_CHAMBER),
    ],
)


hydroponic_base = PageGroup(
    "hydroponic_base_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HYDROPONIC_BASE),
            '水培基座为其上方的<style color="§2"><link text="水培床" id="hydroponic_bed"><style color="R">提供作物生长所需水源， 同时水培床的作物产出也会存放到水培基座供抽取。\n\n水培床所需水分或营养液需要输入到其下方的水培基座才能被水培床利用。',
            hyperlink_cbs={"hydroponic_bed": lambda _: hydroponic_bed.FastJump()},
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HYDROPONIC_BASE),
    ],
)

hydroponic_bed = PageGroup(
    "hydroponic_bed_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HYDROPONIC_BED),
            '水培床可给予其中的作物<item id="minecraft:wheat_seeds">恒定的光照和水分， <text color="§2" t="加快作物生长">。\n为水培床下方的<link text="水培基座" id="hydroponic_base">供水， 在水培床内放置作物种子， 再在水培床上方使用线缆进行供能， 即可使作物进入生长周期。',
            hyperlink_cbs={"hydroponic_base": lambda _: hydroponic_base.FastJump()},
        ),
        TextPage(
            "",
            '水培床会<text color="§2" t="自动">从产出中收取一枚种子进行补种， 剩余产物会被存入下方的<text color="§9" t="水培基座">。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HYDROPONIC_BED),
    ],
)

hydroponic_bed_sand = PageGroup(
    "hydroponic_bed_sand_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.HYDROPONIC_BED_SAND),
            "沙底水培床可培养甘蔗和仙人掌。将其放在水培基座上并供电， 基座供水并接收收获的作物。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.HYDROPONIC_BED_SAND),
    ],
)


industrial_centrifuge = PageGroup(
    "industrial_centrifuge_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.INDUSTRIAL_CENTRIFUGE),
            '工业离心机通过快速转动离心管， 对其中的液体进行<text color="§5" t="离心分离">， 或分离出其中的固体粉末。\n\n'
            "放置时， 上方留出一格供转子自动生成。需要加热的配方从机器底面供热。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.INDUSTRIAL_CENTRIFUGE),
    ],
)


large_reaction_pool = PageGroup(
    "large_reaction_pool_description",
    [
        TextPage(
            "大型反应池",
            '大型反应池可进行比小型化学反应釜更复杂的反应， 最多使用三路流体输入和两路流体输出。需要加热的配方还要通过<text color="§c" t="热量输入口">供热。\n\n'
            "池体底面为 3×3， 高 4 格。控制器所在层可安装输入口， 紧上方一层可安装输出口， 两层池壁的中心留空。\n\n"
            "通过能源输入口供电， 按配方所示的通道编号接管。点击结构图中的方块可查看该位置允许使用的部件。",
        ),
        MultiBlockStructureModelPage(
            id_enum.LargeReactionPool.CONTROLLER, LARGE_REACTION_POOL_SP
        ),
        MachineryWorkstationRecipePage(id_enum.LargeReactionPool.CONTROLLER),
    ],
)


macerator = PageGroup(
    "macerator_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.MACERATOR),
            '磨粉机能被用于物品磨粉<item id="minecraft:bone_meal">、 矿物粉碎<item id="%s">等。 它能将金属锭隔绝空气磨成金属粉， 也能对部分自然资源进行粉碎处理， 还能对粗矿甚至远古残骸进行研磨增产。'
            % id_enum.Dusts.TIN,
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.MACERATOR),
    ],
)

magma_centrifuge = PageGroup(
    "magma_centrifuge_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.MAGMA_CENTRIFUGE),
            '高热流体离心机主要用于对<text color="§4" t="熔岩"><item id="minecraft:lava_bucket">类混合物流体进行离心， 例如对深层熔岩进行离心， 再对产物进行进一步离心得到熔融矿物质。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.MAGMA_CENTRIFUGE),
    ],
)

magma_furnace = PageGroup(
    "magma_furnace_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.MAGMA_FURNACE),
            '熔岩炉以比较高的功耗<text color="§c" t="熔化物品">， 例如将金属熔化为熔融金属， 将石头熔化为熔岩。\n\n使用<link text="特化控制电路： 高热熔岩工厂" id="magma_factory_recipe">升级可加快熔岩产出、 降低熔岩炉能耗， 但是此时熔岩炉<text color="§c" t="只能">生产熔岩。',
            hyperlink_cbs={
                "magma_factory_recipe": lambda _: CheckRecipe(
                    id_enum.Upgraders.SPEC_MAGMA_FACTORY
                )
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.MAGMA_FURNACE),
    ],
)

metal_press = PageGroup(
    "metal_press_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.METAL_PRESS),
            '可以使用一份金属原料<item id="%s">和润滑油， 根据所安装的<item id="%s"><link id="press" text="压印模板">生产金属制品<item id="%s">。'
            % (id_enum.Ingots.TIN, id_enum.InscriberPress.EMPTY, id_enum.Sticks.TIN),
            hyperlink_cbs={
                "press": lambda _: CheckRecipes(list(id_enum.InscriberPress.all_sub()))
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.METAL_PRESS),
    ],
)

mixed_macerator = PageGroup(
    "mixed_macerator_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.MIXED_MACERATOR),
            "可以将多种固体进行混合研磨得到产物。\n\n输入物需要放在固定的槽位， 不能交换摆放。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.MIXED_MACERATOR),
    ],
)


mixer = PageGroup(
    "mixer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.MIXER),
            "可以将固体与流体进行混合搅拌得到固体新产物。",
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.MIXER),
    ],
)

oil_extractor = PageGroup(
    "oil_extractor_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.OIL_EXTRACTOR),
            '可将部分植物种子<item id="minecraft:wheat_seeds">榨油以得到<text color="§a" t="植物油">。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.OIL_EXTRACTOR),
    ],
)

precision_cutter = PageGroup(
    "precision_cutter_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.PRECISION_CUTTER),
            '可对部分物品和建材进行<text color="§1" t="精密切割">， 将其切分为原料， 或对物品进行精细打磨。\n\n'
            '精密切割机需要安装<item id="{cutter}"><link id="cutter" text="锯片">， 每次加工会消耗锯片耐久。'.format(
                cutter=id_enum.Cutter.STEEL
            ),
            hyperlink_cbs={
                "cutter": lambda _: CheckRecipes(list(id_enum.Cutter.all()))
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.PRECISION_CUTTER),
    ],
)


redstone_furnace = PageGroup(
    "redstone_furnace_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.REDSTONE_FURNACE),
            '红石炉将红石能这种能源作为燃料， 和熔炉<item id="minecraft:furnace">一样<text color="§c" t="烧制物品">。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.REDSTONE_FURNACE),
    ],
)

sawmill = PageGroup(
    "sawmill_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.SAWMILL),
            '锯木机可以提高木材利用率。\n\n例如， 1 根<item id="minecraft:oak_log">橡木原木可锯成 6 块<item id="minecraft:oak_planks">橡木木板， 1 块木板可锯成 3 根<item id="minecraft:stick">木棍。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.SAWMILL),
    ],
)


smmall_chemical_reactor = PageGroup(
    "smmall_chemical_reactor_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.SMALL_CHEMICAL_REACTOR),
            '小型化学反应釜可消耗能量进行不复杂的化学反应。\n\n部分配方可能需要<text color="§d" t="催化剂">。',
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.SMALL_CHEMICAL_REACTOR),
    ],
)

specialized_growth_base = PageGroup(
    "specialized_growth_base_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.SPECIALIZED_GROWTH_BASE),
            '特种培养基座向正上方的<link id="chamber" text="特种培养仓">补充消耗性原料和培养液， 并接收物品及液体产物。自动化供料和收集时， 将物品、流体管道接到基座。',
            hyperlink_cbs={
                "chamber": lambda _: specialized_growth_chamber.FastJump(),
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.SPECIALIZED_GROWTH_BASE),
    ],
)


specialized_growth_chamber = PageGroup(
    "specialized_growth_chamber_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.SPECIALIZED_GROWTH_CHAMBER),
            "特种培养仓用于培养特殊作物。接通电源后， 手动将配方需要的保留材料放入绿色槽位， 加工时不会消耗这些材料。\n\n"
            '培养仓可以手动供料和取出产物。需要自动化时， 在正下方放置<item id="{base}"><link id="chamber_base" text="特种培养基座">， 由基座补充消耗性原料和培养液， 并收集产物。'.format(
                base=id_enum.Machinery.SPECIALIZED_GROWTH_BASE
            ),
            hyperlink_cbs={
                "chamber_base": lambda _: specialized_growth_base.FastJump(),
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.SPECIALIZED_GROWTH_CHAMBER),
    ],
)


thermal_cracker = PageGroup(
    "thermal_cracker_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.THERMAL_CRACKER),
            '热裂解机从底部接收热量， 可按配方裂解物品或流体。建议使用<link id="heater" text="红外高热发生器">供热。\n\n'
            "在「流体输出面」页可为每个输出槽选择一个或多个面， 也可以关闭该槽的所有输出面。",
            hyperlink_cbs={
                "heater": lambda _: (
                    _get_machinery_thermal_module().infrared_heat_generator.FastJump()
                )
            },
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.THERMAL_CRACKER),
    ],
)

vacuum_freezer = PageGroup(
    "vacuum_freezer_description",
    [
        TextPage(
            UnfinishedItemName(id_enum.Machinery.VACUUM_FREEZER),
            '真空冷却仓是一种<text color="§b" t="多方块结构机器">， 可以消耗能量提供低温或超低温环境对气体<item id="{compressed_air}">进行液化<item id="{liquid_air}">或者对液体<item id="{water}">进行固化<item id="{ice}">的处理； 使用<link id="scepter" text="多方块结构手杖">可快速建造。\n\n<text color="§c" t="注意， ">冷却仓进行超低温冷却需要消耗大量电力， 一旦提供的输入功率不足， 不仅会使配方减速， 甚至会使得配方运行进度倒流！'.format(
                compressed_air=id_enum.CommonGas.COMPRESSED_AIR,
                liquid_air=id_enum.CommonLiquid.LIQUID_AIR,
                water=id_enum.Vanilla.WATER,
                ice="minecraft:ice",
            ),
            hyperlink_cbs={
                "scepter": lambda _: CheckRecipe(id_enum.MULTIBLOCK_STRUCTURE_SCEPTER)
            },
        ),
        MultiBlockStructureModelPage(
            id_enum.VacuumFreezer.CONTROLLER, VACUUM_FREEZER_SP
        ),
        MachineryWorkstationRecipePage(id_enum.Machinery.VACUUM_FREEZER),
    ],
)


def _get_machinery_thermal_module():
    from . import machinery_thermal

    return machinery_thermal
