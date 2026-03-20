# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import CustomS2CEvent


class ChapterUnlockEvent(CustomS2CEvent):
    name = "st:ChapterUnlockEvent"

    def __init__(self, chapter_id):
        # type: (str) -> None
        self.chapter_id = chapter_id

    def marshal(self):
        return {"chapter_id": self.chapter_id}

    @classmethod
    def unmarshal(cls, data):
        return cls(data["chapter_id"])
