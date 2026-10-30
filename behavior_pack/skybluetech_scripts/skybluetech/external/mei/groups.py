# coding=utf-8
"""
MEI 物品栏的分组（ctx.Registry.ItemOrganizer）：照 MEI 给原版分组的规矩 —— 同一类、至少三样，一样东西只进一个组。

两种组：
- **SHARED：和原版、别的模组一起的组**（「锭」「粗矿」「矿石」「镐」「桶」……，键是原版扩展用的 `mei:group.*` / `minecraft:itemGroup.name.*`）。
  组在就往里加（原版的锭后面接蔚蓝的金属锭），不在（比如 MEI 没给原版分组的那一类）就建上；卸载时只撤自己加的那几样，自己建的组空了再撤组。
  工具、盔甲按种类进原版的组（青铜镐进「镐」），不按材料另分。
- **OWN：蔚蓝自己的组**，照蔚蓝创造栏的分组（behavior_pack/netease_group/*.json：机器七类、金属板、线缆、升级……），
  名字用蔚蓝 .lang 里那些组名（itemGroup.skybluetech.*）。多方块结构一个结构一组（零件放在一起）。

不进组的：只有两样的（海水蓄水池、扇叶、矿锤、电池）、流体方块（flowing_*、熔融金属这些不在物品栏里）、*_useless。
创造栏的分组改了要跟着改这里 —— MEI 的 probe_skyblue_ext.py 拿 netease_group 对照（组员对得上、id 都在、不重）。
在 OnReady 登记：原版扩展的组在它的 OnRegister 里建，装配器三个阶段一个阶段跑完一轮，到 OnReady 一定都在。
"""
from . import bridge


def _ids(*names):  # type: (str) -> tuple
    return tuple("skybluetech:" + name for name in names)


