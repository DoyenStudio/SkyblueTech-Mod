# coding=utf-8
from mod.client.extraClientApi import GetBookManager
from skybluetech_scripts.tooldelta.general import ClientInitCallback


BookMgr = GetBookManager()
BaseComp = BookMgr.GetBaseCompCls()
BasePage = BookMgr.GetBasePageCls()
TextComp = BookMgr.GetTextCompCls()
ImageComp = BookMgr.GetImageCompCls()
BookConfig = BookMgr.GetBookConfig()

registered_pages = []


def RegisterPage(
    page_name,  # type: str
):
    def wrapper(cls):
        registered_pages.append((page_name, cls))
        return cls

    return wrapper


@ClientInitCallback()
def onClientInit():
    for page_name, cls in registered_pages:
        BookMgr.AddPageType(page_name, cls)
