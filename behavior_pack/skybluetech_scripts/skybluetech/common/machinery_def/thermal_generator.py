# coding=utf-8

STORE_RF_MAX = 14400
TICK_POWER = 50

K_BURN_SEC_LEFT = "st:burn_sec_left"
K_MAX_BURN_SEC = "st:max_burn_secs"

# copied from SiliconMod
# thanks to @MI4C
FUEL_TICK_MAP = {
    # 高燃值
    "minecraft:lava_bucket": 20000,  # 熔岩桶
    "minecraft:coal_block": 16000,  # 煤炭块
    "minecraft:dried_kelp_block": 4001,  # 干海带块
    "minecraft:blaze_rod": 2400,  # 烈焰棒
    "minecraft:coal": 1600,  # 煤炭
    "minecraft:charcoal": 1600,  # 木炭
    # 木船
    "minecraft:oak_boat": 1200,  # 橡木船
    "minecraft:spruce_boat": 1200,  # 云杉木船
    "minecraft:birch_boat": 1200,  # 白桦木船
    "minecraft:jungle_boat": 1200,  # 丛林木船
    "minecraft:acacia_boat": 1200,  # 金合欢木船
    "minecraft:dark_oak_boat": 1200,  # 深色橡木船
    "minecraft:mangrove_boat": 1200,  # 红树木船
    "minecraft:cherry_boat": 1200,  # 樱花木船
    "minecraft:pale_oak_boat": 1200,  # 苍白橡木船
    "minecraft:bamboo_raft": 1200,  # 竹筏
    # 木运输船
    "minecraft:oak_chest_boat": 1200,  # 橡木运输船
    "minecraft:spruce_chest_boat": 1200,  # 云杉木运输船
    "minecraft:birch_chest_boat": 1200,  # 白桦木运输船
    "minecraft:jungle_chest_boat": 1200,  # 丛林木运输船
    "minecraft:acacia_chest_boat": 1200,  # 金合欢木运输船
    "minecraft:dark_oak_chest_boat": 1200,  # 深色橡木运输船
    "minecraft:mangrove_chest_boat": 1200,  # 红树木运输船
    "minecraft:cherry_chest_boat": 1200,  # 樱花木运输船
    "minecraft:pale_oak_chest_boat": 1200,  # 苍白橡木运输船
    "minecraft:bamboo_chest_raft": 1200,  # 运输竹筏
    # 悬挂式木告示牌
    "minecraft:oak_hanging_sign": 800,  # 悬挂式橡木告示牌
    "minecraft:spruce_hanging_sign": 800,  # 悬挂式云杉木告示牌
    "minecraft:birch_hanging_sign": 800,  # 悬挂式白桦木告示牌
    "minecraft:jungle_hanging_sign": 800,  # 悬挂式丛林木告示牌
    "minecraft:acacia_hanging_sign": 800,  # 悬挂式金合欢木告示牌
    "minecraft:dark_oak_hanging_sign": 800,  # 悬挂式深色橡木告示牌
    "minecraft:mangrove_hanging_sign": 800,  # 悬挂式红树木告示牌
    "minecraft:cherry_hanging_sign": 800,  # 悬挂式樱花木告示牌
    "minecraft:pale_oak_hanging_sign": 800,  # 悬挂式苍白橡木告示牌
    "minecraft:bamboo_hanging_sign": 800,  # 悬挂式竹告示牌
    # 原木
    "minecraft:oak_log": 300,  # 橡木原木
    "minecraft:spruce_log": 300,  # 云杉原木
    "minecraft:birch_log": 300,  # 白桦原木
    "minecraft:jungle_log": 300,  # 丛林原木
    "minecraft:acacia_log": 300,  # 金合欢原木
    "minecraft:dark_oak_log": 300,  # 深色橡木原木
    "minecraft:mangrove_log": 300,  # 红树原木
    "minecraft:cherry_log": 300,  # 樱花原木
    "minecraft:pale_oak_log": 300,  # 苍白橡木原木
    "minecraft:bamboo_block": 300,  # 竹块
    # 去皮原木
    "minecraft:stripped_oak_log": 300,  # 去皮橡木原木
    "minecraft:stripped_spruce_log": 300,  # 去皮云杉原木
    "minecraft:stripped_birch_log": 300,  # 去皮白桦原木
    "minecraft:stripped_jungle_log": 300,  # 去皮丛林原木
    "minecraft:stripped_acacia_log": 300,  # 去皮金合欢原木
    "minecraft:stripped_dark_oak_log": 300,  # 去皮深色橡木原木
    "minecraft:stripped_mangrove_log": 300,  # 去皮红树原木
    "minecraft:stripped_cherry_log": 300,  # 去皮樱花原木
    "minecraft:stripped_pale_oak_log": 300,  # 去皮苍白橡木原木
    "minecraft:stripped_bamboo_block": 300,  # 去皮竹块
    # 木头
    "minecraft:oak_wood": 300,  # 橡木
    "minecraft:spruce_wood": 300,  # 云杉木
    "minecraft:birch_wood": 300,  # 白桦木
    "minecraft:jungle_wood": 300,  # 丛林木
    "minecraft:acacia_wood": 300,  # 金合欢木
    "minecraft:dark_oak_wood": 300,  # 深色橡木
    "minecraft:mangrove_wood": 300,  # 红树木
    "minecraft:cherry_wood": 300,  # 樱花木
    "minecraft:pale_oak_wood": 300,  # 苍白橡木
    # 去皮木头
    "minecraft:stripped_oak_wood": 300,  # 去皮橡木
    "minecraft:stripped_spruce_wood": 300,  # 去皮云杉木
    "minecraft:stripped_birch_wood": 300,  # 去皮白桦木
    "minecraft:stripped_jungle_wood": 300,  # 去皮丛林木
    "minecraft:stripped_acacia_wood": 300,  # 去皮金合欢木
    "minecraft:stripped_dark_oak_wood": 300,  # 去皮深色橡木
    "minecraft:stripped_mangrove_wood": 300,  # 去皮红树木
    "minecraft:stripped_cherry_wood": 300,  # 去皮樱花木
    "minecraft:stripped_pale_oak_wood": 300,  # 去皮苍白橡木
    # 木板
    "minecraft:oak_planks": 300,  # 橡木木板
    "minecraft:spruce_planks": 300,  # 云杉木板
    "minecraft:birch_planks": 300,  # 白桦木板
    "minecraft:jungle_planks": 300,  # 丛林木板
    "minecraft:acacia_planks": 300,  # 金合欢木板
    "minecraft:dark_oak_planks": 300,  # 深色橡木木板
    "minecraft:mangrove_planks": 300,  # 红树木板
    "minecraft:cherry_planks": 300,  # 樱花木板
    "minecraft:pale_oak_planks": 300,  # 苍白橡木木板
    "minecraft:bamboo_planks": 300,  # 竹板
    "minecraft:bamboo_mosaic": 300,  # 竹马赛克
    # 木压力板
    "minecraft:wooden_pressure_plate": 300,  # 橡木压力板
    "minecraft:spruce_pressure_plate": 300,  # 云杉木压力板
    "minecraft:birch_pressure_plate": 300,  # 白桦木压力板
    "minecraft:jungle_pressure_plate": 300,  # 丛林木压力板
    "minecraft:acacia_pressure_plate": 300,  # 金合欢木压力板
    "minecraft:dark_oak_pressure_plate": 300,  # 深色橡木压力板
    "minecraft:mangrove_pressure_plate": 300,  # 红树木压力板
    "minecraft:cherry_pressure_plate": 300,  # 樱花木压力板
    "minecraft:pale_oak_pressure_plate": 300,  # 苍白橡木压力板
    "minecraft:bamboo_pressure_plate": 300,  # 竹压力板
    # 木栅栏
    "minecraft:oak_fence": 300,  # 橡木栅栏
    "minecraft:spruce_fence": 300,  # 云杉木栅栏
    "minecraft:birch_fence": 300,  # 白桦木栅栏
    "minecraft:jungle_fence": 300,  # 丛林木栅栏
    "minecraft:acacia_fence": 300,  # 金合欢木栅栏
    "minecraft:dark_oak_fence": 300,  # 深色橡木栅栏
    "minecraft:mangrove_fence": 300,  # 红树木栅栏
    "minecraft:cherry_fence": 300,  # 樱花木栅栏
    "minecraft:pale_oak_fence": 300,  # 苍白橡木栅栏
    "minecraft:bamboo_fence": 300,  # 竹栅栏
    # 木栅栏门
    "minecraft:fence_gate": 300,  # 橡木栅栏门
    "minecraft:spruce_fence_gate": 300,  # 云杉木栅栏门
    "minecraft:birch_fence_gate": 300,  # 白桦木栅栏门
    "minecraft:jungle_fence_gate": 300,  # 丛林木栅栏门
    "minecraft:acacia_fence_gate": 300,  # 金合欢木栅栏门
    "minecraft:dark_oak_fence_gate": 300,  # 深色橡木栅栏门
    "minecraft:mangrove_fence_gate": 300,  # 红树木栅栏门
    "minecraft:cherry_fence_gate": 300,  # 樱花木栅栏门
    "minecraft:pale_oak_fence_gate": 300,  # 苍白橡木栅栏门
    "minecraft:bamboo_fence_gate": 300,  # 竹栅栏门
    # 木楼梯
    "minecraft:oak_stairs": 300,  # 橡木楼梯
    "minecraft:spruce_stairs": 300,  # 云杉木楼梯
    "minecraft:birch_stairs": 300,  # 白桦木楼梯
    "minecraft:jungle_stairs": 300,  # 丛林木楼梯
    "minecraft:acacia_stairs": 300,  # 金合欢木楼梯
    "minecraft:dark_oak_stairs": 300,  # 深色橡木楼梯
    "minecraft:mangrove_stairs": 300,  # 红树木楼梯
    "minecraft:cherry_stairs": 300,  # 樱花木楼梯
    "minecraft:pale_oak_stairs": 300,  # 苍白橡木楼梯
    "minecraft:bamboo_stairs": 300,  # 竹楼梯
    "minecraft:bamboo_mosaic_stairs": 300,  # 竹马赛克楼梯
    # 木活板门
    "minecraft:trapdoor": 300,  # 橡木活板门
    "minecraft:spruce_trapdoor": 300,  # 云杉木活板门
    "minecraft:birch_trapdoor": 300,  # 白桦木活板门
    "minecraft:jungle_trapdoor": 300,  # 丛林木活板门
    "minecraft:acacia_trapdoor": 300,  # 金合欢木活板门
    "minecraft:dark_oak_trapdoor": 300,  # 深色橡木活板门
    "minecraft:mangrove_trapdoor": 300,  # 红树木活板门
    "minecraft:cherry_trapdoor": 300,  # 樱花木活板门
    "minecraft:pale_oak_trapdoor": 300,  # 苍白橡木活板门
    "minecraft:bamboo_trapdoor": 300,  # 竹活板门
    # 木台阶
    "minecraft:oak_slab": 300,  # 橡木台阶
    "minecraft:spruce_slab": 300,  # 云杉木台阶
    "minecraft:birch_slab": 300,  # 白桦木台阶
    "minecraft:jungle_slab": 300,  # 丛林木台阶
    "minecraft:acacia_slab": 300,  # 金合欢木台阶
    "minecraft:dark_oak_slab": 300,  # 深色橡木台阶
    "minecraft:mangrove_slab": 300,  # 红树木台阶
    "minecraft:cherry_slab": 300,  # 樱花木台阶
    "minecraft:pale_oak_slab": 300,  # 苍白橡木台阶
    "minecraft:bamboo_slab": 300,  # 竹台阶
    "minecraft:bamboo_mosaic_slab": 300,  # 竹马赛克台阶
    # 木按钮
    "minecraft:wooden_button": 300,  # 橡木按钮
    "minecraft:spruce_button": 300,  # 云杉木按钮
    "minecraft:birch_button": 300,  # 白桦木按钮
    "minecraft:jungle_button": 300,  # 丛林木按钮
    "minecraft:acacia_button": 300,  # 金合欢木按钮
    "minecraft:dark_oak_button": 300,  # 深色橡木按钮
    "minecraft:mangrove_button": 300,  # 红树木按钮
    "minecraft:cherry_button": 300,  # 樱花木按钮
    "minecraft:pale_oak_button": 300,  # 苍白橡木按钮
    "minecraft:bamboo_button": 300,  # 竹按钮
    # 木质方块
    "minecraft:bee_nest": 300,  # 蜂巢
    "minecraft:crafting_table": 300,  # 工作台
    "minecraft:cartography_table": 300,  # 制图台
    "minecraft:fletching_table": 300,  # 制箭台
    "minecraft:smithing_table": 300,  # 锻造台
    "minecraft:beehive": 300,  # 蜂箱
    "minecraft:loom": 300,  # 织布机
    "minecraft:bookshelf": 300,  # 书架
    "minecraft:chiseled_bookshelf": 300,  # 雕纹书架
    "minecraft:lectern": 300,  # 讲台
    "minecraft:composter": 300,  # 堆肥桶
    "minecraft:chest": 300,  # 箱子
    "minecraft:trapped_chest": 300,  # 陷阱箱
    "minecraft:barrel": 300,  # 木桶
    "minecraft:noteblock": 300,  # 音符盒
    "minecraft:jukebox": 300,  # 唱片机
    "minecraft:daylight_detector": 300,  # 阳光探测器
    "minecraft:banner": 300,  # 旗帜
    "minecraft:ladder": 300,  # 梯子
    # 木告示牌
    "minecraft:oak_sign": 200,  # 橡木告示牌
    "minecraft:spruce_sign": 200,  # 云杉木告示牌
    "minecraft:birch_sign": 200,  # 白桦木告示牌
    "minecraft:jungle_sign": 200,  # 丛林木告示牌
    "minecraft:acacia_sign": 200,  # 金合欢木告示牌
    "minecraft:dark_oak_sign": 200,  # 深色橡木告示牌
    "minecraft:mangrove_sign": 200,  # 红树木告示牌
    "minecraft:cherry_sign": 200,  # 樱花木告示牌
    "minecraft:pale_oak_sign": 200,  # 苍白橡木按钮
    "minecraft:bamboo_sign": 200,  # 竹告示牌
    # 木门
    "minecraft:wooden_door": 200,  # 橡木门
    "minecraft:spruce_door": 200,  # 云杉木门
    "minecraft:birch_door": 200,  # 白桦木门
    "minecraft:jungle_door": 200,  # 丛林木门
    "minecraft:acacia_door": 200,  # 金合欢木门
    "minecraft:dark_oak_door": 200,  # 深色橡木门
    "minecraft:mangrove_door": 200,  # 红树木门
    "minecraft:cherry_door": 200,  # 樱花木门
    "minecraft:pale_oak_door": 200,  # 苍白橡木门
    "minecraft:bamboo_door": 200,  # 竹门
    # 树苗
    "minecraft:oak_sapling": 100,  # 树苗
    "minecraft:spruce_sapling": 100,  # 树苗
    "minecraft:birch_sapling": 100,  # 树苗
    "minecraft:jungle_sapling": 100,  # 树苗
    "minecraft:acacia_sapling": 100,  # 树苗
    "minecraft:dark_oak_sapling": 100,  # 树苗
    "minecraft:mangrove_propagule": 100,  # 红树胎生苗
    "minecraft:cherry_sapling": 100,  # 樱花树苗
    "minecraft:pale_oak_sapling": 100,  # 苍白橡树树苗
    "minecraft:azalea": 100,  # 杜鹃花丛
    "minecraft:flowering_azalea": 100,  # 盛开的杜鹃花丛
    # 其它低燃值方块
    "minecraft:mangrove_roots": 300,  # 红树根
    "minecraft:deadbush": 100,  # 枯萎的灌木
    "minecraft:scaffolding": 50,  # 脚手架
    "minecraft:leaf_litter": 50,  # 枯叶
    "minecraft:short_dry_grass": 50,  # 矮枯草丛
    "minecraft:tall_dry_grass": 50,  # 高枯草丛
    "minecraft:fishing_rod": 300,  # 钓鱼竿
    "minecraft:bowl": 200,  # 碗
    "minecraft:bow": 200,  # 弓
    "minecraft:crossbow": 200,  # 弩
    "minecraft:wooden_pickaxe": 200,  # 木镐
    "minecraft:wooden_shovel": 200,  # 木锹
    "minecraft:wooden_hoe": 200,  # 木锄
    "minecraft:wooden_axe": 200,  # 木斧
    "minecraft:wooden_sword": 200,  # 木剑
    "minecraft:stick": 100,  # 木棍
    "minecraft:bamboo": 50,  # 竹子
    # 自定义燃料
    "skybluetech:sawdust": 150,  # 锯末，木板燃烧时长的一半
}

FUEL_SECONDS_MAP = {k: v / 20.0 for k, v in FUEL_TICK_MAP.items()}