SHARED = (
    ("mei:group.ingot", "mei.group.ingot", _ids(
        "aluminum_ingot", "tin_ingot", "lead_ingot", "silver_ingot", "nickel_ingot", "platinum_ingot", "titanium_ingot",
        "refined_iron_ingot", "bronze_ingot", "invar_ingot", "steel_ingot", "alumite_ingot", "light_skyblue_ingot",
        "soldering_ingot", "cupronickel_ingot", "ultraheatinum_ingot", "superconduct_ingot")),
    ("mei:group.raw_ore", "mei.group.raw_ore", _ids(
        "raw_aluminum", "raw_tin", "raw_lead", "raw_silver", "raw_nickel", "raw_platinum", "raw_titanium", "raw_uranium")),
    ("mei:group.raw_ore_block", "mei.group.raw_ore_block", _ids(
        "raw_tin_block", "raw_lead_block", "raw_silver_block", "raw_nickel_block", "raw_platinum_block")),
    ("minecraft:itemGroup.name.ore", "itemGroup.name.ore", _ids(
        "aluminum_ore", "tin_ore", "lead_ore", "silver_ore", "nickel_ore", "platinum_ore", "titanium_ore", "uranium_ore",
        "deepslate_tin_ore", "deepslate_lead_ore", "deepslate_silver_ore", "deepslate_nickel_ore", "deepslate_platinum_ore",
        "deepslate_uranium_ore", "nether_sulfur_ore")),
    ("mei:group.mineral_block", "mei.group.mineral_block", _ids(
        "tin_block", "lead_block", "silver_block", "nickel_block", "platinum_block", "bronze_block", "invar_block",
        "steel_block", "ultraheatinum_block")),
    ("mei:group.bucket", "mei.group.bucket", _ids(
        "brine_bucket", "chlorine_bucket", "deepslate_lava_bucket", "dilute_brine_bucket", "distilled_water_bucket",
        "heavy_lava_bucket", "hydrogen_bucket", "light_lava_bucket", "liquid_air_bucket", "liquid_resin_bucket",
        "lubricant_bucket", "methane_bucket", "methane_mud_bucket", "mid_lava_bucket", "molten_copper_bucket",
        "molten_earth_bucket", "molten_gold_bucket", "molten_impurity_bucket", "molten_iron_bucket", "molten_lead_bucket",
        "molten_nickel_bucket", "molten_platinum_bucket", "molten_silver_bucket", "molten_tin_bucket", "raw_oil_bucket",
        "saturated_brine_bucket", "sodium_hydroxide_solution_bucket", "sulfuric_acid_bucket", "vegetable_oil_bucket",
        "water_vapor_bucket")),
    ("minecraft:itemGroup.name.pickaxe", "itemGroup.name.pickaxe", _ids("bronze_pickaxe", "invar_pickaxe", "skyblue_pickaxe")),
    ("minecraft:itemGroup.name.sword", "itemGroup.name.sword", _ids("bronze_sword", "invar_sword", "skyblue_sword")),
    ("minecraft:itemGroup.name.axe", "itemGroup.name.axe", _ids("bronze_axe", "invar_axe", "skyblue_axe")),
    ("minecraft:itemGroup.name.shovel", "itemGroup.name.shovel", _ids("bronze_shovel", "invar_shovel", "skyblue_shovel")),
    ("minecraft:itemGroup.name.hoe", "itemGroup.name.hoe", _ids("bronze_hoe", "invar_hoe", "skyblue_hoe")),
    ("minecraft:itemGroup.name.helmet", "itemGroup.name.helmet", _ids("skyblue_helmet")),
    ("minecraft:itemGroup.name.chestplate", "itemGroup.name.chestplate", _ids("skyblue_chestplate")),
    ("minecraft:itemGroup.name.leggings", "itemGroup.name.leggings", _ids("skyblue_leggings")),
    ("minecraft:itemGroup.name.boots", "itemGroup.name.boots", _ids("skyblue_boots")),
    ("mei:group.dust", "mei.group.dust", _ids(
        "aluminum_dust", "copper_dust", "iron_dust", "gold_dust", "tin_dust", "lead_dust", "lead_oxide_dust",
        "lead_sulfate_dust", "silver_dust", "nickel_dust", "platinum_dust", "titanium_dust", "uranium_dust", "alumite_dust",
        "bronze_dust", "invar_dust", "steel_dust", "cupronickel_dust",
        "ancient_debris_dust", "carbon_dust", "lapis_dust", "obsidian_dust", "sulfur_dust", "concrete_dust")),
)
"""
(组的键, .lang 的键, (物品 id, ...))：和原版、别的模组一起的组。原版那几组的键照 MEI 原版扩展（creative/table.py、creative/groups.py）；
「粉」（mei:group.dust）原版没有，名字是 MEI 给的通用组名，谁先用谁建 —— 别的模组的粉也能并进来。蔚蓝的金属粉在前、别的粉在后
"""

