# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomC2SEvent, CustomS2CEvent


class PressAction(CustomC2SEvent):
    name = "st:press_action"

    def __init__(self, session, action, index=-1, serial=0, player_id=""):
        self.session = session
        self.action = action
        self.index = index
        self.serial = serial
        self.player_id = player_id

    def marshal(self):
        return dict(session=self.session, action=self.action, index=self.index, serial=self.serial)

    @classmethod
    def unmarshal(cls, args):
        return cls(args.get("session"), args.get("action"), args.get("index"),
                   args.get("serial"), args["__id__"])


class PressState(CustomS2CEvent):
    name = "st:press_state"

    def __init__(self, session, grid=None, closed=False, message="", started=0):
        self.session = session
        self.grid = grid
        self.closed = closed
        self.message = message
        self.started = started

    def marshal(self):
        return dict(session=self.session, grid=self.grid, closed=self.closed, message=self.message, started=self.started)

    @classmethod
    def unmarshal(cls, args):
        return cls(args["session"], args["grid"], args["closed"], args["message"], args.get("started", 0))
