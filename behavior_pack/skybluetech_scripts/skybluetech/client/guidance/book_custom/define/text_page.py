# coding=utf-8
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.tooldelta.extensions.richer_text import (
    RicherTextCtrl,
    RicherTextOpt,
)
from .base_page import BasePage

if 0:
    import typing


class TextPage(BasePage):
    ctrl_def_name = "GuidanceLib.text_page"

    def __init__(self, title, content, hyperlink_cbs=None):
        # type: (str, str, dict[str, typing.Callable[[dict], typing.Any]] | None) -> None
        BasePage.__init__(self)
        self.title = title
        self.content = content
        self.hyperlink_cbs = hyperlink_cbs or {}
        self._ticker = None

    def RenderInit(self, ctrl):
        # type: (UBaseCtrl) -> None
        BasePage.RenderInit(self, ctrl)
        ctrl["title_label"].asLabel().SetText(self.title)
        async_load = False
        if not async_load:
            RicherTextCtrl(
                ctrl["content"], opts=RicherTextOpt(hyperlink_cbs=self.hyperlink_cbs)
            ).SetText(self.content)
        else:
            async_executor = RicherTextCtrl(
                ctrl["content"], opts=RicherTextOpt(hyperlink_cbs=self.hyperlink_cbs)
            ).SetTextAsync(self.content)

            def run_async():
                if run_async.finished:
                    return
                try:
                    next(async_executor)
                except StopIteration:
                    run_async.finished = True

            run_async.finished = False
            self._ticker = run_async

    def ScreenTicking(self):
        if self._ticker is not None:
            self._ticker()