OWN = (
    ("skybluetech:group.machinery_crafting", "itemGroup.skybluetech.machinery_crafting", _ids(
        "assembler", "electric_machinery_workstation", "machinery_workstation")),
    ("skybluetech:group.machinery_production", "itemGroup.skybluetech.machinery_production", _ids(
        "alloy_furnace", "compressor", "distillation_chamber", "electric_crafter", "electric_heater", "electrolyzer",
        "engraver", "fluid_condenser", "freezer", "heavy_compressor", "hydroponic_base", "hydroponic_bed",
        "hydroponic_bed_sand", "macerator", "magma_centrifuge", "magma_furnace", "metal_press", "mixed_macerator", "mixer",
        "oil_extractor", "precision_cutter", "redstone_furnace", "sawmill", "splitter", "template_assembler")),
    ("skybluetech:group.machinery_energy", "itemGroup.skybluetech.machinery_energy", _ids(
        "charger", "creative_power_acceptor", "redstoneflux_brake", "rf_repeater_plant")),
    ("skybluetech:group.machinery_logistics", "itemGroup.skybluetech.machinery_logistics", _ids(
        "item_splitter", "item_spreader", "fluid_splitter")),
    ("skybluetech:group.machinery_source_extraction", "itemGroup.skybluetech.machinery_source_extraction", _ids(
        "air_compressor", "digger", "farming_station", "forester", "mini_miner", "pump")),
    ("skybluetech:group.machinery_generator", "itemGroup.skybluetech.machinery_generator", _ids(
        "creative_generator", "gas_burning_generator", "geothermal_generator", "reacting_thermal_generator",
        "redstone_generator", "solar_panel", "thermal_generator", "wind_generator")),
    ("skybluetech:group.machinery_misc", "itemGroup.skybluetech.machinery_misc", _ids(
        "deepslate_lava_vibrator", "hover_text_displayer", "lexical_transmuter")),
    ("skybluetech:group.plates", "itemGroup.skybluetech.plates", _ids(
        "aluminum_plate", "copper_plate", "iron_plate", "gold_plate", "tin_plate", "lead_plate", "silver_plate",
        "nickel_plate", "platinum_plate", "titanium_plate", "alumite_plate", "bronze_plate", "invar_plate", "steel_plate",
        "cupronickel_plate", "ultraheatinum_plate", "superconduct_plate")),
    ("skybluetech:group.metal_sticks", "itemGroup.name.metal_sticks", _ids(
        "copper_stick", "tin_stick", "silver_stick", "platinum_stick", "bronze_stick", "invar_stick", "cupronickel_stick",
        "steel_stick", "iron_stick", "superconduct_stick")),
    ("skybluetech:group.tanks", "itemGroup.skybluetech.tanks", _ids(
        "tank_bronze", "tank_invar", "tank_steel", "tank_platinum", "tank_creative")),
    ("skybluetech:group.wire", "itemGroup.skybluetech.wire", _ids(
        "wire_tin", "wire_insulated_tin", "wire_copper", "wire_insulated_copper", "wire_silver", "wire_insulated_silver",
        "wire_superconduct", "wire_insulated_superconduct", "wire_creative", "wire_insulated_creative")),
    ("skybluetech:group.fluid_pipe", "itemGroup.skybluetech.fluid_pipe", _ids(
        "pipe_bronze", "pipe_cupronickel", "pipe_acidproof", "pipe_chemical", "pipe_ultraheatinum")),
    ("skybluetech:group.upgraders", "itemGroup.skybluetech.upgraders", _ids(
        "upgrader_plate_empty", "upgrader_basic_energy", "upgrader_basic_speed", "upgrader_generic_split",
        "upgrader_generic_expansion", "upgrader_generic_auto_ejection", "upgrader_generic_autostop",
        "upgrader_spec_magma_factory", "upgrader_spec_nitrogen_ext")),
    ("skybluetech:group.obj_upgraders", "itemGroup.skybluetech.obj_upgraders", _ids(
        "obj_upgrader_plate_common", "obj_upgrader_attack", "obj_upgrader_autoburning", "obj_upgrader_digspeed",
        "obj_upgrader_energy", "obj_upgrader_fortune", "obj_upgrader_veinminer", "obj_upgrader_plate_spec",
        "obj_upgrader_spec_farming", "obj_upgrader_spec_nofarm", "obj_upgrader_spec_nvision")),
    ("skybluetech:group.workstation_tools", "itemGroup.skybluetech.workstation_tools", _ids(
        "wrench_iron", "wrench_invar", "wrench_skyblue", "pincer_iron", "pincer_invar", "pincer_skyblue")),
    ("skybluetech:group.control_circuits", "itemGroup.skybluetech.control_circuits", _ids(
        "control_circuit_basic", "control_circuit_advanced", "control_circuit_professional")),
    ("skybluetech:group.debuggers", "itemGroup.skybluetech.debuggers", _ids(
        "simple_block_debugger", "simple_blocknbt_debugger", "simple_machine_checker")),
    ("skybluetech:group.cartidges", "itemGroup.skybluetech.cartidges", _ids(
        "famicom_cartidge_1", "famicom_cartidge_2", "famicom_cartidge_3", "famicom_cartidge_4", "famicom_cartidge_5")),
    ("skybluetech:group.brine_evaporation_pond", "itemGroup.skybluetech.brine_evaporation_pond", _ids(
        "brine_evaporation_pond_controller", "brine_evaporation_pond_io_fluid1", "brine_evaporation_pond_io_fluid2",
        "brine_evaporation_pond_io_heat")),
    ("skybluetech:group.fermenter", "itemGroup.skybluetech.fermenter", _ids(
        "fermenter_controller", "fermenter_io_energy", "fermenter_io_fluid1", "fermenter_io_fluid2", "fermenter_io_item1",
        "fermenter_io_gas")),
    ("skybluetech:group.battery_matrix", "itemGroup.skybluetech.battery_matrix", _ids(
        "battery_matrix_controller", "battery_matrix_frame", "battery_matrix_core", "battery_matrix_io_energy1",
        "battery_matrix_io_energy2")),
    ("skybluetech:group.bedrock_lava_drill", "itemGroup.skybluetech.bedrock_lava_drill", _ids(
        "bedrock_lava_drill_controller", "bedrock_lava_drill_frame", "bedrock_lava_drill_io_energy",
        "bedrock_lava_drill_io_fluid")),
    ("skybluetech:group.vacuum_freezer", "itemGroup.skybluetech.vacuum_freezer", _ids(
        "vacuum_freezer_controller", "vacuum_freezer_frame", "vacuum_freezer_condenser", "vacuum_freezer_io_fluid1",
        "vacuum_freezer_io_fluid2", "vacuum_freezer_io_energy", "vacuum_freezer_io_item1", "vacuum_freezer_io_item2")),
)
""" (组的键, .lang 的键, (物品 id, ...))：蔚蓝自己的组，照创造栏的分组与顺序 """


