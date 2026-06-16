# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import CheckRecipe
from ...define import (
    TextPage,
    TOCPage,
    TOCPageSection,
    PageGroup,
)

pipes_description = PageGroup(
    "pipes_description",
    [
        TextPage(
            "青铜流体管道",
            '最常见的流体管道， 没有任何特殊功能。\n\n可以用于输送大部分常见流体， 无法输送低温或者高温流体。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.Pipe.BRONZE)},
        ),
        TextPage(
            "白铜流体管道",
            '对比普通的流体管道， 白铜流体管道支持<text color="§c" t="熔岩">的运送。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.Pipe.CUPRONICKEL)},
        ),
        TextPage(
            "耐热流体管道",
            '在白铜管道的基础上支持了<text color="§c" t="深层熔岩、 轻、 中、 重熔岩">的运送。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.Pipe.ULTRAHEATINUM)},
        ),
        TextPage(
            "耐酸流体管道",
            '不易被酸腐蚀的管道， 可以运输液酸或其它酸性流体。\n\n<style color="§6"><link id="a" text="查看配方">',
            hyperlink_cbs={"a": lambda _: CheckRecipe(id_enum.Pipe.ACIDPROOF)},
        ),
    ],
)

pipe_entry = PageGroup(
    "pipe_entry",
    [
        TextPage(
            "流体管道",
            '一般的流体管道能安全输送所有常温无害的液体或气体， 当你需要输送一些特殊流体例如<text color="§9" t="低温">、 <text color="§c" t="高温">流体， 则需要拥有特殊功能的管道， 如<text color="§d" t="耐寒或耐热流体管道">。 流体管道无法输送不符合要求的流体， 一旦强制输送则很可能导致管道破裂、 流体外泄造成污染。',
        ),
        TOCPage([
            TOCPageSection(
                id_enum.Pipe.BRONZE, 0, "青铜流体管道", pipes_description, 0
            ),
            TOCPageSection(
                id_enum.Pipe.CUPRONICKEL, 0, "白铜流体管道", pipes_description, 1
            ),
            TOCPageSection(
                id_enum.Pipe.ULTRAHEATINUM, 0, "耐热流体管道", pipes_description, 2
            ),
            TOCPageSection(
                id_enum.Pipe.ACIDPROOF, 0, "耐酸流体管道", pipes_description, 3
            ),
        ]),
    ],
)
