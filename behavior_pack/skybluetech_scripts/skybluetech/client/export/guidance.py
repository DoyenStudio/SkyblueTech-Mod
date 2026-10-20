# coding=utf-8
from mod_log import logger

from ..guidance.book_custom import define as pages_define

"""
使用: `ImportModule("skybluetech_scripts.skybluetech.client.export.guidance")`
"""


class AdditionData:
    has_addition = False


def AddAddition(entry):
    # type: (pages_define.MainTOCPageSection) -> None
    if not AdditionData.has_addition:
        page = pages_define.MainTOCPage.GetByIdentifier("skybluetech_guidance_main_toc")
        if page is None:
            logger.error("[SkyblueTech] skybluetech_guidance_main_toc page not found")
            return
        page.AddSection(
            pages_define.MainTOCPageSection(
                "minecraft:bundle", 0, "附属模组", additions_toc
            )
        )
        group = page.GetGroup()
        if group is None:
            return
        additions_toc.SetParent(group)
        AdditionData.has_addition = True
    addition_sections.AddSection(entry)
    addition_sections.SetGroup(additions_toc)


addition_sections = pages_define.MainTOCPage([], "addition_sections")

additions_toc = pages_define.PageGroup(
    "additions_toc",
    [
        pages_define.TextPage(
            "附属模组列表", "在本页面查看《蔚蓝科技》所有附属的教程。"
        ),
        addition_sections,
    ],
)

__all__ = ["AddAddition", "pages_define"]
