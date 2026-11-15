# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)


transmit_belts_description = PageGroup(
    "transmit_belts_description",
    [
        TextPage(
            "普通传送带",
            '普通传送带沿放置朝向输送带上的掉落物、 生物和玩家。\n\n将另一条传送带从侧面朝向普通传送带接入， 可以实现<text color="§2" t="转弯或汇流">。\n\n普通传送带本身不从容器中取货或存货， 自动装卸需要搭配取货传送带和存货传送带。\n\n<style color="§6"><link id="recipe" text="查看配方">',
            hyperlink_cbs={"recipe": lambda _: CheckRecipe(id_enum.TransmitBelt.BELT)},
        ),
        TextPage(
            "取货传送带",
            '将容器放在取货传送带<text color="§2" t="运输方向的后方">， 与取货口紧贴并保持同一高度。\n\n取货传送带会自动从容器中取出物品， 每次取出一件， 作为掉落物放到带上继续运输。\n\n<style color="§6"><link id="recipe" text="查看配方">',
            hyperlink_cbs={
                "recipe": lambda _: CheckRecipe(id_enum.TransmitBelt.EXTRACTOR)
            },
        ),
        TextPage(
            "存货传送带",
            '将容器放在存货传送带<text color="§2" t="运输方向的前方">， 与存货口紧贴并保持同一高度。\n\n运到存货口的掉落物会被自动存入容器。 如果容器已满或无法接收该物品， 物品会停在存货口等待。\n\n<style color="§6"><link id="recipe" text="查看配方">',
            hyperlink_cbs={
                "recipe": lambda _: CheckRecipe(id_enum.TransmitBelt.INSERTER)
            },
        ),
        TextPage(
            "感应传送带",
            '感应传送带在输送物品和生物的同时， 可以检测站在带上的生物或玩家。\n\n检测到生物或玩家时输出<text color="§c" t="15 级红石信号">， 全部离开后信号归零。 <text color="§2" t="掉落物和盔甲架不会触发感应">。\n\n<style color="§6"><link id="recipe" text="查看配方">',
            hyperlink_cbs={
                "recipe": lambda _: CheckRecipe(id_enum.TransmitBelt.DETECTOR)
            },
        ),
    ],
)


transmit_belt_entry = PageGroup(
    "transmit_belt_entry",
    [
        TextPage(
            "传送带",
            '传送带无需能量， 可以沿放置朝向输送掉落物、 生物和玩家。\n\n搭配<text color="§2" t="取货传送带">和<text color="§2" t="存货传送带">， 即可在容器之间自动运输物品。\n\n一条基础运输线路依次连接：\n源容器 → 取货传送带 → 普通传送带 → 存货传送带 → 目标容器。',
        ),
        TOCPage(
            [
                TOCPageSection(
                    id_enum.TransmitBelt.BELT,
                    0,
                    "普通传送带",
                    transmit_belts_description,
                    0,
                ),
                TOCPageSection(
                    id_enum.TransmitBelt.EXTRACTOR,
                    0,
                    "取货传送带",
                    transmit_belts_description,
                    1,
                ),
                TOCPageSection(
                    id_enum.TransmitBelt.INSERTER,
                    0,
                    "存货传送带",
                    transmit_belts_description,
                    2,
                ),
                TOCPageSection(
                    id_enum.TransmitBelt.DETECTOR,
                    0,
                    "感应传送带",
                    transmit_belts_description,
                    3,
                ),
            ],
        ),
    ],
)
