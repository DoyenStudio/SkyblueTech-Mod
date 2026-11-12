# coding=utf-8
from mod.client.extraClientApi import GetTopUI as top_screen
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.internal import GetClient
from skybluetech_scripts.tooldelta.general import ClientUninitCallback
from skybluetech_scripts.tooldelta.events.client import DimensionChangeClientEvent, OnScriptTickClient
from skybluetech_scripts.tooldelta.events.basic import ClientEvent
from skybluetech_scripts.tooldelta.extensions.mod_block_event import asModBlockRemovedListener
from skybluetech_scripts.tooldelta.extensions.singleblock_model_loader import CreateBlankModel
from ...common.events.machinery.blueprint import BlueprintAction, BlueprintUpdate
from ...common.utils import blueprint as bp
from ...common.define.id_enum import Machinery


class PlayerChatButtonClickClientEvent(ClientEvent):
    name = "PlayerChatButtonClickClientEvent"


def picked_block():
    hit = CF.CreateCamera(LEVEL_ID).PickFacing() or {}
    if hit.get("type") == "Block":
        return hit["x"], hit["y"], hit["z"]


def translucent(model, opacity):
    render = CF.CreateActorRender(model.entity_id)
    return (render.EnableActorBlockGeometryTransparent(model.geo_id, True)
            and render.SetActorBlockGeometryTransparency(model.geo_id, opacity))


def palette_from_cells(size, groups, states, actors):
    palette = CF.CreateBlock(LEVEL_ID).GetBlankBlockPalette()
    if palette and palette.DeserializeBlockPalette({
        "volume": (size[2], size[0], size[1]), "common": groups, "states": states,
        "extra": {}, "actor": actors, "void": False, "eliminateAir": True,
    }):
        return palette


class Preview(object):
    def __init__(self):
        self.location = self.frame = self.model = self.shape = self.signature = None
        self.origin = self.target = self.chat_target = None
        self.chat_locked = False
        self.panel = None

    def clear(self):
        if self.frame:
            GetClient().DestroyClientEntity(self.frame)
        if self.model:
            self.model.Destroy()
        self.model = self.frame = self.shape = self.signature = None
        self.origin = self.target = self.chat_target = None
        self.chat_locked = False

    def box(self, first, last):
        low, size = bp.bounds(first, last)
        if self.shape == (low, size):
            return
        center = tuple(a + b * 0.5 for a, b in zip(low, size))
        if not self.frame:
            self.frame = GetClient().CreateClientEntityByTypeStr("skybluetech:blueprint_frame", center, (0, 0))
            if not self.frame:
                return
            CF.CreateModel(self.frame).SetEntityShadowShow(False)
        else:
            CF.CreatePos(self.frame).SetPosForClientEntity(center)
        invalid = any(n > cap for n, cap in zip(size, bp.LIMIT))
        CF.CreateActorRender(self.frame).SetEntityExtraUniforms(1, tuple(n * 0.5 + 0.008 for n in size) + (float(invalid),))
        self.shape = (low, size)
        if invalid and self.origin:
            CF.CreateGame(LEVEL_ID).SetTipMessage("§c超出范围")

    def display(self, state):
        code, facing = state["code"], state["facing"]
        if self.signature == (code, facing):
            return
        self.clear()
        size, anchor, source, groups = bp.unshare(code)
        turns = (facing - source) % 4
        origin = bp.front(self.location[1:], facing)
        first = bp.world((0, 0, 0), anchor, origin, turns)
        last = bp.world(tuple(n - 1 for n in size), anchor, origin, turns)
        low, rotated_size = bp.bounds(first, last)
        self.box(first, last)
        common, states, actors = {}, {}, {}
        for (_, indices), (name, aux, block_state, color) in zip(sorted(groups.items()), state["variants"]):
            key = (name, aux)
            states[key] = block_state
            target = common.setdefault(key, [])
            for index in indices:
                pos = bp.world(bp.local(index, size), anchor, origin, turns)
                cell = bp.linear(tuple(a - b for a, b in zip(pos, low)), rotated_size)
                target.append(cell)
                if color is not None:
                    actors.setdefault(name, {})[cell] = {"color": 15 - color, "direction": block_state["direction"]}
                if name in ("minecraft:chest", "minecraft:trapped_chest", "minecraft:ender_chest"):
                    # Native palette geometry uses a block actor for the closed chest shell.
                    direction = block_state.get("minecraft:cardinal_direction", "north")
                    actors.setdefault(name, {})[cell] = {
                        "chestMainSubChest": True, "chestIsGlobalChest": False,
                        "chestModelOffset": 0.0, "chestOpenness": 0.0,
                        "chestOldOpenness": 0.0, "chestIsLargeChest": False,
                        "facingDirection": (2, 5, 3, 4)[bp.DIRECTIONS.index(direction)],
                    }
        pal = palette_from_cells(rotated_size, common, states, actors)
        if pal:
            self.model = CreateBlankModel(low)
            if self.model.SetBlockPaletteModel(pal, "geometry.skybluetech.blueprint_preview"):
                translucent(self.model, 0.5)
        self.signature = (code, facing)


preview = Preview()


@OnScriptTickClient.Listen()
def update_target(_):
    if preview.origin is None:
        return
    if "chat" in (top_screen() or "").lower():
        return
    hit = picked_block()
    preview.target = hit
    if hit:
        preview.box(preview.origin, hit)
    elif preview.frame:
        GetClient().DestroyClientEntity(preview.frame)
        preview.frame = preview.shape = None


@PlayerChatButtonClickClientEvent.Listen()
def lock_target(_):
    if preview.origin:
        preview.chat_target = preview.target
        preview.chat_locked = True


@BlueprintUpdate.Listen()
def on_update(event):
    if event.location != preview.location:
        return
    action, value = event.action, event.value
    if action == "state":
        panel = preview.panel
        if panel is not None and panel.apply_state(value):
            if value["variants"]:
                preview.display(value)
            else:
                preview.clear()
    elif action in ("capturing", "clear", "leave", "selected"):
        preview.clear()
        if action == "selected":
            # The native proxy normally gets its location from the last block use.
            from ..ui.machinery.define import _RUNTIME
            _RUNTIME.GPos = event.location
    elif action == "select" and preview.panel:
        preview.clear()
        preview.origin = bp.front(event.location[1:], value)
        preview.panel.close_for_selection()
        CF.CreateGame(LEVEL_ID).SetTipMessage("瞄准范围终点，在聊天栏输入 OK")
    elif action == "request_target":
        target = preview.chat_target if preview.chat_locked else preview.target
        preview.chat_locked = False
        x, y, z = event.location[1:]
        BlueprintAction(x, y, z, "target", target).send()


@asModBlockRemovedListener(Machinery.BLUEPRINT_TABLE)
def removed(event):
    if preview.location == (event.dimensionId, event.posX, event.posY, event.posZ):
        preview.clear()
        preview.location = None


@DimensionChangeClientEvent.Listen()
def dimension_changed(_):
    leave()


@ClientUninitCallback()
def leave():
    preview.clear()
    preview.location = preview.panel = None