class Mounted(object):
    """ Mount 记下的：共享组里加了哪几样（自己建的还是别人的组）、自己建的 OWN 组，Unmount 照它撤 """

    __slots__ = ("Shared", "Own")

    def __init__(self):
        self.Shared = []  # type: list  # [(组的键, 是不是自己建的, [加进去的物品 id])]
        self.Own = []  # type: list  # 自己建的 OWN 组的键


def Mount(ctx):  # type: (any) -> Mounted or None
    """ 登记分组：SHARED 组在就加、不在就建，OWN 自己建（同一个键别人先建了就不动）；物品表里没有的 id 不加 """
    organizer = getattr(ctx.Registry, "ItemOrganizer", None)
    if organizer is None:
        return None
    lookup = ctx.Registry.ItemManager.LookUpItem
    record = Mounted()
    for key, name_key, ids in SHARED:
        known = [item_id for item_id in ids if lookup(item_id)]
        if not known:
            continue
        created = organizer.AddGroup(key, name=name_key)
        present = organizer.GetGroupItems(key)
        added = [item_id for item_id in known if item_id not in present]  # 别人已经放进来的不归我们撤
        organizer.AddGroupItemFromList(key, added)
        record.Shared.append((key, created, added))
    for key, name_key, ids in OWN:
        known = [item_id for item_id in ids if lookup(item_id)]
        if not known or not organizer.AddGroup(key, name=name_key):
            continue
        organizer.AddGroupItemFromList(key, known)
        record.Own.append(key)
    joined = sum(len(added) for key, created, added in record.Shared if not created)
    ctx.Log.info("物品分组: 蔚蓝自己的 {} 组, 和原版一起的 {} 组（往原版的组里加了 {} 样）".format(
        len(record.Own), len(record.Shared), joined))
    return record


def Unmount(ctx, record):  # type: (any, Mounted or None) -> None
    """
    撤掉 Mount 登记的：共享组只撤自己加的那几样（MEI 的 RemoveGroupItem），自己建的共享组空了再撤组 ——
    别的模组也并进来的话不能整个撤；OWN 组整个撤。MEI 太老没有 RemoveGroupItem 时：自己建的共享组整个撤，
    别人的组里加的留着（原版扩展卸载时会撤掉它自己的组）
    """
    if record is None:
        return
    organizer = getattr(ctx.Registry, "ItemOrganizer", None)
    if organizer is None:
        return
    remove_item = getattr(organizer, "RemoveGroupItem", None)
    for key, created, added in record.Shared:
        if remove_item is None:
            if created:
                organizer.RemoveGroup(key)
            continue
        for item_id in added:
            try:
                remove_item(key, item_id)
            except Exception as e:  # noqa  撤不掉一样不影响别的
                ctx.Log.warn("从组 {} 撤 {} 失败: {}".format(key, item_id, bridge.ErrorText(e)))
        if created and not organizer.GetGroupItems(key):
            organizer.RemoveGroup(key)
    for key in record.Own:
        organizer.RemoveGroup(key)
    record.Shared = []
    record.Own = []
