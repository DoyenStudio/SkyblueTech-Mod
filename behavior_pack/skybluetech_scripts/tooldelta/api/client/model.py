# coding=utf-8
from mod.client.extraClientApi import GetEngineCompFactory
from ...internal import ClientComp, ClientLevelId, inClientEnv


class FreeModel(object):
    def __init__(self, model_name):
        # type: (str) -> None
        if not inClientEnv():
            raise RuntimeError("Not in client")
        self.model_comp = GetEngineCompFactory().CreateModel(ClientLevelId)
        self.model_id = self.model_comp.CreateFreeModel(model_name)
        if self.model_id == 0:
            print("[ERROR] model invalid: " + model_name)

    def SetPos(self, x, y, z):
        # type: (float, float, float) -> bool
        return self.model_comp.SetFreeModelPos(self.model_id, x, y, z)

    def SetTexture(self, texture_name):
        # type: (str) -> bool
        return self.model_comp.SetTexture(texture_name, self.model_id)

    def SetScale(self, x, y, z):
        # type: (float, float, float) -> bool
        return self.model_comp.SetFreeModelScale(self.model_id, x, y, z)

    def Destroy(self):
        return self.model_comp.RemoveFreeModel(self.model_id)


def CreateFreeModel(model_name):
    # type: (str) -> FreeModel
    return FreeModel(model_name)


