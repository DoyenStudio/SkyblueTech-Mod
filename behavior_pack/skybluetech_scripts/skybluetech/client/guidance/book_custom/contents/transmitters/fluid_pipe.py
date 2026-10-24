# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

fluid_pipes_description = PageGroup(
    "fluid_pipes_description",
    [
        TextPage(
            "青铜流体管道",
            '最常见的流体管道， 没有任何特殊功能。\n\n可以用于输送大部分常见流体， 无法输送低温或者高温流体。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.FluidPipe.BRONZE)},
        ),
        TextPage(
            "白铜流体管道",
            '对比普通的流体管道， 白铜流体管道支持<text color="§c" t="熔岩">的运送。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.FluidPipe.CUPRONICKEL)},
        ),
        TextPage(
            "耐热流体管道",
            '在白铜管道的基础上支持了<text color="§c" t="深层熔岩、 轻、 中、 重熔岩">的运送。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.FluidPipe.ULTRAHEATINUM)},
        ),
        TextPage(
            "耐酸流体管道",
            '不易被酸腐蚀的管道， 可以运输液酸或其它酸性流体。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.FluidPipe.ACIDPROOF)},
        ),
        TextPage(
            "化学品管道",
            "传输速率和容量与耐酸流体管道相同， 可以运输常规流体、 酸性流体和碱性流体。",
        ),
    ],
)

fluid_pipe_entry = PageGroup(
    "fluid_pipe_entry",
    [
        TextPage(
            "流体管道",
            '一般的流体管道能安全输送所有常温无害的液体或气体， 当你需要输送一些特殊流体例如<text color="§9" t="低温">、 <text color="§c" t="高温">流体， 则需要拥有特殊功能的管道， 如<text color="§d" t="耐寒或耐热流体管道">。 流体管道无法输送不符合要求的流体， 一旦强制输送则很可能导致管道破裂、 流体外泄造成污染。',
        ),
        TOCPage([
            TOCPageSection(
                id_enum.FluidPipe.BRONZE, 0, "青铜流体管道", fluid_pipes_description, 0
            ),
            TOCPageSection(
                id_enum.FluidPipe.CUPRONICKEL, 0, "白铜流体管道", fluid_pipes_description, 1
            ),
            TOCPageSection(
                id_enum.FluidPipe.ULTRAHEATINUM, 0, "耐热流体管道", fluid_pipes_description, 2
            ),
            TOCPageSection(
                id_enum.FluidPipe.ACIDPROOF, 0, "耐酸流体管道", fluid_pipes_description, 3
            ),
            TOCPageSection(
                id_enum.FluidPipe.CHEMICAL, 0, "化学品管道", fluid_pipes_description, 4
            ),
        ]),
    ],
)
