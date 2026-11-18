# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF
from skybluetech_scripts.skybluetech.common.events.machinery.fluid_output_faces import (
    FluidOutputFacesGet,
    FluidOutputFacesSet,
    FluidOutputFacesUpdate,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.fluid_output_faces import (
    ALL_OUTPUT_FACES,
    K_OUTPUT_FACE_MASK,
    K_OUTPUT_FACE_REVISION,
    OUTPUT_FACES,
)

from .operation_listener import OperationListener


class FluidOutputFaces(OperationListener):
    """可选流体输出面配置；与 Processor、MultiFluidContainer 一起继承。"""

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidOutputFaces, self).__init__(dim, x, y, z, block_entity_data)
        defaults = self.fluid_output_slots_by_face
        self._fluid_output_masks = {}
        self._fluid_output_revision = self.bdata[K_OUTPUT_FACE_REVISION] or 0
        for slot in self.fluid_output_slots:
            mask = self.bdata[K_OUTPUT_FACE_MASK + str(slot)]
            if type(mask) is not int or not 0 <= mask <= ALL_OUTPUT_FACES:
                mask = sum(
                    1 << index for index, face in enumerate(OUTPUT_FACES)
                    if defaults is None or slot in defaults.get(face, ())
                )
            self._fluid_output_masks[slot] = mask
        self._update_output_face_slots()

    def _update_output_face_slots(self):
        # 每台机器独立生成白名单；不能修改子类共享的默认映射。
        self.fluid_output_slots_by_face = {
            face: tuple(
                slot for slot in self.fluid_output_slots
                if self._fluid_output_masks[slot] & (1 << index)
            )
            for index, face in enumerate(OUTPUT_FACES)
        }

    def CanConfigureFluidOutput(self, player_id):
        if not self.ui_sync.PlayerInSync(player_id):
            return False
        pos = CF.CreatePos(player_id).GetFootPos()
        return pos is not None and sum(
            (a - b - 0.5) ** 2 for a, b in zip(pos, self.xyz)
        ) <= 64

    def SendFluidOutputFaces(self, player_id=None, status=""):
        packet = FluidOutputFacesUpdate(
            (self.dim, self.x, self.y, self.z),
            [(slot, self._fluid_output_masks[slot]) for slot in self.fluid_output_slots],
            self._fluid_output_revision,
            status,
        )
        if player_id is None:
            packet.sendMulti(self.ui_sync.GetPlayersInSync())
        else:
            packet.send(player_id)

    def SetFluidOutputFaces(self, slot, mask):
        from ... import transferlib

        if self._fluid_output_masks[slot] == mask:
            return
        self._fluid_output_masks[slot] = mask
        self.bdata[K_OUTPUT_FACE_MASK + str(slot)] = mask
        self._fluid_output_revision += 1
        self.bdata[K_OUTPUT_FACE_REVISION] = self._fluid_output_revision
        self._update_output_face_slots()
        transferlib.invalidate()
        self.SendFluidOutputFaces()


@FluidOutputFaces.ForOperation(FluidOutputFacesGet)
def on_get_output_faces(event, machine):
    if machine.CanConfigureFluidOutput(event.player_id):
        machine.SendFluidOutputFaces(event.player_id)


@FluidOutputFaces.ForOperation(FluidOutputFacesSet)
def on_set_output_faces(event, machine):
    if not machine.CanConfigureFluidOutput(event.player_id):
        return
    if (
        type(event.slot) is not int or event.slot not in machine.fluid_output_slots
        or type(event.mask) is not int or not 0 <= event.mask <= ALL_OUTPUT_FACES
        or type(event.revision) is not int
    ):
        machine.SendFluidOutputFaces(event.player_id, "invalid")
    elif event.revision != machine._fluid_output_revision:
        machine.SendFluidOutputFaces(event.player_id, "conflict")
    else:
        machine.SetFluidOutputFaces(event.slot, event.mask)
        machine.SendFluidOutputFaces(event.player_id, "saved")
