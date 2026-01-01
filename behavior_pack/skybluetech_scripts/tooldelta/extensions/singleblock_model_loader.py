# coding=utf-8
from ..api.client import (
    CombineBlockPaletteToGeometry,
    NewSingleBlockPalette,
    CreateClientEntity,
    DestroyClientEntity,
    AddActorBlockGeometry,
    DeleteActorBlockGeometry,
)

class GeometryModel(object):
    def __init__(self, entity_id):
        # type: (str) -> None
        self.entity_id = entity_id
        self.geo_id = None

    def SetBlockModel(self, block_name, aux):
        # type: (str, int) -> bool
        if self.geo_id is not None:
            res = self.RemoveGeometry()
            if not res:
                print ("[Warning] last geometry remove failed")
        pal = NewSingleBlockPalette(block_name, aux)
        self.geo_id = block_name + ":" + str(aux)
        self.geo_id = CombineBlockPaletteToGeometry(pal, self.geo_id)
        if self.geo_id is None:
            raise Exception("Failed to create geometry: " + self.geo_id)
        return AddActorBlockGeometry(self.entity_id, self.geo_id)

    def RemoveGeometry(self):
        if self.geo_id is not None:
            geo_id = self.geo_id
            self.geo_id = None
            return DeleteActorBlockGeometry(self.entity_id, geo_id)
        else:
            print ("[Warning] No geometry to remove")
            return False

    def Destroy(self):
        DestroyClientEntity(self.entity_id)


def CreateSingleBlockModelEntity(pos, block_name, aux=0, entity_name="skybluetech:model_entity"):
    # type: (tuple[float, float, float], str, int, str) -> tuple[GeometryModel, bool]
    entity_id = CreateClientEntity(entity_name, pos, (0, 0))
    if entity_id is None:
        raise Exception("Failed to create entity: " + entity_name)
    model = GeometryModel(entity_id)
    return model, model.SetBlockModel(block_name, aux)

def CreateBlankSingleBlockModelEntity(pos, entity_name="skybluetech:model_entity"):
    # type: (tuple[float, float, float], str) -> GeometryModel
    x, y, z = pos
    entity_id = CreateClientEntity(entity_name, (x+0.5, y, z+0.5), (0, 0))
    if entity_id is None:
        raise Exception("Failed to create entity: " + entity_name)
    model = GeometryModel(entity_id)
    return model
